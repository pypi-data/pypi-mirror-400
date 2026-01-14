from typing import Dict, List, Optional, Union

from coze_coding_utils.runtime_ctx.context import Context

from ..core.client import BaseClient
from ..core.config import Config
from .models import (
    ChunkConfig,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeInsertResponse,
    KnowledgeSearchResponse,
)


class KnowledgeClient(BaseClient):
    def __init__(
        self,
        config: Optional[Config] = None,
        ctx: Optional[Context] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        verbose: bool = True,
    ):
        super().__init__(config, ctx, custom_headers, verbose)
        # Use COZE_INTEGRATION_BASE_URL as endpoint
        self.base_url = self.config.base_url
        
        # Add default PPE headers for testing
        if self.custom_headers is None:
            self.custom_headers = {}
        self.custom_headers.update({
            "x-tt-env": "ppe_coze_knowledge",
            "x-use-ppe": "1"
        })

    def search(
        self,
        query: str,
        table_names: Optional[List[str]] = None,
        top_k: int = 5,
        min_score: Optional[float] = 0.0,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> KnowledgeSearchResponse:
        """
        Search for knowledge chunks in specified tables.

        Args:
            query: The search query string.
            table_names: List of table names to search in (dataset).
            top_k: Number of results to return. Default is 5.
            min_score: Minimum similarity score. Default is 0.0.
            extra_headers: Extra headers to send with the request.

        Returns:
            KnowledgeSearchResponse: The search results.
        """
        payload = {
            "query": query,
            "top_k": top_k,
            "min_score": min_score,
        }
        if table_names:
            payload["dataset"] = table_names
        
        url = f"{self.base_url}/v1/knowledge_base/recall"

        headers = extra_headers or {}
        if self.config.api_key:
             headers["x-coze-token"] = f"Bearer {self.config.api_key}"

        response = self._request(
            method="POST",
            url=url,
            json=payload,
            headers=headers,
        )

        # Response structure: { "data": [ ... ], "BaseResp": ... }
        # RecallDataInfo: { "slice": "...", "score": 0.0, "chunk_id": "...", "doc_id": "..." }
        
        data_list = response.get("data", [])
        
        chunks = []
        for item in data_list:
            # Map RecallDataInfo to KnowledgeChunk
            chunks.append(KnowledgeChunk(
                content=item.get("slice", ""),
                score=item.get("score", 0.0),
                chunk_id=item.get("chunk_id"),
                doc_id=item.get("doc_id")
            ))
            
        return KnowledgeSearchResponse(
            chunks=chunks,
            code=response.get("code", 0),
            msg=response.get("msg", "")
        )

    def add_documents(
        self,
        documents: List[Union[KnowledgeDocument, Dict]],
        table_name: str,
        chunk_config: Optional[ChunkConfig] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> KnowledgeInsertResponse:
        """
        Add documents to a specified table in the knowledge base (BatchImportData).

        Args:
            documents: List of documents to add. Can be KnowledgeDocument objects or dictionaries.
            table_name: The name of the table to add documents to (dataset).
            chunk_config: Optional chunking configuration.
            extra_headers: Extra headers to send with the request.

        Returns:
            KnowledgeInsertResponse: The response containing inserted document IDs and status.
        """
        docs_payload = []
        for doc in documents:
            if isinstance(doc, KnowledgeDocument):
                docs_payload.append(doc.to_api_format())
            else:
                # Assuming dictionary is already in correct format or close to it
                docs_payload.append(doc)

        payload = {
            "dataset": table_name,
            "data": docs_payload,
        }
        
        if chunk_config:
            payload["chunk_config"] = chunk_config.model_dump(exclude_none=True)

        url = f"{self.base_url}/v1/knowledge_base/batch_import"

        headers = extra_headers or {}
        if self.config.api_key:
             headers["x-coze-token"] = f"Bearer {self.config.api_key}"

        response = self._request(
            method="POST",
            url=url,
            json=payload,
            headers=headers,
        )
        
        code = response.get("code", 0)
        msg = response.get("msg", "")
        if code == 0:
            msg = "成功！文档正在异步导入中，请稍候。您可以查看数据库中的 'knowledge' schema 来验证导入状态。"

        return KnowledgeInsertResponse(
            doc_ids=response.get("doc_ids"),
            code=code,
            msg=msg
        )
