from pydantic import BaseModel, Field
from typing import Optional

from .evidence import Evidence


class FieldValue(BaseModel):
    value: str | float | int
    unit: Optional[str] = None

    confidence: float
    evidence: list[Evidence] = []


class ProductRecord(BaseModel):
    manufacturer: str
    model_mpn: str
    product_family: Optional[str] = None
    category: str

    specifications: dict[str, FieldValue] = {}

    applications: list[str] = []
    certifications: list[str] = []
    compatible_products: list[str] = []

    quality_score: Optional[float] = None