"""LangChain integration for VasperaMemory.

Example:
    ```python
    from vasperamemory import VasperaMemory
    from vasperamemory.integrations.langchain import VasperaMemoryRetriever

    vm = VasperaMemory(api_key="vm_xxx", project_id="proj_xxx")
    retriever = VasperaMemoryRetriever(vasperamemory=vm)

    # Use in a chain
    from langchain.chains import RetrievalQA
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
    )
    ```
"""

from typing import Any, List, Optional

try:
    from langchain_core.callbacks import CallbackManagerForRetrieverRun
    from langchain_core.chat_history import BaseChatMessageHistory
    from langchain_core.documents import Document
    from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
    from langchain_core.retrievers import BaseRetriever
except ImportError:
    raise ImportError(
        "LangChain is required for this integration. "
        "Install it with: pip install vasperamemory[langchain]"
    )

from ..client import VasperaMemory


class VasperaMemoryRetriever(BaseRetriever):
    """LangChain retriever backed by VasperaMemory.

    Retrieves relevant memories based on semantic similarity.

    Example:
        ```python
        from vasperamemory import VasperaMemory
        from vasperamemory.integrations.langchain import VasperaMemoryRetriever

        vm = VasperaMemory(api_key="vm_xxx", project_id="proj_xxx")
        retriever = VasperaMemoryRetriever(vasperamemory=vm, k=5)

        docs = retriever.invoke("authentication patterns")
        ```
    """

    vasperamemory: VasperaMemory
    """VasperaMemory client instance."""

    k: int = 4
    """Number of documents to retrieve."""

    threshold: float = 0.7
    """Minimum relevance score."""

    include_decisions: bool = True
    """Whether to include decisions in search."""

    include_error_fixes: bool = True
    """Whether to include error fixes in search."""

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
    ) -> List[Document]:
        """Get documents relevant to a query.

        Args:
            query: String to find relevant documents for
            run_manager: Callback manager

        Returns:
            List of relevant documents
        """
        documents: List[Document] = []

        # Search memories
        try:
            results = self.vasperamemory.search(
                query=query,
                limit=self.k,
                threshold=self.threshold,
            )

            for result in results:
                item = result.item
                metadata = {
                    "source": "vasperamemory",
                    "type": getattr(item, "type", "memory"),
                    "id": item.id,
                    "score": result.score,
                }

                # Build content based on item type
                content_parts = [item.content]
                if hasattr(item, "reasoning") and item.reasoning:
                    content_parts.append(f"Reasoning: {item.reasoning}")

                documents.append(
                    Document(
                        page_content="\n".join(content_parts),
                        metadata=metadata,
                    )
                )
        except Exception:
            pass  # Continue if search fails

        # Get recent decisions if enabled
        if self.include_decisions:
            try:
                decisions = self.vasperamemory.get_recent_decisions(limit=3)
                for decision in decisions:
                    content_parts = [
                        f"Decision: {decision.title}",
                        decision.content,
                    ]
                    if decision.reasoning:
                        content_parts.append(f"Reasoning: {decision.reasoning}")

                    documents.append(
                        Document(
                            page_content="\n".join(content_parts),
                            metadata={
                                "source": "vasperamemory",
                                "type": "decision",
                                "category": decision.category.value,
                                "id": decision.id,
                            },
                        )
                    )
            except Exception:
                pass

        # Get error fixes if enabled and query looks like an error
        if self.include_error_fixes and any(
            word in query.lower() for word in ["error", "exception", "fail", "bug"]
        ):
            try:
                fix = self.vasperamemory.find_error_fix(query)
                if fix:
                    content_parts = [
                        f"Error: {fix.error_message}",
                        f"Root Cause: {fix.root_cause}",
                        f"Fix: {fix.fix_description}",
                    ]
                    if fix.prevention_rule:
                        content_parts.append(f"Prevention: {fix.prevention_rule}")

                    documents.append(
                        Document(
                            page_content="\n".join(content_parts),
                            metadata={
                                "source": "vasperamemory",
                                "type": "error_fix",
                                "id": fix.id,
                            },
                        )
                    )
            except Exception:
                pass

        return documents


class VasperaMemoryChatHistory(BaseChatMessageHistory):
    """LangChain chat history backed by VasperaMemory.

    Stores and retrieves conversation history as memories.

    Example:
        ```python
        from vasperamemory import VasperaMemory
        from vasperamemory.integrations.langchain import VasperaMemoryChatHistory
        from langchain.memory import ConversationBufferMemory

        vm = VasperaMemory(api_key="vm_xxx", project_id="proj_xxx")
        history = VasperaMemoryChatHistory(vasperamemory=vm, session_id="chat_123")

        memory = ConversationBufferMemory(chat_memory=history)
        ```
    """

    vasperamemory: VasperaMemory
    """VasperaMemory client instance."""

    session_id: str
    """Unique identifier for this chat session."""

    _messages: List[BaseMessage] = []

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._messages = []

    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve messages."""
        return self._messages

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the history."""
        self._messages.append(message)

        # Store important messages as memories
        if isinstance(message, AIMessage) and len(message.content) > 100:
            try:
                self.vasperamemory.capture_memory(
                    content=f"[Chat {self.session_id}] AI: {message.content[:500]}",
                    type="pattern",
                    reasoning="Captured from chat history",
                    confidence=0.6,
                )
            except Exception:
                pass  # Don't fail if memory capture fails

    def add_user_message(self, message: str) -> None:
        """Add a user message."""
        self.add_message(HumanMessage(content=message))

    def add_ai_message(self, message: str) -> None:
        """Add an AI message."""
        self.add_message(AIMessage(content=message))

    def clear(self) -> None:
        """Clear message history."""
        self._messages = []
