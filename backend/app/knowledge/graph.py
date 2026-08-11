from .entities import Entity, Relationship


class KnowledgeGraph:

    def __init__(self):

        self.entities: dict[str, Entity] = {}

        self.relationships: list[
            Relationship
        ] = []

    # =====================================
    # ENTITY
    # =====================================

    def add_entity(
        self,
        entity: Entity,
    ) -> Entity:

        self.entities[entity.id] = entity

        return entity

    def get_entity(
        self,
        entity_id: str,
    ) -> Entity | None:

        return self.entities.get(
            entity_id
        )

    # =====================================
    # RELATIONSHIP
    # =====================================

    def add_relationship(
        self,
        relationship: Relationship,
    ):

        self.relationships.append(
            relationship
        )

    # =====================================
    # QUERY
    # =====================================

    def get_relationships(
        self,
        entity_id: str,
    ) -> list[Relationship]:

        return [
            relationship
            for relationship
            in self.relationships
            if (
                relationship.source_id
                == entity_id
                or
                relationship.target_id
                == entity_id
            )
        ]

    # =====================================
    # SERIALIZATION
    # =====================================

    def to_dict(self) -> dict:

        return {
            "entities": [
                {
                    "id": entity.id,
                    "type": entity.entity_type,
                    "properties": (
                        entity.properties
                    ),
                }
                for entity in self.entities.values()
            ],
            "relationships": [
                {
                    "source": (
                        relationship.source_id
                    ),
                    "type": (
                        relationship.relationship_type
                    ),
                    "target": (
                        relationship.target_id
                    ),
                    "properties": (
                        relationship.properties
                    ),
                }
                for relationship
                in self.relationships
            ],
        }