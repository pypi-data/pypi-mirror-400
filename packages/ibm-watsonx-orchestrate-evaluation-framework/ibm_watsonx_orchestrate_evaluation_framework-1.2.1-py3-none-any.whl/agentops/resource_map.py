from collections import defaultdict

from pydantic import BaseModel

from agentops.utils.utils import is_saas_url
from agentops.wxo_client import WXOClient


class AgentData(BaseModel):
    agent_name: str
    id: str
    tools: list[str]
    collaborators: list[str]
    is_manager: bool = False


class ResourceMap:
    def __init__(self, wxo_client: WXOClient):
        self.wxo_client = wxo_client
        self.agent2tools, self.tools2agents = self.init_mapping()
        self.all_agents = list(self.agent2tools.keys())

    def init_mapping(self):
        agent2tools = defaultdict(set)
        tools2agents = defaultdict(set)
        agents_data: dict[str, AgentData] = {}
        if is_saas_url(self.wxo_client.service_url):
            # TO-DO: this is not validated after the v1 prefix change
            # need additional validation
            tools_path = "v1/orchestrate/tools"
            agents_path = "v1/orchestrate/agents"
        else:
            tools_path = "v1/tools/"
            agents_path = "v1/orchestrate/agents/"

        # id : tool name
        tool_id2name = {}

        resp = self.wxo_client.get(tools_path)
        if resp.status_code == 200:
            tools = resp.json()
            tool_id2name = {tool["id"]: tool["name"] for tool in tools}
        else:
            resp.raise_for_status()

        resp = self.wxo_client.get(agents_path)

        agent_id2name = {}
        if resp.status_code == 200:
            agents: list[dict] = resp.json()

            self.all_agent_objs = agents

            agent_id2name = {agent["id"]: agent["name"] for agent in agents}

            for agent in agents:
                agent_name = agent["name"]
                agent_tools = [tool_id2name[id] for id in agent["tools"]]
                # only get collaborator names that are retrievable
                collaborators = [
                    agent_id2name.get(id)
                    for id in agent["collaborators"]
                    if agent_id2name.get(id) is not None
                ]

                for tool in agent_tools:
                    agent2tools[agent_name].add(tool)
                    tools2agents[tool].add(agent_name)

                agents_data[agent_name] = AgentData(
                    agent_name=agent_name,
                    id=agent.get("id", ""),
                    tools=agent_tools,
                    collaborators=collaborators,
                    is_manager=(len(agent_tools) == 0),
                )
        else:
            resp.raise_for_status()

        self.agent_data = agents_data

        agent2tools = dict(agent2tools)
        tools2agents = dict(tools2agents)
        return agent2tools, tools2agents
