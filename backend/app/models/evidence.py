from pydantic import BaseModel
from typing import Optional, Union


class Evidence(BaseModel):
    field: str
    value: Union[str, float, int]
    unit: Optional[str] = None

    source_id: str
    source_url: Optional[str] = None

    page: Optional[int] = None
    raw_text: Optional[str] = None

    extracted_by: str
    confidence: float = 0.0