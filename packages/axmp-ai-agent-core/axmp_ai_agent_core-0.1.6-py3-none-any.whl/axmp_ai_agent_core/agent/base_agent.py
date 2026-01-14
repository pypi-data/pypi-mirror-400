"""AlertAgent - a specialized assistant for alert management."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import (
    SSEConnection,
    StdioConnection,
    StreamableHttpConnection,
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore

from axmp_ai_agent_core.agent.langgraph_react_agent import create_langgraph_agent
from axmp_ai_agent_core.agent.util.mcp_client_manager import McpServer

logger = logging.getLogger(__name__)


class AxmpBaseAgent(ABC):
    """AxmpBaseAgent - a specialized assistant for Axmp AI platform."""

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        """Initialize the AxmpBaseAgent."""
        self.provider_and_model: str = None
        self.base_url: str = None
        self.temperature: float = 0.0
        self.max_tokens: int = 5000
        self.memory: MemorySaver = None
        self.store: BaseStore = None
        self.agent: CompiledStateGraph = None
        self.tools: list[BaseTool] = None
        self.agent_name: str = None
        self.prompt_path: str = "prompts/default_template.yaml"
        self.system_instruction: str = None
        self.connections: dict[
            str, StdioConnection | SSEConnection | StreamableHttpConnection
        ] = None
        self.api_key: str | None = None
        self.aws_access_key_id: str | None = None
        self.aws_secret_access_key: str | None = None
        self.aws_region_name: str | None = None
        self.mcp_servers: list[McpServer] = []
        self._initialized = False

    @abstractmethod
    async def initialize(
        self,
        connections: dict[
            str, StdioConnection | SSEConnection | StreamableHttpConnection
        ],
    ) -> None:
        """Initialize the AxmpBaseAgent."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup the AxmpBaseAgent."""
        pass

    def get_tools(self) -> list[BaseTool]:
        """Get the agent tools."""
        if not self._initialized:
            raise ValueError("Agent not initialized")

        return self.tools

    def _create_agent(self) -> CompiledStateGraph:
        """Create the langgraph agent with the flexibile prompt and llm model."""
        return create_langgraph_agent(
            tools=self.tools,
            checkpointer=self.memory,
            store=self.store,
            agent_name=self.agent_name,
            prompt_path=self.prompt_path,
            system_message=self.system_instruction,
            base_url=self.base_url,
            api_key=self.api_key,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_region_name=self.aws_region_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
