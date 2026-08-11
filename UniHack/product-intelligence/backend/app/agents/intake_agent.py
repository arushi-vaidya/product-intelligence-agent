from .base import Agent, AgentInput, AgentOutput


class IntakeAgent(Agent):

    name = "intake_agent"

    async def run(self, input: AgentInput) -> AgentOutput:

        raw_product = input.context.get("product", {})

        manufacturer = raw_product.get("manufacturer")
        mpn = raw_product.get("mpn")

        if not manufacturer or not mpn:
            return AgentOutput(
                success=False,
                data={},
                errors=["Manufacturer and MPN are required"]
            )

        return AgentOutput(
            success=True,
            data={
                "manufacturer": manufacturer,
                "mpn": mpn,
                "category_guess": "industrial_electrical"
            }
        )