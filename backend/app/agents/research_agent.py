from .base import Agent, AgentInput, AgentOutput
from app.services.source_discovery import (
    SourceDiscoveryService
)


class ResearchAgent(Agent):

    name = "research_agent"

    def __init__(self):

        self.source_discovery = (
            SourceDiscoveryService()
        )

    async def run(
        self,
        input: AgentInput
    ) -> AgentOutput:

        manufacturer = (
            input.context.get("manufacturer")
        )

        mpn = (
            input.context.get("mpn")
        )

        category = (
            input.context.get("category_guess")
        )

        if not manufacturer or not mpn:

            return AgentOutput(
                success=False,
                data={},
                errors=[
                    "Manufacturer and MPN are required"
                ]
            )

        print(
            f"[RESEARCH] Researching "
            f"{manufacturer} {mpn}"
        )

        # Ask the source discovery service
        # to find relevant sources.

        sources = await (
            self.source_discovery.search_product(
                manufacturer=manufacturer,
                mpn=mpn,
            )
        )

        return AgentOutput(
            success=True,
            data={
                "product": {
                    "manufacturer": manufacturer,
                    "mpn": mpn,
                    "category": category,
                },
                "sources": sources,
            }
        )