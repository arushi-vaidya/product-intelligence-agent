from .base import Agent, AgentInput, AgentOutput


class ResearchAgent(Agent):

    name = "research_agent"

    async def run(
        self,
        input: AgentInput
    ) -> AgentOutput:

        # IntakeAgent output is passed directly
        # as the context to ResearchAgent.
        manufacturer = input.context.get("manufacturer")
        mpn = input.context.get("mpn")
        category = input.context.get("category_guess")

        if not manufacturer or not mpn:
            return AgentOutput(
                success=False,
                data={},
                errors=[
                    "Manufacturer and MPN are required"
                ]
            )

        # Mock sources for now.
        # We will replace these with real web research later.
        sources = [
            {
                "id": "mock_manufacturer_page",
                "url": "https://example.com/product",
                "source_type": "manufacturer_page",
                "authority_tier": 1,
                "title": f"{manufacturer} {mpn} Product Page"
            },
            {
                "id": "mock_datasheet",
                "url": "https://example.com/datasheet.pdf",
                "source_type": "manufacturer_datasheet",
                "authority_tier": 1,
                "title": f"{manufacturer} {mpn} Datasheet"
            }
        ]

        return AgentOutput(
            success=True,
            data={
                "product": {
                    "manufacturer": manufacturer,
                    "mpn": mpn,
                    "category": category
                },
                "sources": sources
            }
        )