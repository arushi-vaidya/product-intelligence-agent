from typing import Any, Optional

from pydantic import BaseModel, Field


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


class InvestigationCreatedResponse(BaseModel):
    investigation_id: str
    status: str


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