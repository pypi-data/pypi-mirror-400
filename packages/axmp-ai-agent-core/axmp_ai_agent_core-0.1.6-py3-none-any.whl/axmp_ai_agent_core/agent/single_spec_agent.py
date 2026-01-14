"""Single Specification Agent."""

import logging

from axmp_ai_agent_spec.profile_node_data import AgentData, LLMModelData, McpServerData
from axmp_ai_agent_spec.profiles.single_agent_profile import (
    NodeOfSingleAgent,
    SingleAgentProfile,
)
from axmp_ai_agent_spec.types import NodeType
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.base import BaseStore

from axmp_ai_agent_core.agent.base_agent import AxmpBaseAgent
from axmp_ai_agent_core.agent.util.mcp_client_manager import MultiServerMCPClientManager

logger = logging.getLogger(__name__)


class SingleSpecAgent(AxmpBaseAgent):
    """Single Specification Agent."""

    def __init__(
        self,
        *,
        memory: MemorySaver,
        store: BaseStore,
        specification: SingleAgentProfile,
    ):
        """Initialize the SingleSpecAgent."""
        # Call parent constructor first
        super().__init__()

        # Initialize child-specific attributes
        self.memory = memory
        self.store = store
        self.specification = specification

    async def initialize(
        self,
    ) -> None:
        """Initialize the graph."""
        if self._initialized:
            if self.agent:
                return
            else:
                raise Exception("Initialized is True but Graph is not initialized")

        if not self.agent:
            self.agent_name = f"Single-Agent-{self.specification.system_name}"
            self.connections = {}

            flow = self.specification.flow
            if flow is None:
                raise ValueError("Flow is not found")

            nodes: list[NodeOfSingleAgent] = flow.nodes
            if nodes is None:
                raise ValueError("Nodes are not found")

            for node in nodes:
                if node.type == NodeType.TRIGGER:
                    # TODO: implement the init message of the trigger node
                    pass
                elif node.type == NodeType.AI_AGENT:
                    agent_data: AgentData = node.data
                    self.system_instruction = agent_data.system_prompt
                elif node.type == NodeType.LLM:
                    llm_data: LLMModelData = node.data
                    self.api_key = llm_data.api_key or None
                    self.aws_access_key_id = llm_data.aws_access_key_id or None
                    self.aws_secret_access_key = llm_data.aws_secret_access_key or None
                    self.aws_region_name = llm_data.aws_region_name or None
                    self.base_url = llm_data.base_url or None
                    self.provider_and_model = (
                        f"{llm_data.provider}:{llm_data.default_model_id}"
                    )
                    self.temperature = llm_data.temperature
                    self.max_tokens = llm_data.max_tokens
                elif node.type == NodeType.MEMORY:
                    # NOTE: Don't anything for the memory node because the workspace will use the common checkpointer
                    pass
                elif node.type == NodeType.MCP_SERVER:
                    mcp_server_data: McpServerData = node.data
                    mcp_connection = mcp_server_data.config
                    if not mcp_connection:
                        raise ValueError("The MCP server doesn't have configuration")
                    # server_name, connection = mcp_connection.popitem()
                    server_name = next(iter(mcp_connection))
                    connection = mcp_connection[server_name]
                    self.connections[server_name] = connection
                    logger.info(f"MCP server: {server_name}, connection:\n{connection}")
                else:
                    raise ValueError(f"Invalid node type: {node.type}")

            mcp_client_manager = await MultiServerMCPClientManager.initialize()
            await mcp_client_manager.add_mcp_servers(self.connections)
            self.mcp_servers = await mcp_client_manager.get_mcp_servers()
            self.tools = await mcp_client_manager.get_tools()

            self.agent = await self._create_agent()
            self._initialized = True

            logger.info(f"Initialized {self.agent_name} with {len(self.tools)} tools")

    async def cleanup(self) -> None:
        """Cleanup the graph."""
        if self.memory is not None:
            # await self.memory.__aexit__(None, None, None)
            pass
