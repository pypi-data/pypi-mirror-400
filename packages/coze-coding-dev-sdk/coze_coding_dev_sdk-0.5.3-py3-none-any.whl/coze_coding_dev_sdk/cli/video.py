import json
from typing import Optional

import click
from coze_coding_utils.runtime_ctx.context import new_context
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..core.config import Config
from ..core.exceptions import APIError
from ..video import (
    ImageURL,
    ImageURLContent,
    TextContent,
    VideoConfig,
    VideoGenerationClient,
)
from .constants import RUN_MODE_HEADER, RUN_MODE_TEST

console = Console()


def parse_resolution(size: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    if not size:
        return None, None

    width, height = size.split("x")
    w, h = int(width), int(height)

    if w == h:
        return "1:1", "720p" if w <= 1024 else "1080p"
    elif w > h:
        return "16:9", "720p" if w <= 1440 else "1080p"
    else:
        return "9:16", "720p" if h <= 1440 else "1080p"


@click.command()
@click.option("--prompt", "-p", help="文本提示词")
@click.option("--image-url", "-i", help="图片URL（单个或逗号分隔的两个）")
@click.option("--size", "-s", help="视频分辨率（如 1920x1080）")
@click.option("--duration", "-d", type=int, help="视频时长（5-10秒）")
@click.option("--model", "-m", help="模型名称")
@click.option("--callback-url", help="回调URL")
@click.option("--return-last-frame", is_flag=True, help="返回尾帧图像")
@click.option("--watermark", is_flag=True, default=False, help="添加水印")
@click.option("--seed", type=int, help="随机种子")
@click.option("--camerafixed", is_flag=True, help="固定摄像头")
@click.option("--output", "-o", type=click.Path(), help="输出文件路径（JSON）")
@click.option("--mock", is_flag=True, help="使用 mock 模式（测试运行）")
@click.option(
    "--header",
    "-H",
    multiple=True,
    help="自定义 HTTP 请求头 (格式: 'Key: Value' 或 'Key=Value'，可多次使用)",
)
@click.option("--verbose", "-v", is_flag=True, help="显示详细的 HTTP 请求日志")
def video(
    prompt: Optional[str],
    image_url: Optional[str],
    size: Optional[str],
    duration: Optional[int],
    model: Optional[str],
    callback_url: Optional[str],
    return_last_frame: bool,
    watermark: bool,
    seed: Optional[int],
    camerafixed: bool,
    output: Optional[str],
    mock: bool,
    header: tuple,
    verbose: bool,
):
    """同步生成视频（等待完成）"""
    try:
        from .utils import parse_headers

        config = Config()

        ctx = None
        custom_headers = parse_headers(header) or {}

        if mock:
            ctx = new_context(method="video.generate", headers=custom_headers)
            custom_headers[RUN_MODE_HEADER] = RUN_MODE_TEST
            console.print("[yellow]🧪 Mock 模式已启用（测试运行）[/yellow]")

        client = VideoGenerationClient(
            config, ctx=ctx, custom_headers=custom_headers, verbose=verbose
        )

        image_urls = None
        if image_url:
            image_urls = [url.strip() for url in image_url.split(",")]

        ratio, resolution = parse_resolution(size)

        video_config = VideoConfig(
            resolution=resolution or "720p",
            ratio=ratio or "16:9",
            duration=duration or 5,
            watermark=watermark,
            seed=seed,
            camerafixed=camerafixed,
        )

        content_items = []

        if prompt:
            content_items.append(TextContent(text=prompt))

        if image_urls:
            if len(image_urls) == 1:
                content_items.append(
                    ImageURLContent(
                        image_url=ImageURL(url=image_urls[0]), role="first_frame"
                    )
                )
            elif len(image_urls) == 2:
                content_items.append(
                    ImageURLContent(
                        image_url=ImageURL(url=image_urls[0]), role="first_frame"
                    )
                )
                content_items.append(
                    ImageURLContent(
                        image_url=ImageURL(url=image_urls[1]), role="last_frame"
                    )
                )
            else:
                raise ValueError("Only 1 or 2 images are supported")

        if not content_items:
            raise ValueError("Either --prompt or --image-url must be provided")

        model_name = model or "doubao-seedance-1-0-pro-fast-251015"

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Generating video...", total=None)

            try:
                video_url, response, last_frame_url = client.video_generation(
                    content_items=content_items,
                    model=model_name,
                    config=video_config,
                    callback_url=callback_url,
                    return_last_frame=return_last_frame,
                )

                progress.update(
                    task, description="[green]✓ Video generation completed!"
                )
                result = response

            except APIError as e:
                progress.update(task, description="[red]✗ Video generation failed")
                console.print(f"[red]Error: {str(e)}[/red]")
                raise click.Abort()

        table = Table(title="Video Generation Result")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="green", no_wrap=True, overflow="fold")

        table.add_row("Task ID", result.get("id", ""))
        table.add_row("Status", result.get("status", ""))

        video_url = result.get("content", {}).get("video_url")
        if video_url:
            table.add_row("Video URL", video_url)
        if return_last_frame and last_frame_url:
            table.add_row("Last Frame URL", last_frame_url)
        if result.get("error_message"):
            table.add_row("Error", result.get("error_message"))

        console.print(table)

        if video_url:
            console.print(f"\n[cyan]Complete Video URL:[/cyan]")
            console.print(f"[green]{video_url}[/green]")
        if return_last_frame and last_frame_url:
            console.print(f"\n[cyan]Complete Last Frame URL:[/cyan]")
            console.print(f"[green]{last_frame_url}[/green]")

        if output:
            with open(output, "w") as f:
                json.dump(result, f, indent=2)
            console.print(f"\n[green]✓[/green] Result saved to: {output}")

    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise click.Abort()
