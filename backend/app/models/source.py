from pydantic import BaseModel
from typing import Optional


class Source(BaseModel):
    id: str
    url: str
    source_type: str

    # 1 = manufacturer
    # 2 = authorized distributor
    # 3 = marketplace / other
    authority_tier: int

    title: Optional[str] = None