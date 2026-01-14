from enum import IntEnum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class DataSourceType(IntEnum):
    TEXT = 0
    URL = 1
    URI = 2


class ChunkConfig(BaseModel):
    separator: str = Field(..., description="Chunk separator")
    max_tokens: int = Field(..., description="Max tokens per chunk")
    remove_extra_spaces: bool = Field(False, description="Normalize extra spaces")
    remove_urls_emails: bool = Field(False, description="Strip URLs and emails")


class KnowledgeDocument(BaseModel):
    source: DataSourceType = Field(..., description="Data source type")
    raw_data: Optional[str] = Field(None, description="Plain text content (for RAW_TEXT)")
    uri: Optional[str] = Field(None, description="Object storage URI")
    url: Optional[str] = Field(None, description="Document download link")
    
    def to_api_format(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)


class KnowledgeChunk(BaseModel):
    content: str = Field(..., description="The content of the chunk (slice)")
    score: float = Field(..., description="Similarity score")
    chunk_id: Optional[str] = Field(None, description="Unique identifier of the chunk")
    doc_id: Optional[str] = Field(None, description="Unique identifier of the document")


class KnowledgeSearchResponse(BaseModel):
    chunks: List[KnowledgeChunk] = Field(default_factory=list, description="List of matching knowledge chunks")
    code: int = Field(..., description="Status code")
    msg: str = Field(..., description="Status message")


class KnowledgeInsertResponse(BaseModel):
    doc_ids: Optional[List[str]] = Field(None, description="List of inserted document IDs")
    code: int = Field(..., description="Status code")
    msg: str = Field(..., description="Status message")
