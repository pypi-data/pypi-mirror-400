"""ZMP MCP client manager."""

from __future__ import annotations

import asyncio
import logging

from axmp_ai_agent_spec.types import MCPServerType, TransportType
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import (
    MultiServerMCPClient,
    SSEConnection,
    StdioConnection,
    StreamableHttpConnection,
)
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class McpServer(BaseModel):
    """MCP server."""

    server_name: str = Field(..., description="The name of the MCP server")
    connected: bool = Field(False, description="Whether the server is connected")
    tools: list[BaseTool] = Field(
        default_factory=list, description="List of tools available from this server"
    )

    # for the frontend to display the MCP servers (registry_id, icon_url, resource_type, transport_type)
    registry_id: str | None = Field(
        default=None, description="The registry id of the MCP server"
    )
    resource_type: MCPServerType | None = Field(
        default=None, description="The resource type of the MCP server"
    )
    transport_type: TransportType | None = Field(
        default=None, description="The transport type of the MCP server"
    )
    icon_url: str | None = Field(
        default=None, description="The icon url of the MCP server"
    )


class MultiServerMCPClientManager:
    """Multi server MCP client manager."""

    def __init__(self):
        """Initialize the Multi server MCP client manager."""
        self.connections: dict[
            str, StdioConnection | SSEConnection | StreamableHttpConnection
        ] = {}
        self.client: MultiServerMCPClient | None = None
        self.mcp_servers: list[McpServer] = []
        self.tools: list[BaseTool] = []

    @classmethod
    async def initialize(cls) -> MultiServerMCPClientManager:
        """Initialize the Multi server MCP client manager."""
        return cls()

    async def add_mcp_servers(
        self,
        connections: dict[
            str, StdioConnection | SSEConnection | StreamableHttpConnection
        ],
    ) -> None:
        """Add MCP servers."""
        new_servers: list[str] = []
        if self.connections is not None and len(self.connections.items()) > 0:
            # If the connections are not empty, we need to add only the new servers
            new_servers = list(set(connections.keys()) - set(self.connections.keys()))
        else:
            new_servers = list(connections.keys())

        for server_name in new_servers:
            self.connections[server_name] = connections[server_name]

        self.client = MultiServerMCPClient(connections=self.connections)
        await self._initialize_tools()

    async def add_mcp_server(
        self,
        server_name: str,
        connection: StdioConnection | SSEConnection | StreamableHttpConnection,
    ) -> None:
        """Add a MCP server."""
        if server_name in self.connections:
            raise ValueError(f"MCP server {server_name} already exists")

        self.connections[server_name] = connection
        self.client = MultiServerMCPClient(connections=self.connections)
        await self._initialize_tools()

    async def get_mcp_servers(self) -> list[McpServer]:
        """Get the MCP servers."""
        return self.mcp_servers

    async def _initialize_tools(self) -> None:
        """Initialize the tools."""
        # Reset the tools and server name to tools
        self.tools = []
        self.mcp_servers = []

        load_mcp_tool_tasks = []
        server_names = list(self.connections.keys())

        for server_name in server_names:
            load_mcp_tool_task = asyncio.create_task(
                self.client.get_tools(server_name=server_name)
            )
            load_mcp_tool_tasks.append(load_mcp_tool_task)

        tools_list = await asyncio.gather(*load_mcp_tool_tasks, return_exceptions=True)
        for server_name, tools in zip(server_names, tools_list):
            if isinstance(tools, Exception):
                logger.error(f"Failed to get tools for {server_name}: {tools}")
                if server_name in self.connections:
                    del self.connections[server_name]
                if server_name in self.client.connections:
                    del self.client.connections[server_name]
                self.mcp_servers.append(
                    McpServer(server_name=server_name, connected=False, tools=[])
                )

                continue
            else:
                self.tools.extend(tools)
                self.mcp_servers.append(
                    McpServer(server_name=server_name, connected=True, tools=tools)
                )

    async def get_tools(self) -> list[BaseTool]:
        """Get all tools or a specific server's tools."""
        return self.tools

    async def get_mcp_server(
        self, server_name: str
    ) -> StdioConnection | SSEConnection | StreamableHttpConnection:
        """Get a MCP server."""
        if server_name not in self.connections:
            raise ValueError(f"MCP server {server_name} not found")

        return self.connections[server_name]

    async def remove_mcp_server(self, server_name: str):
        """Remove a MCP server."""
        if server_name not in self.connections:
            raise ValueError(f"MCP server {server_name} not found")

        del self.connections[server_name]
        logger.info(f"Removed MCP server: {server_name} from connections")

        self.client = MultiServerMCPClient(connections=self.connections)
        await self._initialize_tools()

    async def teardown(self):
        """Teardown the Multi server MCP client manager."""
        self.tools = []
        self.mcp_servers = []
        self.connections = {}
        self.client = None
