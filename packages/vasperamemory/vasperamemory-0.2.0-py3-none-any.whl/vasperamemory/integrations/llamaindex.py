"""LlamaIndex integration for VasperaMemory.

Example:
    ```python
    from vasperamemory import VasperaMemory
    from vasperamemory.integrations.llamaindex import VasperaMemoryVectorStore

    vm = VasperaMemory(api_key="vm_xxx", project_id="proj_xxx")
    vector_store = VasperaMemoryVectorStore(vasperamemory=vm)

    # Use with LlamaIndex
    from llama_index.core import VectorStoreIndex
    index = VectorStoreIndex.from_vector_store(vector_store)
    ```
"""

from typing import Any, List, Optional

try:
    from llama_index.core.schema import NodeWithScore, QueryBundle, TextNode
    from llama_index.core.vector_stores.types import (
        BasePydanticVectorStore,
        VectorStoreQuery,
        VectorStoreQueryResult,
    )
except ImportError:
    raise ImportError(
        "LlamaIndex is required for this integration. "
        "Install it with: pip install vasperamemory[llamaindex]"
    )

from ..client import VasperaMemory


class VasperaMemoryVectorStore(BasePydanticVectorStore):
    """LlamaIndex vector store backed by VasperaMemory.

    Example:
        ```python
        from vasperamemory import VasperaMemory
        from vasperamemory.integrations.llamaindex import VasperaMemoryVectorStore
        from llama_index.core import VectorStoreIndex

        vm = VasperaMemory(api_key="vm_xxx", project_id="proj_xxx")
        vector_store = VasperaMemoryVectorStore(vasperamemory=vm)

        index = VectorStoreIndex.from_vector_store(vector_store)
        query_engine = index.as_query_engine()
        response = query_engine.query("What caching patterns do we use?")
        ```
    """

    stores_text: bool = True
    flat_metadata: bool = True

    _vasperamemory: VasperaMemory

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, vasperamemory: VasperaMemory, **kwargs: Any):
        """Initialize the vector store.

        Args:
            vasperamemory: VasperaMemory client instance
        """
        super().__init__(**kwargs)
        self._vasperamemory = vasperamemory

    @property
    def client(self) -> VasperaMemory:
        """Return the VasperaMemory client."""
        return self._vasperamemory

    def add(self, nodes: List[TextNode], **kwargs: Any) -> List[str]:
        """Add nodes to the vector store.

        Stores nodes as memories in VasperaMemory.

        Args:
            nodes: List of nodes to add

        Returns:
            List of node IDs
        """
        ids = []
        for node in nodes:
            try:
                memory = self._vasperamemory.capture_memory(
                    content=node.get_content(),
                    type="pattern",
                    reasoning=node.metadata.get("source", "Added via LlamaIndex"),
                    confidence=0.8,
                )
                ids.append(memory.id)
            except Exception:
                ids.append(node.node_id)
        return ids

    def delete(self, ref_doc_id: str, **kwargs: Any) -> None:
        """Delete a node from the vector store.

        Args:
            ref_doc_id: Reference document ID to delete
        """
        try:
            self._vasperamemory.delete_memory(ref_doc_id)
        except Exception:
            pass  # Ignore if not found

    def query(
        self,
        query: VectorStoreQuery,
        **kwargs: Any,
    ) -> VectorStoreQueryResult:
        """Query the vector store.

        Args:
            query: Query parameters

        Returns:
            Query results
        """
        query_str = query.query_str or ""
        similarity_top_k = query.similarity_top_k or 10

        try:
            results = self._vasperamemory.search(
                query=query_str,
                limit=similarity_top_k,
                threshold=0.5,
            )

            nodes = []
            similarities = []
            ids = []

            for result in results:
                item = result.item
                content_parts = [item.content]
                if hasattr(item, "reasoning") and item.reasoning:
                    content_parts.append(f"Reasoning: {item.reasoning}")

                node = TextNode(
                    text="\n".join(content_parts),
                    id_=item.id,
                    metadata={
                        "type": getattr(item, "type", "memory"),
                        "source": "vasperamemory",
                    },
                )
                nodes.append(node)
                similarities.append(result.score)
                ids.append(item.id)

            return VectorStoreQueryResult(
                nodes=nodes,
                similarities=similarities,
                ids=ids,
            )
        except Exception:
            return VectorStoreQueryResult(nodes=[], similarities=[], ids=[])
