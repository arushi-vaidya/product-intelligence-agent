from .base import Agent, AgentInput, AgentOutput

from app.knowledge.entities import (
    Entity,
    Relationship,
)

from app.knowledge.graph import (
    KnowledgeGraph,
)


class AKGPAgent(Agent):

    name = "akgp_agent"

    async def run(
        self,
        input: AgentInput
    ) -> AgentOutput:

        manufacturer = input.context.get(
            "manufacturer"
        )

        mpn = input.context.get(
            "mpn"
        )

        specifications = input.context.get(
            "specifications",
            {}
        )

        conflicts = input.context.get(
            "conflicts",
            []
        )
        
        sources = input.context.get(
            "sources",
            []
        )

        evidence = self._collect_evidence(
            specifications
        )

        graph = KnowledgeGraph()

        # =====================================
        # MANUFACTURER
        # =====================================

        manufacturer_id = (
            f"manufacturer:{manufacturer}"
        )

        graph.add_entity(
            Entity(
                id=manufacturer_id,
                entity_type="Manufacturer",
                properties={
                    "name": manufacturer
                },
            )
        )

        # =====================================
        # PRODUCT FAMILY
        # =====================================

        family_id = (
            f"family:{manufacturer}:{mpn}"
        )

        graph.add_entity(
            Entity(
                id=family_id,
                entity_type="ProductFamily",
                properties={
                    "name": mpn,
                    "manufacturer": manufacturer,
                },
            )
        )

        graph.add_relationship(
            Relationship(
                source_id=manufacturer_id,
                relationship_type="MANUFACTURES",
                target_id=family_id,
            )
        )

        # =====================================
        # IDENTIFY PRODUCT VARIANTS
        # =====================================

        variants = self._identify_variants(
            evidence,
            sources
        )

        for variant in variants:

            variant_id = (
                f"variant:"
                f"{manufacturer}:"
                f"{variant['mpn']}"
            )

            graph.add_entity(
                Entity(
                    id=variant_id,
                    entity_type="ProductVariant",
                    properties={
                        "mpn": variant["mpn"],
                        "manufacturer": (
                            manufacturer
                        ),
                        "specifications": (
                            variant[
                                "specifications"
                            ]
                        ),
                    },
                )
            )

            graph.add_relationship(
                Relationship(
                    source_id=family_id,
                    relationship_type=(
                        "HAS_VARIANT"
                    ),
                    target_id=variant_id,
                )
            )

        # =====================================
        # RESOLVE CONFLICTS
        # =====================================

        resolutions = []

        for conflict in conflicts:

            resolution = (
                self._resolve_conflict(
                    conflict,
                    variants,
                )
            )

            resolutions.append(
                resolution
            )

        # =====================================
        # RETURN
        # =====================================

        return AgentOutput(
            success=True,
            data={
                "knowledge_graph": (
                    graph.to_dict()
                ),
                "variants": variants,
                "conflict_resolutions": (
                    resolutions
                ),
            },
        )

    # =====================================
    # EVIDENCE
    # =====================================

    def _collect_evidence(
        self,
        specifications,
    ):

        evidence = []

        for field, specification in (
            specifications.items()
        ):

            for item in specification.get(
                "evidence",
                []
            ):

                evidence.append(
                    {
                        "field": field,
                        "value": item.get(
                            "value"
                        ),
                        "source_id": item.get(
                            "source_id"
                        ),
                        "text": item.get(
                            "text"
                        ),
                    }
                )

        return evidence

    # =====================================
    # VARIANT IDENTIFICATION
    # =====================================

    def _identify_variants(
        self,
        evidence,
        sources,
    ):

        source_map = {
            source.get("id"): source
            for source in sources
        }

        variants = {}

        for item in evidence:

            source_id = item.get(
                "source_id"
            )

            source = source_map.get(
                source_id
            )

            if not source:
                continue

            variant_mpn = (
                self._extract_source_mpn(
                    source
                )
            )

            if not variant_mpn:
                continue

            if variant_mpn not in variants:

                variants[
                    variant_mpn
                ] = {
                    "mpn": variant_mpn,
                    "specifications": {},
                    "sources": [],
                }

            field = item.get(
                "field"
            )

            value = item.get(
                "value"
            )

            variants[
                variant_mpn
            ]["specifications"][
                field
            ] = value

            if source_id not in (
                variants[
                    variant_mpn
                ]["sources"]
            ):

                variants[
                    variant_mpn
                ]["sources"
                ].append(
                    source_id
                )

        return list(
            variants.values()
        )

    # =====================================
    # MPN EXTRACTION
    # =====================================

    def _extract_source_mpn(
        self,
        source: dict,
    ) -> str | None:

        import re

        text = " ".join([
            source.get("title", ""),
            source.get("snippet", ""),
            source.get("url", ""),
        ])

        match = re.search(
            r"\bA9F\d{5}\b",
            text,
            re.IGNORECASE,
        )

        if not match:
            return None

        return match.group(0).upper()

    # =====================================
    # CONFLICT RESOLUTION
    # =====================================

    def _resolve_conflict(
        self,
        conflict,
        variants,
    ):

        field = conflict.get(
            "field"
        )

        values = conflict.get(
            "values",
            []
        )

        variant_values = []

        for variant in variants:

            value = variant.get(
                "specifications",
                {}
            ).get(field)

            if value:

                variant_values.append(
                    {
                        "mpn": variant[
                            "mpn"
                        ],
                        "value": value,
                    }
                )

        if len(variant_values) > 1:

            return {
                "field": field,
                "status": (
                    "variant_difference"
                ),
                "explanation": (
                    "The conflicting values "
                    "appear to belong to "
                    "different product variants."
                ),
                "variants": (
                    variant_values
                ),
                "requires_human_review": False,
            }

        return {
            "field": field,
            "status": "unresolved",
            "original_conflict": values,
            "requires_human_review": True,
        }