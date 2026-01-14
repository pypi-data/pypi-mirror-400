"""Default Agent."""

import logging
from typing import Literal

from langchain_mcp_adapters.client import (
    MultiServerMCPClient,
    SSEConnection,
    StdioConnection,
    StreamableHttpConnection,
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.base import BaseStore

from axmp_ai_agent_core.agent.base_agent import AxmpBaseAgent
from axmp_ai_agent_core.agent.util.load_chat_model import load_chat_model
from axmp_ai_agent_core.agent.util.mcp_client_manager import (
    MultiServerMCPClientManager,
)
from axmp_ai_agent_core.setting import core_settings

logger = logging.getLogger(__name__)


class DefaultAgent(AxmpBaseAgent):
    """Default Agent."""

    def __init__(
        self,
        *,
        provider: str | None = None,
        default_model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        chat_memory_type: Literal["POSTGRESQL", "REDIS"] = None,
        chat_memory_uri: str = None,
        memory: MemorySaver | None = None,
        store: BaseStore | None = None,
        connections: dict[
            str, StdioConnection | SSEConnection | StreamableHttpConnection
        ]
        | None = None,
        system_instruction: str | None = None,
        mcp_client_manager: MultiServerMCPClientManager | None = None,
    ):
        """Initialize the DefaultAgent."""
        # Call parent constructor first
        super().__init__()

        # Initialize child-specific attributes
        provier_and_model = None
        if provider and default_model:
            provier_and_model = f"{provider}/{default_model}"
        else:
            provier_and_model = core_settings.default_model

        self.api_key = api_key
        self.base_url = base_url
        self.model = load_chat_model(
            fully_specified_name=provier_and_model,
            api_key=api_key,
            base_url=base_url,
        )
        self.chat_memory_type = chat_memory_type
        self.chat_memory_uri = chat_memory_uri
        self.memory = memory
        self.store = store
        self.agent_name = "Default-Agent"
        self.prompt_path = "prompts/default_template.yaml"
        self.system_instruction = system_instruction or None
        self.mcp_client_manager = mcp_client_manager
        self.connections = connections

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
            if self.mcp_client_manager is None:
                client = MultiServerMCPClient(self.connections)
                self.tools = await client.get_tools()
            else:
                self.tools = await self.mcp_client_manager.get_tools()

            if self.memory is None:
                if self.chat_memory_type is None and self.chat_memory_uri is None:
                    self.memory = MemorySaver()
                # NOTE: this logic is not working as expected because the contextmanager issue
                elif (
                    self.chat_memory_type is not None
                    and self.chat_memory_uri is not None
                ):
                    if self.chat_memory_type == "POSTGRESQL":
                        checkpointer_context_manager = (
                            AsyncPostgresSaver.from_conn_string(self.chat_memory_uri)
                        )
                        checkpointer = await checkpointer_context_manager.__aenter__()
                        await checkpointer.setup()
                        self.memory = checkpointer
                    elif self.chat_memory_type == "REDIS":
                        # self.memory = RedisSaver(
                        #     url=self.chat_memory_uri,
                        #     namespace=self.agent_name,
                        # )
                        raise ValueError("Redis chat memory is not supported yet")
                    else:
                        raise ValueError(
                            f"Unsupported chat memory type: {self.chat_memory_type}"
                        )
                else:
                    raise ValueError("Chat memory type and URI are required")

            self.agent = await self._create_agent()
            self._initialized = True

            logger.info(f"Initialized {self.agent_name} with {len(self.tools)} tools")

    async def cleanup(self) -> None:
        """Cleanup the graph."""
        if self.memory is not None:
            await self.memory.__aexit__(None, None, None)
