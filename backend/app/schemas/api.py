from typing import Any, Optional

from pydantic import BaseModel, Field
from datetime import datetime


class InvestigationRequest(BaseModel):
    manufacturer: str = Field(
        ...,
        min_length=1,
        description="Product manufacturer"
    )

    mpn: str = Field(
        ...,
        min_length=1,
        description="Manufacturer part number"
    )


class ProductExtractionResponse(BaseModel):
    manufacturer: Optional[str] = None
    mpn: Optional[str] = None
    notes: Optional[str] = None


class InvestigationCreatedResponse(BaseModel):
    investigation_id: str
    status: str


class InvestigationSummary(BaseModel):
    investigation_id: str
    status: str
    manufacturer: str
    mpn: str
    product_category: Optional[str] = None
    source_count: int = 0
    variant_count: int = 0
    commerce_readiness: Optional[str] = None
    created_at: datetime


class InvestigationListResponse(BaseModel):
    investigations: list[InvestigationSummary] = Field(
        default_factory=list
    )


class TaskResponse(BaseModel):
    id: str
    agent: str
    status: str
    attempts: int

    depends_on: list[str] = Field(
        default_factory=list
    )

    output: Optional[dict[str, Any]] = Field(
        default=None
    )


class ProductIntelligenceResponse(BaseModel):
    manufacturer: str
    mpn: str
    product_category: str

    enrichment: dict[str, Any] = Field(
        default_factory=dict
    )

    family_specifications: dict[str, Any] = Field(
        default_factory=dict
    )

    variants: list[dict[str, Any]] = Field(
        default_factory=list
    )

    knowledge_graph: dict[str, Any] = Field(
        default_factory=dict
    )

    conflict_resolutions: list[
        dict[str, Any]
    ] = Field(
        default_factory=list
    )

    evidence_validation: dict[str, Any] = Field(
        default_factory=dict
    )

    quality: dict[str, Any] = Field(
        default_factory=dict
    )

    commerce_readiness: dict[str, Any] = Field(
        default_factory=dict
    )

    sources: list[dict[str, Any]] = Field(
        default_factory=list
    )


class InvestigationResponse(BaseModel):
    investigation_id: str
    status: str

    input: InvestigationRequest

    result: Optional[
        ProductIntelligenceResponse
    ] = None

    tasks: list[TaskResponse] = Field(
        default_factory=list
    )