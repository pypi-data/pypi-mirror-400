import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple, Union

from coze_coding_utils.runtime_ctx.context import Context
from cozeloop.decorator import observe

from ..core.client import BaseClient
from ..core.config import Config
from ..core.exceptions import APIError
from .models import (
    ImageURLContent,
    TextContent,
    VideoConfig,
    VideoGenerationRequest,
    VideoGenerationTask,
)

logger = logging.getLogger(__name__)


class VideoGenerationClient(BaseClient):
    def __init__(
        self,
        config: Optional[Config] = None,
        ctx: Optional[Context] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        verbose: bool = False,
    ):
        super().__init__(config, ctx, custom_headers, verbose)
        self.base_url = self.config.base_url

    def _create_task(
        self,
        model: str,
        content: List[Union[TextContent, ImageURLContent]],
        config: Optional[VideoConfig] = None,
    ) -> str:
        request = VideoGenerationRequest(
            model=model, content=content, config=config or VideoConfig()
        )

        response = self._request(
            method="POST",
            url=f"{self.base_url}/api/v3/contents/generations/tasks",
            json=request.model_dump(exclude_none=True),
        )

        return response.get("id")

    def _get_task_status(self, task_id: str) -> VideoGenerationTask:
        response = self._request(
            method="GET",
            url=f"{self.base_url}/api/v3/contents/generations/tasks/{task_id}",
        )

        return VideoGenerationTask(**response)

    @observe(name="video_generation")
    def video_generation(
        self,
        content_items: List[Union[TextContent, ImageURLContent]],
        callback_url: Optional[str] = None,
        return_last_frame: Optional[bool] = False,
        model: str = "doubao-seedance-1-0-pro-fast-251015",
        config: Optional[VideoConfig] = None,
    ) -> Tuple[Optional[str], Dict, str]:
        """
        视频生成函数（同步）。调用生视频模型，非大语言模型，仅用于生成视频

        Args:
            content_items: 输入给模型，生成视频的信息，支持文本信息和图片信息。
            callback_url: 可选，填写本次生成任务结果的回调通知地址。当视频生成任务有状态变化时，方舟将向此地址推送 POST 请求。
            return_last_frame: 可选，返回生成视频的尾帧图像。设置为 true 后，可获取视频的尾帧图像。
            model: 模型名称，默认使用 doubao-seedance-1-0-pro-fast-251015
            config: 视频配置参数

        Returns:
            Tuple[Optional[str], Dict, str]: (视频URL, 完整响应数据字典, 尾帧图像URL)
                完整响应数据示例：
                {
                  "id": "cgt-2025******-****",
                  "model": "doubao-seedance-1-0-pro-fast-251015",
                  "status": "succeeded",
                  "content": {
                    "video_url": "https://ark-content-generation-cn-beijing.tos-cn-beijing.volces.com/..."
                  },
                  "seed": 10,
                  "resolution": "720p",
                  "ratio": "16:9",
                  "duration": 5,
                  "framespersecond": 24,
                  "usage": {
                    "completion_tokens": 108900,
                    "total_tokens": 108900
                  },
                  "created_at": 1743414619,
                  "updated_at": 1743414673
                }

        Raises:
            APIError: 当视频生成失败、超时或出现其他错误时
        """
        poll_interval = 5
        max_wait_time = 300

        request_data = {
            "model": model,
            "content": [item.model_dump() for item in content_items],
        }

        if callback_url:
            request_data["callback_url"] = callback_url
        if return_last_frame:
            request_data["return_last_frame"] = return_last_frame
        if config:
            request_data["config"] = config.model_dump(exclude_none=True)

        task_id = None
        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:
            try:
                response = self._request(
                    method="POST",
                    url=f"{self.base_url}/api/v3/contents/generations/tasks",
                    json=request_data,
                )

                task_id = response.get("id")
                if not task_id:
                    raise APIError("创建视频生成任务失败：响应中缺少任务ID")

                logger.info(f"视频生成任务创建成功，任务ID: {task_id}")
                break

            except APIError as e:
                retry_count += 1
                error_msg = str(e)
                logger.error(
                    f"创建视频生成任务失败（尝试 {retry_count}/{max_retries}）: {error_msg}"
                )

                if retry_count >= max_retries:
                    raise APIError(
                        f"创建视频生成任务失败，已重试{max_retries}次: {error_msg}"
                    )

                if "rate limit" in error_msg.lower() or "429" in error_msg:
                    wait_time = min(2**retry_count, 10)
                    logger.warning(f"遇到速率限制，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                elif "timeout" in error_msg.lower():
                    logger.warning(f"请求超时，等待 2 秒后重试...")
                    time.sleep(2)
                else:
                    raise

        start_time = time.time()
        poll_count = 0

        while time.time() - start_time < max_wait_time:
            poll_count += 1

            try:
                response = self._request(
                    method="GET",
                    url=f"{self.base_url}/api/v3/contents/generations/tasks/{task_id}",
                )

                status = response.get("status")
                logger.debug(f"任务 {task_id} 状态检查 #{poll_count}: {status}")

                if status == "succeeded":
                    video_url = response.get("content", {}).get("video_url")
                    last_frame_url = response.get("content", {}).get(
                        "last_frame_url", ""
                    )

                    if not video_url:
                        raise APIError(
                            f"视频生成成功但响应中缺少视频URL，任务ID: {task_id}"
                        )

                    logger.info(
                        f"视频生成成功，任务ID: {task_id}, 视频URL: {video_url}"
                    )
                    return video_url, response, last_frame_url

                elif status == "failed":
                    error_message = response.get("error_message", "未知错误")
                    logger.error(
                        f"视频生成失败，任务ID: {task_id}, 错误: {error_message}"
                    )
                    raise APIError(f"视频生成失败: {error_message}")

                elif status == "cancelled":
                    logger.warning(f"视频生成任务被取消，任务ID: {task_id}")
                    return None, response, ""

                elif status in ["queued", "running"]:
                    time.sleep(poll_interval)
                    continue

                else:
                    logger.warning(f"未知的任务状态: {status}，任务ID: {task_id}")
                    time.sleep(poll_interval)
                    continue

            except APIError as e:
                error_msg = str(e)
                logger.error(f"查询任务状态失败，任务ID: {task_id}, 错误: {error_msg}")

                if "not found" in error_msg.lower() or "404" in error_msg:
                    raise APIError(f"任务不存在或已过期，任务ID: {task_id}")

                if time.time() - start_time >= max_wait_time:
                    raise

                time.sleep(poll_interval)
                continue

        elapsed_time = int(time.time() - start_time)
        logger.error(f"视频生成超时，任务ID: {task_id}, 已等待: {elapsed_time}秒")
        raise APIError(f"视频生成超时，已等待 {elapsed_time} 秒，任务ID: {task_id}")

    async def video_generation_async(
        self,
        content_items: List[Union[TextContent, ImageURLContent]],
        callback_url: Optional[str] = None,
        return_last_frame: Optional[bool] = False,
        model: str = "doubao-seedance-1-0-pro-fast-251015",
        config: Optional[VideoConfig] = None,
    ) -> Tuple[Optional[str], Dict, str]:
        """
        视频生成函数（异步）。调用生视频模型，非大语言模型，仅用于生成视频

        适用于批量生成视频的场景，可以并发执行多个视频生成任务。

        Example:
            ```python
            import asyncio

            async def batch_generate():
                prompts = ["小猫玩球", "日落海滩", "城市夜景"]
                tasks = [
                    client.video_generation_async(
                        content_items=[TextContent(text=prompt)]
                    )
                    for prompt in prompts
                ]
                results = await asyncio.gather(*tasks)
                return results

            results = asyncio.run(batch_generate())
            ```

        Args:
            content_items: 输入给模型，生成视频的信息，支持文本信息和图片信息。
            callback_url: 可选，填写本次生成任务结果的回调通知地址。
            return_last_frame: 可选，返回生成视频的尾帧图像。
            model: 模型名称，默认使用 doubao-seedance-1-0-pro-fast-251015
            config: 视频配置参数

        Returns:
            Tuple[Optional[str], Dict, str]: (视频URL, 完整响应数据字典, 尾帧图像URL)

        Raises:
            APIError: 当视频生成失败、超时或出现其他错误时
        """
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self.video_generation,
            content_items,
            callback_url,
            return_last_frame,
            model,
            config,
        )
        return result
