from dataclasses import dataclass, field
from typing import Any


@dataclass
class Entity:
    id: str
    entity_type: str
    properties: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class Relationship:
    source_id: str
    relationship_type: str
    target_id: str
    properties: dict[str, Any] = field(
        default_factory=dict
    )