from .base import Agent, AgentInput, AgentOutput


class CanonicalResolutionAgent(Agent):

    name = "canonical_resolution_agent"

    async def run(
        self,
        input: AgentInput
    ) -> AgentOutput:

        specifications = input.context.get(
            "specifications",
            {}
        )

        variants = input.context.get(
            "variants",
            []
        )

        conflict_resolutions = input.context.get(
            "conflict_resolutions",
            []
        )

        # -----------------------------------
        # Family-level specifications
        # -----------------------------------

        family_specifications = {}

        # -----------------------------------
        # Variant-level specifications
        # -----------------------------------

        variant_specifications = {}

        # Start with specifications that
        # are already consistent.
        for field, specification in specifications.items():

            status = specification.get(
                "quality_status"
            )

            if status == "consistent":

                family_specifications[field] = {
                    "value": specification.get(
                        "value"
                    ),
                    "unit": specification.get(
                        "unit"
                    ),
                    "confidence": specification.get(
                        "confidence"
                    ),
                }

        # -----------------------------------
        # Move conflict fields to variants
        # -----------------------------------

        conflict_fields = {
            conflict.get("field")
            for conflict in conflict_resolutions
            if conflict.get("status")
            == "variant_difference"
        }

        for variant in variants:

            variant_mpn = variant.get(
                "mpn"
            )

            if not variant_mpn:
                continue

            variant_specifications[
                variant_mpn
            ] = {}

            for field, value in (
                variant.get(
                    "specifications",
                    {}
                ).items()
            ):

                if field in conflict_fields:

                    variant_specifications[
                        variant_mpn
                    ][field] = value

        # -----------------------------------
        # Build canonical variants
        # -----------------------------------

        canonical_variants = []

        for variant in variants:

            variant_mpn = variant.get(
                "mpn"
            )

            if not variant_mpn:
                continue

            canonical_variants.append(
                {
                    "mpn": variant_mpn,
                    "specifications": (
                        variant_specifications.get(
                            variant_mpn,
                            {}
                        )
                    ),
                    "sources": variant.get(
                        "sources",
                        []
                    ),
                }
            )

        # -----------------------------------
        # Determine review status
        # -----------------------------------

        unresolved_conflicts = [
            conflict
            for conflict in conflict_resolutions
            if conflict.get(
                "requires_human_review",
                False
            )
        ]

        human_review_required = (
            len(unresolved_conflicts) > 0
        )

        # -----------------------------------
        # Final canonical object
        # -----------------------------------

        canonical_product = {

            "family_specifications":
                family_specifications,

            "variants":
                canonical_variants,

            "quality": {

                "human_review_required":
                    human_review_required,

                "unresolved_conflicts":
                    unresolved_conflicts,
            },
        }

        return AgentOutput(
            success=True,
            data={
                "canonical_product":
                    canonical_product
            },
        )