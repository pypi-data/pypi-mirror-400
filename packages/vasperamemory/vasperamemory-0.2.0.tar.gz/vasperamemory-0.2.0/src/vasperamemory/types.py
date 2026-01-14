"""Type definitions for VasperaMemory SDK."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class MemoryType(str, Enum):
    """Type of memory to capture."""

    PATTERN = "pattern"
    DECISION = "decision"
    ARCHITECTURAL = "architectural"


class DecisionCategory(str, Enum):
    """Category of decision."""

    ARCHITECTURAL = "architectural"
    PATTERN = "pattern"
    CONVENTION = "convention"
    FIX = "fix"
    REJECTION = "rejection"
    PREFERENCE = "preference"


class PreferenceCategory(str, Enum):
    """Category of preference."""

    CODE_STYLE = "code_style"
    COMMUNICATION = "communication"
    WORKFLOW = "workflow"
    TOOLING = "tooling"
    VALUES = "values"


class Memory(BaseModel):
    """A captured memory."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    project_id: str = Field(alias="projectId")
    type: MemoryType
    content: str
    reasoning: Optional[str] = None
    confidence: float = 0.8
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class Decision(BaseModel):
    """A captured decision."""

    id: str
    project_id: str = Field(alias="projectId")
    category: DecisionCategory
    title: str
    content: str
    reasoning: Optional[str] = None
    related_files: Optional[list[str]] = Field(default=None, alias="relatedFiles")
    confidence: float = 0.9
    created_at: datetime = Field(alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)



class ErrorFix(BaseModel):
    """A captured error fix."""

    id: str
    project_id: str = Field(alias="projectId")
    error_message: str = Field(alias="errorMessage")
    error_file: Optional[str] = Field(default=None, alias="errorFile")
    root_cause: str = Field(alias="rootCause")
    fix_description: str = Field(alias="fixDescription")
    prevention_rule: Optional[str] = Field(default=None, alias="preventionRule")
    created_at: datetime = Field(alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)



class Preference(BaseModel):
    """A user preference."""

    id: str
    project_id: Optional[str] = Field(default=None, alias="projectId")
    category: PreferenceCategory
    key: str
    value: str
    confidence: float = 1.0
    created_at: datetime = Field(alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)



class SearchResult(BaseModel):
    """A search result with relevance score."""

    item: Memory | Decision | ErrorFix
    score: float


class SessionContext(BaseModel):
    """Session context from VasperaMemory."""

    decisions: list[Decision] = Field(default_factory=list)
    preferences: list[Preference] = Field(default_factory=list)
    recent_fixes: list[ErrorFix] = Field(default_factory=list, alias="recentFixes")
    memories: list[Memory] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)



class FusedContext(BaseModel):
    """Fused context from multiple sources."""

    content: str
    sources: list[str] = Field(default_factory=list)
    token_count: int = Field(default=0, alias="tokenCount")

    model_config = ConfigDict(populate_by_name=True)



# Request/Response models


class CaptureMemoryRequest(BaseModel):
    """Request to capture a memory."""

    type: MemoryType
    content: str
    reasoning: Optional[str] = None
    confidence: float = 0.8


class CaptureDecisionRequest(BaseModel):
    """Request to capture a decision."""

    category: DecisionCategory
    title: str
    content: str
    reasoning: Optional[str] = None
    related_files: Optional[list[str]] = Field(default=None, alias="relatedFiles")
    confidence: float = 0.9

    model_config = ConfigDict(populate_by_name=True)



class CaptureErrorFixRequest(BaseModel):
    """Request to capture an error fix."""

    error_message: str = Field(alias="errorMessage")
    error_file: Optional[str] = Field(default=None, alias="errorFile")
    root_cause: str = Field(alias="rootCause")
    fix_description: str = Field(alias="fixDescription")
    prevention_rule: Optional[str] = Field(default=None, alias="preventionRule")

    model_config = ConfigDict(populate_by_name=True)



class SetPreferenceRequest(BaseModel):
    """Request to set a preference."""

    category: PreferenceCategory
    key: str
    value: str
    confidence: float = 1.0


class SearchRequest(BaseModel):
    """Request to search memories."""

    query: str
    limit: int = 10
    threshold: float = 0.7


# ============ CHANGE ANALYSIS TYPES ============


class ChangeImpact(BaseModel):
    """Impact analysis for a code change."""

    model_config = ConfigDict(populate_by_name=True)

    file: str
    affected_files: list[str] = Field(default_factory=list, alias="affectedFiles")
    affected_symbols: list[str] = Field(default_factory=list, alias="affectedSymbols")
    risk_level: str = Field(default="low", alias="riskLevel")
    suggestions: list[str] = Field(default_factory=list)


class ChangeRisk(BaseModel):
    """Risk assessment for proposed changes."""

    model_config = ConfigDict(populate_by_name=True)

    overall_risk: str = Field(alias="overallRisk")
    risk_score: float = Field(alias="riskScore")
    risk_factors: list[str] = Field(default_factory=list, alias="riskFactors")
    recommendations: list[str] = Field(default_factory=list)


# ============ ENTITY TYPES ============


class EntityType(str, Enum):
    """Type of code entity."""

    FILE = "file"
    FUNCTION = "function"
    CLASS = "class"
    SERVICE = "service"
    API_ENDPOINT = "api_endpoint"
    PERSON = "person"
    PACKAGE = "package"
    ERROR_TYPE = "error_type"
    CONCEPT = "concept"


class Entity(BaseModel):
    """A code entity (file, function, class, etc.)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    entity_type: str = Field(alias="entityType")
    value: str
    mention_count: int = Field(default=0, alias="mentionCount")
    context: Optional[str] = None


class EntityRelationship(BaseModel):
    """Relationship between two entities."""

    model_config = ConfigDict(populate_by_name=True)

    source: str
    target: str
    predicate: str
    context: Optional[str] = None


# ============ EXPORT/IMPORT TYPES ============


class ExportResult(BaseModel):
    """Result of exporting memories."""

    model_config = ConfigDict(populate_by_name=True)

    export_id: str = Field(alias="exportId")
    format: str
    item_count: int = Field(alias="itemCount")
    download_url: Optional[str] = Field(default=None, alias="downloadUrl")


class ImportResult(BaseModel):
    """Result of importing memories."""

    model_config = ConfigDict(populate_by_name=True)

    imported_count: int = Field(alias="importedCount")
    skipped_count: int = Field(default=0, alias="skippedCount")
    errors: list[str] = Field(default_factory=list)


# ============ PATTERN FEED TYPES ============


class Pattern(BaseModel):
    """A community or project pattern."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    description: str
    category: str
    code_example: Optional[str] = Field(default=None, alias="codeExample")
    adoption_rate: float = Field(default=0.0, alias="adoptionRate")
    created_at: datetime = Field(alias="createdAt")


class PatternSuggestion(BaseModel):
    """A suggested pattern based on context."""

    model_config = ConfigDict(populate_by_name=True)

    pattern: Pattern
    relevance_score: float = Field(alias="relevanceScore")
    reason: str


# ============ CODE INTELLIGENCE TYPES ============


class SimilarCode(BaseModel):
    """Similar code found in the codebase."""

    model_config = ConfigDict(populate_by_name=True)

    file_path: str = Field(alias="filePath")
    start_line: int = Field(alias="startLine")
    end_line: int = Field(alias="endLine")
    similarity_score: float = Field(alias="similarityScore")
    code_snippet: str = Field(alias="codeSnippet")


class EntityEvolution(BaseModel):
    """Evolution history of a code entity."""

    model_config = ConfigDict(populate_by_name=True)

    entity_name: str = Field(alias="entityName")
    file_path: str = Field(alias="filePath")
    version_count: int = Field(alias="versionCount")
    stability_score: float = Field(alias="stabilityScore")
    last_change: datetime = Field(alias="lastChange")
    changes: list[dict[str, Any]] = Field(default_factory=list)
