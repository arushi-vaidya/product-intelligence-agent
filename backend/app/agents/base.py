from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class AgentInput(BaseModel):

    investigation_id: str

    context: dict = Field(
        default_factory=dict
    )


class AgentOutput(BaseModel):

    success: bool

    data: dict = Field(
        default_factory=dict
    )

    errors: list[str] = Field(
        default_factory=list
    )


class Agent(ABC):

    name: str

    @abstractmethod
    async def run(
        self,
        input: AgentInput
    ) -> AgentOutput:
        pass