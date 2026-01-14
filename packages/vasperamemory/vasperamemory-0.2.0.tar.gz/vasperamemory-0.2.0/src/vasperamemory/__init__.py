"""VasperaMemory Python SDK.

Universal AI memory layer for development tools.

Example:
    ```python
    from vasperamemory import VasperaMemory

    vm = VasperaMemory(api_key="vm_xxx", project_id="proj_xxx")

    # Capture a decision
    vm.capture_decision(
        category="architectural",
        title="Use Redis for caching",
        content="Chose Redis over Memcached",
        reasoning="Need sorted sets for leaderboards"
    )

    # Search memories
    results = vm.search("caching strategy", limit=5)
    ```
"""

from .client import AsyncVasperaMemory, VasperaMemory
from .exceptions import (
    AuthenticationError,
    MemoryNotFoundError,
    NetworkError,
    ProjectNotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    VasperaMemoryError,
)
from .types import (
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
    SimilarCode,
)

__version__ = "0.2.0"
__all__ = [
    # Clients
    "VasperaMemory",
    "AsyncVasperaMemory",
    # Core Types
    "Memory",
    "MemoryType",
    "Decision",
    "DecisionCategory",
    "ErrorFix",
    "Preference",
    "PreferenceCategory",
    "SearchResult",
    "SessionContext",
    "FusedContext",
    # Change Analysis Types
    "ChangeImpact",
    "ChangeRisk",
    # Entity Types
    "Entity",
    "EntityType",
    "EntityRelationship",
    "EntityEvolution",
    # Export/Import Types
    "ExportResult",
    "ImportResult",
    # Pattern Types
    "Pattern",
    "PatternSuggestion",
    # Code Intelligence Types
    "SimilarCode",
    # Exceptions
    "VasperaMemoryError",
    "AuthenticationError",
    "RateLimitError",
    "ProjectNotFoundError",
    "MemoryNotFoundError",
    "ValidationError",
    "ServerError",
    "NetworkError",
]
