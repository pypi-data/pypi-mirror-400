from abc import ABC

from langchain import PromptTemplate
from agent_build_sdk.memory.memory import SimpleMemory
from agent_build_sdk.model.werewolf_model import AgentReq, AgentResp
from agent_build_sdk.sdk.agent import BasicAgent
from agent_build_sdk.utils.logger import logger


def format_prompt(prompt_template: str, variables: dict) -> str:
    pt = PromptTemplate(template=prompt_template, input_variables=list(variables.keys()))
    return pt.format(**variables)


class WerewolfAgent(BasicAgent):

    def __init__(self, name, memory=SimpleMemory(), model_name='gpt4-4o-mini'):
        """

        :param name: 智能体的名字
        :param memory: memory
        """
        super().__init__(name, memory, model_name)
        self.name = name
        self.memory = memory
        self.model_name = model_name
        self.role_agent_map = {}

    def register_role_agent(self, role, role_agent):
        """Register a role agent."""
        self.role_agent_map[role] = role_agent

    def perceive(
            self,
            req=AgentReq,
    ):
        """Run perceive."""
        logger.info(f"Perceive: {req}")
        role_name = req.role
        if role_name not in self.role_agent_map:
            raise ValueError(f"Role agent for {role_name} not registered.")
        return self.role_agent_map[role_name].perceive(req)

    def interact(
            self,
            req=AgentReq,
    ) -> AgentResp:
        """Run interact."""
        logger.info(f"interact: {req}")
        role_name = req.role
        if role_name not in self.role_agent_map:
            raise ValueError(f"Role agent for {role_name} not registered.")
        return self.role_agent_map[role_name].interact(req)
