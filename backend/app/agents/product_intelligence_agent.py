from .base import Agent, AgentInput, AgentOutput


class ProductIntelligenceAgent(Agent):

    name = "product_intelligence_agent"

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

        knowledge_graph = input.context.get(
            "knowledge_graph",
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
        # Build normalized specifications
        # -----------------------------------

        normalized_specs = {}

        for field, specification in specifications.items():

            normalized_specs[field] = {
                "value": specification.get("value"),
                "unit": specification.get("unit"),
                "confidence": specification.get(
                    "confidence"
                ),
                "quality_status": specification.get(
                    "quality_status",
                    "unknown"
                ),
            }

        # -----------------------------------
        # Determine human review requirement
        # -----------------------------------

        human_review_required = any(
            resolution.get(
                "requires_human_review",
                False
            )
            for resolution in conflict_resolutions
        )

        # -----------------------------------
        # Calculate overall confidence
        # -----------------------------------

        confidence_values = [
            spec.get("confidence")
            for spec in specifications.values()
            if spec.get("confidence") is not None
        ]

        if confidence_values:
            overall_confidence = round(
                sum(confidence_values)
                / len(confidence_values),
                2
            )
        else:
            overall_confidence = 0.0

        # -----------------------------------
        # Build final product intelligence
        # -----------------------------------

        product_intelligence = {

            "manufacturer": manufacturer,

            "mpn": mpn,

            "product_category": (
                "industrial_electrical"
            ),

            "specifications": normalized_specs,

            "variants": variants,

            "knowledge_graph": knowledge_graph,

            "conflict_resolutions": (
                conflict_resolutions
            ),

            "quality": {
                "overall_confidence": (
                    overall_confidence
                ),
                "human_review_required": (
                    human_review_required
                ),
            },

            "commerce_readiness": {
                "status": (
                    "review_required"
                    if human_review_required
                    else "ready"
                )
            },
        }

        return AgentOutput(
            success=True,
            data={
                "product_intelligence": (
                    product_intelligence
                )
            },
        )