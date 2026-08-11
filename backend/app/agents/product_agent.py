from .base import Agent, AgentInput, AgentOutput


class ProductAgent(Agent):

    name = "product_agent"

    async def run(self, input: AgentInput) -> AgentOutput:

        return AgentOutput(
            success=True,
            data={
                "product": {}
            }
        )