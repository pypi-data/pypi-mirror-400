"""VasperaMemory Python SDK Client."""

from typing import Any, Optional

import httpx

from .exceptions import (
    AuthenticationError,
    NetworkError,
    ProjectNotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .types import (
    CaptureDecisionRequest,
    CaptureErrorFixRequest,
    CaptureMemoryRequest,
    ChangeImpact,
    ChangeRisk,
    Decision,
    DecisionCategory,
    Entity,
    EntityEvolution,
    EntityRelationship,
    EntityType,
    ErrorFix,
    ExportResult,
    FusedContext,
    ImportResult,
    Memory,
    MemoryType,
    Pattern,
    PatternSuggestion,
    Preference,
    PreferenceCategory,
    SearchResult,
    SessionContext,
    SetPreferenceRequest,
    SimilarCode,
)

DEFAULT_BASE_URL = "https://vasperamemory-mcp-production.up.railway.app"


class VasperaMemory:
    """VasperaMemory SDK client.

    Example:
        ```python
        from vasperamemory import VasperaMemory

        vm = VasperaMemory(api_key="vm_xxx", project_id="proj_xxx")

        # Capture a decision
        vm.capture_decision(
            category="architectural",
            title="Use Redis for caching",
            content="Chose Redis over Memcached for its data structure support",
            reasoning="Need sorted sets for leaderboards"
        )

        # Search memories
        results = vm.search("caching strategy", limit=5)
        ```
    """

    def __init__(
        self,
        api_key: str,
        project_id: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ):
        """Initialize the VasperaMemory client.

        Args:
            api_key: Your VasperaMemory API key (starts with 'vm_')
            project_id: The project ID to use
            base_url: API base URL (default: production)
            timeout: Request timeout in seconds
        """
        if not api_key or not api_key.startswith("vm_"):
            raise ValidationError("API key must start with 'vm_'")
        if not project_id:
            raise ValidationError("Project ID is required")

        self.api_key = api_key
        self.project_id = project_id
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "vasperamemory-python/0.2.0",
            },
            timeout=timeout,
        )

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        if response.status_code == 404:
            raise ProjectNotFoundError("Project not found")
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                "Rate limit exceeded",
                retry_after=int(retry_after) if retry_after else None,
            )
        if response.status_code == 422:
            raise ValidationError(response.json().get("detail", "Validation error"))
        if response.status_code >= 500:
            raise ServerError(
                f"Server error: {response.text}", status_code=response.status_code
            )
        if response.status_code >= 400:
            raise ServerError(
                f"Request failed: {response.text}", status_code=response.status_code
            )

        return response.json()

    def _request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Make an API request."""
        try:
            response = self._client.request(method, endpoint, **kwargs)
            return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}") from e

    # ============ MEMORY METHODS ============

    def capture_memory(
        self,
        content: str,
        type: MemoryType | str = MemoryType.PATTERN,
        reasoning: Optional[str] = None,
        confidence: float = 0.8,
    ) -> Memory:
        """Capture a new memory.

        Args:
            content: The memory content
            type: Type of memory (pattern, decision, architectural)
            reasoning: Why this memory was captured
            confidence: Confidence score (0-1)

        Returns:
            The captured memory
        """
        if isinstance(type, str):
            type = MemoryType(type)

        request = CaptureMemoryRequest(
            type=type,
            content=content,
            reasoning=reasoning,
            confidence=confidence,
        )

        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/memories",
            json=request.model_dump(exclude_none=True),
        )
        return Memory.model_validate(data)

    def search(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> list[SearchResult]:
        """Search for relevant memories.

        Args:
            query: Search query
            limit: Maximum number of results
            threshold: Minimum relevance score (0-1)

        Returns:
            List of search results with scores
        """
        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/memories/search",
            json={"query": query, "limit": limit, "threshold": threshold},
        )
        return [SearchResult.model_validate(item) for item in data.get("results", [])]

    def get_memory(self, memory_id: str) -> Memory:
        """Get a specific memory by ID.

        Args:
            memory_id: The memory ID

        Returns:
            The memory
        """
        data = self._request(
            "GET", f"/v1/projects/{self.project_id}/memories/{memory_id}"
        )
        return Memory.model_validate(data)

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory.

        Args:
            memory_id: The memory ID

        Returns:
            True if deleted successfully
        """
        self._request("DELETE", f"/v1/projects/{self.project_id}/memories/{memory_id}")
        return True

    # ============ DECISION METHODS ============

    def capture_decision(
        self,
        category: DecisionCategory | str,
        title: str,
        content: str,
        reasoning: Optional[str] = None,
        related_files: Optional[list[str]] = None,
        confidence: float = 0.9,
    ) -> Decision:
        """Capture a decision.

        Args:
            category: Decision category
            title: Brief title (max 50 chars)
            content: Decision content
            reasoning: Why this decision was made
            related_files: Files related to this decision
            confidence: Confidence score (0-1)

        Returns:
            The captured decision
        """
        if isinstance(category, str):
            category = DecisionCategory(category)

        request = CaptureDecisionRequest(
            category=category,
            title=title,
            content=content,
            reasoning=reasoning,
            relatedFiles=related_files,
            confidence=confidence,
        )

        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/decisions",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
        return Decision.model_validate(data)

    def get_recent_decisions(
        self,
        category: Optional[DecisionCategory | str] = None,
        limit: int = 5,
    ) -> list[Decision]:
        """Get recent decisions.

        Args:
            category: Filter by category
            limit: Maximum number of results

        Returns:
            List of recent decisions
        """
        params: dict[str, Any] = {"limit": limit}
        if category:
            params["category"] = (
                category.value if isinstance(category, DecisionCategory) else category
            )

        data = self._request(
            "GET", f"/v1/projects/{self.project_id}/decisions", params=params
        )
        return [Decision.model_validate(item) for item in data.get("decisions", [])]

    # ============ ERROR FIX METHODS ============

    def capture_error_fix(
        self,
        error_message: str,
        root_cause: str,
        fix_description: str,
        error_file: Optional[str] = None,
        prevention_rule: Optional[str] = None,
    ) -> ErrorFix:
        """Capture an error fix.

        Args:
            error_message: The error message that was fixed
            root_cause: The underlying cause of the error
            fix_description: How the error was fixed
            error_file: File where the error occurred
            prevention_rule: How to prevent this error in the future

        Returns:
            The captured error fix
        """
        request = CaptureErrorFixRequest(
            errorMessage=error_message,
            rootCause=root_cause,
            fixDescription=fix_description,
            errorFile=error_file,
            preventionRule=prevention_rule,
        )

        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/error-fixes",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
        return ErrorFix.model_validate(data)

    def find_error_fix(self, error_message: str) -> Optional[ErrorFix]:
        """Find a fix for an error message.

        Args:
            error_message: The error message to search for

        Returns:
            The error fix if found, None otherwise
        """
        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/error-fixes/search",
            json={"errorMessage": error_message},
        )
        if data.get("fix"):
            return ErrorFix.model_validate(data["fix"])
        return None

    def get_recent_fixes(self, limit: int = 5, days: int = 7) -> list[ErrorFix]:
        """Get recent error fixes.

        Args:
            limit: Maximum number of results
            days: Look back this many days

        Returns:
            List of recent error fixes
        """
        data = self._request(
            "GET",
            f"/v1/projects/{self.project_id}/error-fixes",
            params={"limit": limit, "days": days},
        )
        return [ErrorFix.model_validate(item) for item in data.get("fixes", [])]

    # ============ PREFERENCE METHODS ============

    def set_preference(
        self,
        category: PreferenceCategory | str,
        key: str,
        value: str,
        confidence: float = 1.0,
    ) -> Preference:
        """Set a preference.

        Args:
            category: Preference category
            key: Unique key for the preference
            value: The preference value
            confidence: Confidence score (0-1)

        Returns:
            The set preference
        """
        if isinstance(category, str):
            category = PreferenceCategory(category)

        request = SetPreferenceRequest(
            category=category,
            key=key,
            value=value,
            confidence=confidence,
        )

        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/preferences",
            json=request.model_dump(exclude_none=True),
        )
        return Preference.model_validate(data)

    def get_preferences(
        self,
        category: Optional[PreferenceCategory | str] = None,
        limit: int = 10,
    ) -> list[Preference]:
        """Get preferences.

        Args:
            category: Filter by category
            limit: Maximum number of results

        Returns:
            List of preferences
        """
        params: dict[str, Any] = {"limit": limit}
        if category:
            params["category"] = (
                category.value if isinstance(category, PreferenceCategory) else category
            )

        data = self._request(
            "GET", f"/v1/projects/{self.project_id}/preferences", params=params
        )
        return [Preference.model_validate(item) for item in data.get("preferences", [])]

    # ============ CONTEXT METHODS ============

    def get_session_context(
        self,
        query: Optional[str] = None,
        open_files: Optional[list[str]] = None,
    ) -> SessionContext:
        """Get comprehensive session context.

        Args:
            query: The user's initial question/task
            open_files: List of currently open files

        Returns:
            Session context including decisions, preferences, fixes, memories
        """
        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/context/session",
            json={"query": query, "openFiles": open_files},
        )
        return SessionContext.model_validate(data)

    def fuse_context(
        self,
        sources: list[str] | None = None,
        max_tokens: int = 4000,
    ) -> FusedContext:
        """Get fused context from multiple sources.

        Args:
            sources: Sources to include (specs, plans, history, memories)
            max_tokens: Maximum tokens in response

        Returns:
            Fused context
        """
        if sources is None:
            sources = ["memories"]

        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/context/fuse",
            json={"sources": sources, "maxTokens": max_tokens},
        )
        return FusedContext.model_validate(data)

    # ============ CHANGE ANALYSIS METHODS ============

    def analyze_change_impact(
        self,
        file_to_change: str,
        symbols_to_modify: list[str],
    ) -> ChangeImpact:
        """Analyze the impact of modifying code.

        Args:
            file_to_change: The file that will be modified
            symbols_to_modify: Names of functions, classes, or variables being modified

        Returns:
            Impact analysis showing affected files and symbols
        """
        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/analysis/impact",
            json={
                "fileToChange": file_to_change,
                "symbolsToModify": symbols_to_modify,
            },
        )
        return ChangeImpact.model_validate(data)

    def predict_change_impact(
        self,
        file_path: str,
        change_type: str = "feature",
        symbol_name: Optional[str] = None,
    ) -> ChangeImpact:
        """Predict the ripple effects of modifying code.

        Args:
            file_path: File to be modified
            change_type: Type of change (signature, behavior, deletion, rename)
            symbol_name: Optional specific function/class being changed

        Returns:
            Predicted impact including direct and transitive dependencies
        """
        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/analysis/predict",
            json={
                "filePath": file_path,
                "changeType": change_type,
                "symbolName": symbol_name,
            },
        )
        return ChangeImpact.model_validate(data)

    def estimate_change_risk(
        self,
        files_to_change: list[str],
        change_type: str = "feature",
    ) -> ChangeRisk:
        """Assess risk before making changes to files.

        Args:
            files_to_change: Files that will be modified
            change_type: Type of change (refactor, feature, bugfix, delete, rename)

        Returns:
            Risk assessment with factors and recommendations
        """
        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/analysis/risk",
            json={
                "filesToChange": files_to_change,
                "changeType": change_type,
            },
        )
        return ChangeRisk.model_validate(data)

    def find_similar_code(
        self,
        code: str,
        threshold: float = 0.7,
        limit: int = 10,
    ) -> list[SimilarCode]:
        """Find similar implementations across the codebase.

        Args:
            code: Code snippet to find similar implementations for
            threshold: Similarity threshold (0-1)
            limit: Maximum results

        Returns:
            List of similar code snippets
        """
        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/analysis/similar",
            json={
                "code": code,
                "threshold": threshold,
                "limit": limit,
            },
        )
        return [SimilarCode.model_validate(item) for item in data.get("results", [])]

    # ============ ENTITY METHODS ============

    def search_entities(
        self,
        query: str,
        entity_type: Optional[EntityType | str] = None,
        limit: int = 10,
    ) -> list[Entity]:
        """Search for entities across all memories and decisions.

        Args:
            query: Entity name or partial match
            entity_type: Filter by entity type (file, function, class, service, etc.)
            limit: Maximum results

        Returns:
            List of matching entities
        """
        params: dict[str, Any] = {"query": query, "limit": limit}
        if entity_type:
            params["entityType"] = (
                entity_type.value if isinstance(entity_type, EntityType) else entity_type
            )

        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/entities/search",
            json=params,
        )
        return [Entity.model_validate(item) for item in data.get("entities", [])]

    def get_entity_relationships(
        self,
        entity_value: str,
        direction: str = "both",
        predicate_filter: Optional[str] = None,
    ) -> list[EntityRelationship]:
        """Get relationships between entities.

        Args:
            entity_value: Starting entity to find relationships for
            direction: Relationship direction (outgoing, incoming, both)
            predicate_filter: Filter by relationship type (uses, depends_on, calls, etc.)

        Returns:
            List of entity relationships
        """
        params: dict[str, Any] = {
            "entityValue": entity_value,
            "direction": direction,
        }
        if predicate_filter:
            params["predicateFilter"] = predicate_filter

        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/entities/relationships",
            json=params,
        )
        return [
            EntityRelationship.model_validate(item)
            for item in data.get("relationships", [])
        ]

    def get_entity_evolution(
        self,
        file_path: str,
        entity_name: Optional[str] = None,
    ) -> EntityEvolution:
        """Track how code entities evolve over time.

        Args:
            file_path: File path to analyze
            entity_name: Optional specific entity name to track

        Returns:
            Evolution history including version count, stability score, changes
        """
        params: dict[str, Any] = {"filePath": file_path}
        if entity_name:
            params["entityName"] = entity_name

        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/entities/evolution",
            json=params,
        )
        return EntityEvolution.model_validate(data)

    # ============ EXPORT/IMPORT METHODS ============

    def export_memory(
        self,
        format: str = "json",
        include_decisions: bool = True,
        include_errors: bool = True,
    ) -> ExportResult:
        """Export memories to various formats.

        Args:
            format: Export format (json, markdown, yaml)
            include_decisions: Include decisions in export
            include_errors: Include error fixes in export

        Returns:
            Export result with download URL
        """
        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/export",
            json={
                "format": format,
                "includeDecisions": include_decisions,
                "includeErrors": include_errors,
            },
        )
        return ExportResult.model_validate(data)

    def import_memory(
        self,
        data: dict[str, Any],
        merge_strategy: str = "append",
    ) -> ImportResult:
        """Import memories from external sources.

        Args:
            data: Memory data to import
            merge_strategy: How to handle conflicts (append, replace, skip)

        Returns:
            Import result with counts
        """
        response = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/import",
            json={
                "data": data,
                "mergeStrategy": merge_strategy,
            },
        )
        return ImportResult.model_validate(response)

    # ============ PATTERN FEED METHODS ============

    def suggest_patterns(
        self,
        context: Optional[str] = None,
        file_path: Optional[str] = None,
        limit: int = 5,
    ) -> list[PatternSuggestion]:
        """Get pattern suggestions based on context.

        Args:
            context: Description of what you're working on
            file_path: Current file path for context
            limit: Maximum suggestions

        Returns:
            List of suggested patterns with relevance scores
        """
        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/patterns/suggest",
            json={
                "context": context,
                "filePath": file_path,
                "limit": limit,
            },
        )
        return [
            PatternSuggestion.model_validate(item)
            for item in data.get("suggestions", [])
        ]

    def search_patterns(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> list[Pattern]:
        """Search community patterns.

        Args:
            query: Search query
            category: Filter by category
            limit: Maximum results

        Returns:
            List of matching patterns
        """
        params: dict[str, Any] = {"query": query, "limit": limit}
        if category:
            params["category"] = category

        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/patterns/search",
            json=params,
        )
        return [Pattern.model_validate(item) for item in data.get("patterns", [])]

    def contribute_pattern(
        self,
        name: str,
        description: str,
        category: str,
        code_example: Optional[str] = None,
    ) -> Pattern:
        """Contribute a pattern to the community.

        Args:
            name: Pattern name
            description: Pattern description
            category: Pattern category
            code_example: Optional code example

        Returns:
            The contributed pattern
        """
        data = self._request(
            "POST",
            f"/v1/projects/{self.project_id}/patterns/contribute",
            json={
                "name": name,
                "description": description,
                "category": category,
                "codeExample": code_example,
            },
        )
        return Pattern.model_validate(data)

    # ============ LIFECYCLE ============

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "VasperaMemory":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncVasperaMemory:
    """Async VasperaMemory SDK client.

    Example:
        ```python
        from vasperamemory import AsyncVasperaMemory

        async with AsyncVasperaMemory(api_key="vm_xxx", project_id="proj_xxx") as vm:
            results = await vm.search("caching strategy")
        ```
    """

    def __init__(
        self,
        api_key: str,
        project_id: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ):
        """Initialize the async VasperaMemory client."""
        if not api_key or not api_key.startswith("vm_"):
            raise ValidationError("API key must start with 'vm_'")
        if not project_id:
            raise ValidationError("Project ID is required")

        self.api_key = api_key
        self.project_id = project_id
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "vasperamemory-python/0.2.0",
            },
            timeout=timeout,
        )

    async def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        if response.status_code == 404:
            raise ProjectNotFoundError("Project not found")
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                "Rate limit exceeded",
                retry_after=int(retry_after) if retry_after else None,
            )
        if response.status_code == 422:
            raise ValidationError(response.json().get("detail", "Validation error"))
        if response.status_code >= 500:
            raise ServerError(
                f"Server error: {response.text}", status_code=response.status_code
            )
        if response.status_code >= 400:
            raise ServerError(
                f"Request failed: {response.text}", status_code=response.status_code
            )

        return response.json()

    async def _request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Make an async API request."""
        try:
            response = await self._client.request(method, endpoint, **kwargs)
            return await self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}") from e

    # ============ ASYNC MEMORY METHODS ============

    async def capture_memory(
        self,
        content: str,
        type: MemoryType | str = MemoryType.PATTERN,
        reasoning: Optional[str] = None,
        confidence: float = 0.8,
    ) -> Memory:
        """Capture a new memory (async)."""
        if isinstance(type, str):
            type = MemoryType(type)

        request = CaptureMemoryRequest(
            type=type,
            content=content,
            reasoning=reasoning,
            confidence=confidence,
        )

        data = await self._request(
            "POST",
            f"/v1/projects/{self.project_id}/memories",
            json=request.model_dump(exclude_none=True),
        )
        return Memory.model_validate(data)

    async def search(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> list[SearchResult]:
        """Search for relevant memories (async)."""
        data = await self._request(
            "POST",
            f"/v1/projects/{self.project_id}/memories/search",
            json={"query": query, "limit": limit, "threshold": threshold},
        )
        return [SearchResult.model_validate(item) for item in data.get("results", [])]

    async def capture_decision(
        self,
        category: DecisionCategory | str,
        title: str,
        content: str,
        reasoning: Optional[str] = None,
        related_files: Optional[list[str]] = None,
        confidence: float = 0.9,
    ) -> Decision:
        """Capture a decision (async)."""
        if isinstance(category, str):
            category = DecisionCategory(category)

        request = CaptureDecisionRequest(
            category=category,
            title=title,
            content=content,
            reasoning=reasoning,
            relatedFiles=related_files,
            confidence=confidence,
        )

        data = await self._request(
            "POST",
            f"/v1/projects/{self.project_id}/decisions",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
        return Decision.model_validate(data)

    async def get_session_context(
        self,
        query: Optional[str] = None,
        open_files: Optional[list[str]] = None,
    ) -> SessionContext:
        """Get comprehensive session context (async)."""
        data = await self._request(
            "POST",
            f"/v1/projects/{self.project_id}/context/session",
            json={"query": query, "openFiles": open_files},
        )
        return SessionContext.model_validate(data)

    # ============ LIFECYCLE ============

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncVasperaMemory":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
