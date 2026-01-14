from abc import ABC, abstractmethod

from langchain import PromptTemplate
from agent_build_sdk.memory.memory import SimpleMemory
from agent_build_sdk.model.model import AgentReq, AgentResp


def format_prompt(prompt_template: str, variables: dict) -> str:
    pt = PromptTemplate(template=prompt_template, input_variables=list(variables.keys()))
    return pt.format(**variables)


class BasicAgent(ABC):

    def __init__(self, name, memory=SimpleMemory(), model_name='gpt4-4o-mini'):
        """

        :param name: 智能体的名字
        :param memory: memory
        """
        self.name = name
        self.memory = memory
        self.model_name = model_name

    @abstractmethod
    def perceive(
            self,
            req=AgentReq,
    ):
        """Run perceive."""

    @abstractmethod
    def interact(
            self,
            req=AgentReq,
    ) -> AgentResp:
        """Run interact."""
