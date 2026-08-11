import uuid

from app.agents.base import AgentInput
from app.agents.intake_agent import IntakeAgent


class DFOO:

    def __init__(self):
        self.agents = {
            "intake_agent": IntakeAgent(),
        }

    async def start_investigation(self, product: dict):

        investigation_id = str(uuid.uuid4())

        agent = self.agents["intake_agent"]

        result = await agent.run(
            AgentInput(
                investigation_id=investigation_id,
                context={
                    "product": product
                }
            )
        )

        return {
            "investigation_id": investigation_id,
            "result": result
        }