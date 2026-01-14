"""
S3 模块数据模型
"""

from typing import Optional, List, TypedDict


class ListFilesResult(TypedDict):
    """list_files 的返回结构类型"""

    keys: List[str]
    is_truncated: bool
    next_continuation_token: Optional[str]


__all__ = [
    "ListFilesResult",
]
