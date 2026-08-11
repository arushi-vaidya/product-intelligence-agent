from abc import ABC, abstractmethod
from pydantic import BaseModel


class AgentInput(BaseModel):
    investigation_id: str
    context: dict


class AgentOutput(BaseModel):
    success: bool
    data: dict
    errors: list[str] = []


class Agent(ABC):

    name: str

    @abstractmethod
    async def run(self, input: AgentInput) -> AgentOutput:
        pass