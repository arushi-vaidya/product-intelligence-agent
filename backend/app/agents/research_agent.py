from .base import Agent, AgentInput, AgentOutput
from app.services.source_filter import SourceFilter
from app.services.source_discovery import (
    SourceDiscoveryService
)


class ResearchAgent(Agent):

    name = "research_agent"

    def __init__(self):

        self.source_discovery = (
            SourceDiscoveryService()
        )

        self.source_filter = SourceFilter()

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

        # -------------------------------
        # Search
        # -------------------------------

        raw_sources = await (
            self.source_discovery.search_product(
                manufacturer=manufacturer,
                mpn=mpn,
            )
        )

        print(
            f"[RESEARCH] Raw sources found: "
            f"{len(raw_sources)}"
        )

        # -------------------------------
        # Filter
        # -------------------------------

        sources = self.source_filter.filter_sources(
            sources=raw_sources,
            manufacturer=manufacturer,
            mpn=mpn,
        )

        print(
            f"[RESEARCH] Sources after filtering: "
            f"{len(sources)}"
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