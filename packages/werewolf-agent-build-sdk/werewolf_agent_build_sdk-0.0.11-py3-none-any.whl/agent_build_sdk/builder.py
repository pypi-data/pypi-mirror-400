
from agent_build_sdk.sdk.agent import BasicAgent
from agent_build_sdk.server.server import EndpointServer



class AgentBuilder:

    def __init__(self, name: str, agent: BasicAgent):
        self.name = name
        self.agent = agent

    def start(self):
        server = EndpointServer(self.agent)
        server.start()
