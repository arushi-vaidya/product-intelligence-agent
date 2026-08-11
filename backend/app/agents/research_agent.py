from .base import Agent, AgentInput, AgentOutput


class ResearchAgent(Agent):

    name = "research_agent"

    async def run(self, input: AgentInput) -> AgentOutput:

        return AgentOutput(
            success=True,
            data={
                "sources": []
            }
        )