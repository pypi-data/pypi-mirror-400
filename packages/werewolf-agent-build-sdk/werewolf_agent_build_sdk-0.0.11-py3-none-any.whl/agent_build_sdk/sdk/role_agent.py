import os

from abc import ABC, abstractmethod
from agent_build_sdk.memory.memory import SimpleMemory
from agent_build_sdk.model.werewolf_model import AgentReq, AgentResp
from openai import OpenAI

class BasicRoleAgent(ABC):

    def __init__(self, role, memory=SimpleMemory(), model_name='gpt4-4o-mini'):
        """

        :param name: 智能体的名字
        :param memory: memory
        """
        self.role = role
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

    def llm_caller(self, prompt):
        client = OpenAI(
            api_key=os.getenv('API_KEY'),
            base_url=os.getenv('BASE_URL')
        )
        completion = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': prompt}
            ],
            temperature=0
        )
        try:
            return completion.choices[0].message.content
        except Exception as e:
            print(e)
            return None

