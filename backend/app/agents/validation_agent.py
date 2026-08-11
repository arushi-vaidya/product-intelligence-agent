from .base import Agent, AgentInput, AgentOutput


class ValidationAgent(Agent):

    name = "validation_agent"

    async def run(self, input: AgentInput) -> AgentOutput:

        return AgentOutput(
            success=True,
            data={
                "validated": False
            }
        )