from .base import Agent, AgentInput, AgentOutput


class ProductIntelligenceAgent(Agent):

    name = "product_intelligence_agent"

    async def run(
        self,
        input: AgentInput
    ) -> AgentOutput:

        # -----------------------------------
        # Basic product information
        # -----------------------------------

        manufacturer = input.context.get(
            "manufacturer"
        )

        mpn = input.context.get(
            "mpn"
        )

        # -----------------------------------
        # Canonical product
        # -----------------------------------

        canonical_product = input.context.get(
            "canonical_product",
            {}
        )

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

        quality = canonical_product.get(
            "quality",
            {}
        )

        # -----------------------------------
        # Knowledge graph
        # -----------------------------------

        knowledge_graph = input.context.get(
            "knowledge_graph",
            {}
        )

        # -----------------------------------
        # Conflict resolutions
        # -----------------------------------

        conflict_resolutions = input.context.get(
            "conflict_resolutions",
            []
        )

        # -----------------------------------
        # Build final product intelligence
        # -----------------------------------

        product_intelligence = {

            "manufacturer": manufacturer,

            "mpn": mpn,

            "product_category": (
                "industrial_electrical"
            ),

            "family_specifications": (
                family_specifications
            ),

            "variants": variants,

            "knowledge_graph": (
                knowledge_graph
            ),

            "conflict_resolutions": (
                conflict_resolutions
            ),

            "quality": quality,

            "commerce_readiness": {
                "status": (
                    "review_required"
                    if quality.get(
                        "human_review_required",
                        False
                    )
                    else "ready"
                )
            },
        }

        # -----------------------------------
        # Return
        # -----------------------------------

        return AgentOutput(
            success=True,
            data={
                "product_intelligence": (
                    product_intelligence
                )
            },
        )