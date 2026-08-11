from .base import Agent, AgentInput, AgentOutput


class EnrichmentAgent(Agent):

    name = "enrichment_agent"

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

        canonical_product = input.context.get(
            "canonical_product",
            {}
        )

        sources = input.context.get(
            "sources",
            []
        )

        # -----------------------------------
        # Extract canonical information
        # -----------------------------------

        family_specifications = (
            canonical_product.get(
                "family_specifications",
                {}
            )
        )

        variants = canonical_product.get(
            "variants",
            []
        )

        # -----------------------------------
        # Build deterministic enrichment
        # -----------------------------------
        #
        # For MVP, start without an LLM.
        # We will plug the LLM in after
        # verifying the data flow.
        #

        title = (
            f"{manufacturer} "
            f"{mpn} "
            f"Industrial Product"
        )

        technical_summary = {}

        for field, specification in (
            family_specifications.items()
        ):

            technical_summary[field] = (
                specification.get(
                    "value"
                )
            )

            unit = specification.get(
                "unit"
            )

            if unit:
                technical_summary[field] = (
                    f"{specification.get('value')} "
                    f"{unit}"
                )

        # -----------------------------------
        # Build enrichment result
        # -----------------------------------

        enrichment = {

            "title": title,

            "short_description": (
                f"{manufacturer} {mpn} "
                "industrial electrical product."
            ),

            "features": [],

            "applications": [],

            "search_keywords": [
                manufacturer,
                mpn,
                "industrial electrical",
            ],

            "technical_summary": (
                technical_summary
            ),

            "variants": variants,

            "source_count": len(sources),
        }

        return AgentOutput(
            success=True,
            data={
                "enrichment": enrichment
            },
        )