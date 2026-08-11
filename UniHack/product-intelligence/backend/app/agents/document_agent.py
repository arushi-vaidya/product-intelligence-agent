from .base import Agent, AgentInput, AgentOutput


class DocumentAgent(Agent):

    name = "document_agent"

    async def run(self, input: AgentInput) -> AgentOutput:

        return AgentOutput(
            success=True,
            data={
                "evidence": []
            }
        )