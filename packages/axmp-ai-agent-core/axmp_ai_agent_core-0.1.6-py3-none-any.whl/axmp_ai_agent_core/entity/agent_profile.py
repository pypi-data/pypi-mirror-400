"""Reactflow Profile Entity. This entity is used to store the profile of the reactflow."""

from __future__ import annotations

from typing import Any

from axmp_ai_agent_spec.types import (
    AgentMemoryType,
    MCPServerType,
    NodeType,
    ProfileStatus,
    ProfileType,
    RuntimeType,
    TransportType,
    TriggerType,
    UsageType,
)
from axmp_openapi_helper import (
    AuthConfig,
)
from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from axmp_ai_agent_core.entity.base_model import (
    NamedCoreBaseModel,
)
from axmp_ai_agent_core.entity.base_profile import (
    BaseFlow,
    BaseNode,
)
from axmp_ai_agent_core.entity.shared_target import SharedTarget


class ChatbotTriggerNodeData(BaseModel):
    """Chatbot Trigger Node Data entity."""

    type: TriggerType = Field(
        default=TriggerType.CHATBOT, description="The type of the trigger node."
    )
    init_message: str | None = Field(
        None,
        description="The init message of the trigger node.",
        min_length=1,
        max_length=2000,
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="forbid",
    )


class WebhookTriggerNodeData(BaseModel):
    """Webhook Trigger Node Data entity."""

    type: TriggerType = Field(
        default=TriggerType.WEBHOOK, description="The type of the trigger node."
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="forbid",
    )


class SchedulerTriggerNodeData(BaseModel):
    """Scheduler Trigger Node Data entity."""

    type: TriggerType = Field(
        default=TriggerType.SCHEDULER, description="The type of the trigger node."
    )
    cron_expression: str = Field(
        ...,
        description="The cron expression of the trigger node.",
        min_length=1,
        max_length=255,
    )
    timezone: str | None = Field(
        None,
        description="The timezone of the trigger node.",
        min_length=1,
        max_length=255,
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="forbid",
    )


class AgentNodeData(BaseModel):
    """Agent Node Data entity."""

    name: str = Field(
        ...,
        description="The name of the agent node.",
        min_length=1,
        max_length=255,
        # pattern=r"^[a-zA-Z0-9 _-]+$",
    )
    system_prompt: str | None = Field(
        None,
        description="The system prompt of the agent node.",
        min_length=1,
        # NOTE: No max length for system prompt
        # max_length=2000,
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="forbid",
    )


class LLMNodeData(BaseModel):
    """LLM Node Data entity."""

    provider_id: str = Field(
        ..., description="The provider of the LLM node.", min_length=1, max_length=255
    )
    provider_name: str | None = Field(
        None,
        description="The provider name of the LLM node.",
        min_length=1,
        max_length=255,
    )
    icon_url: str | None = Field(
        None,
        description="The icon url of the LLM node.",
        min_length=1,
        max_length=255,
    )
    default_model: str | None = Field(
        None,
        description="The default model of the LLM node.",
        min_length=1,
        max_length=255,
    )
    temperature: float = Field(
        0,
        description="The temperature of the LLM node.",
        ge=0,
        le=1,
    )
    max_tokens: int = Field(
        5000,
        description="The max tokens of the LLM node.",
        ge=5000,
        # NOTE: TBD max length for max tokens
        le=1000000,
    )
    api_key_owner_username: str = Field(
        ...,
        description="The username of the API key owner of the LLM provider.",
        min_length=1,
        max_length=255,
    )
    api_key_credential_id: str = Field(
        ...,
        description="The API key credential id of the LLM provider.",
        min_length=1,
        max_length=255,
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="forbid",
    )


class MemoryNodeData(BaseModel):
    """Memory Node Data entity."""

    memory_id: str = Field(
        ...,
        description="The chat memory id of the memory node.",
        min_length=1,
        max_length=255,
    )
    memory_name: str | None = Field(
        None,
        description="The memory name of the memory node.",
        min_length=1,
        max_length=255,
    )
    memory_type: AgentMemoryType = Field(
        ..., description="The type of the memory node."
    )
    icon_url: str | None = Field(
        None,
        description="The icon url of the memory node.",
        min_length=1,
        max_length=255,
    )
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="forbid",
    )


class McpServerConfigJson(BaseModel):
    """MCP Server config json."""

    mcpServers: dict[str, Any] = Field(default_factory=dict)


class McpServerBackendServerAuthConfig(BaseModel):
    """MCP Server Playground Backend Server Auth Config."""

    server_id: str = Field(..., description="Backend server ID")
    server_name: str = Field(..., description="Backend server name")
    server_system_name: str = Field(..., description="Backend server system name")
    auth_config: AuthConfig = Field(..., description="Backend server auth config")


class InternalMcpServerNodeData(BaseModel):
    """MCP Server entity.

    Only include the data for the right sidebar of the reactflow.
    """

    resource_type: MCPServerType = MCPServerType.INTERNAL
    transport_type: TransportType | None = None
    registry_id: str = Field(
        ...,
        description="The server instance id of the MCP server node.",
        min_length=1,
        max_length=255,
    )
    name: str = Field(
        ...,
        description="The name of the MCP server node.",
        min_length=1,
        max_length=255,
    )
    icon_url: str | None = Field(
        None,
        description="The icon url of the MCP server node.",
        min_length=1,
        max_length=255,
    )
    auth_config: AuthConfig = Field(
        ..., description="The authentication config of the MCP server node."
    )
    backend_server_auth_configs: list[McpServerBackendServerAuthConfig] = Field(
        [], description="The authentication configs of the backend server nodes."
    )
    mcp_config_json: McpServerConfigJson | None = Field(
        None,
        description="The config of the internal MCP server node.",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="forbid",
    )


class ExternalMcpServerNodeData(BaseModel):
    """External MCP Server entity.

    Only include the data for the right sidebar of the reactflow.
    """

    resource_type: MCPServerType = MCPServerType.EXTERNAL
    transport_type: TransportType | None = None
    registry_id: str = Field(
        ...,
        description="The server id of the external MCP server node.",
        min_length=1,
        max_length=255,
    )
    name: str = Field(
        ...,
        description="The name of the external MCP server node.",
        min_length=1,
        max_length=255,
    )
    icon_url: str | None = Field(
        None,
        description="The icon url of the MCP server node.",
        min_length=1,
        max_length=255,
    )
    mcp_config_json: McpServerConfigJson | None = Field(
        None,
        description="The config of the external MCP server node.",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="forbid",
    )


class AgentProfileNode(BaseNode):
    """Node Entity. This entity is used to store the node of the reactflow."""

    type: NodeType
    data: (
        ChatbotTriggerNodeData
        | WebhookTriggerNodeData
        | SchedulerTriggerNodeData
        | AgentNodeData
        | LLMNodeData
        | MemoryNodeData
        | InternalMcpServerNodeData
        | ExternalMcpServerNodeData
    )

    @model_validator(mode="after")
    def validate_type(self) -> AgentProfileNode:
        """Validate that the type of the node is valid."""
        if self.type not in [
            NodeType.TRIGGER,
            NodeType.AI_AGENT,
            NodeType.LLM,
            NodeType.MEMORY,
            NodeType.MCP_SERVER,
            NodeType.REMOTE_AGENT,
        ]:
            raise ValueError(f"Invalid node type: {self.type}")

        if self.type == NodeType.TRIGGER:
            if not isinstance(
                self.data,
                ChatbotTriggerNodeData
                | WebhookTriggerNodeData
                | SchedulerTriggerNodeData,
            ):
                raise ValueError(f"Invalid trigger node data: {self.data}")

        if self.type == NodeType.AI_AGENT:
            if not isinstance(self.data, AgentNodeData):
                raise ValueError(f"Invalid AI agent node data: {self.data}")

        if self.type == NodeType.LLM:
            if not isinstance(self.data, LLMNodeData):
                raise ValueError(f"Invalid LLM node data: {self.data}")

        if self.type == NodeType.MEMORY:
            if not isinstance(self.data, MemoryNodeData):
                raise ValueError(f"Invalid memory node data: {self.data}")

        if self.type == NodeType.MCP_SERVER:
            if not isinstance(
                self.data, InternalMcpServerNodeData | ExternalMcpServerNodeData
            ):
                raise ValueError(f"Invalid MCP server node data: {self.data}")

        # if self.type == NodeType.REMOTE_AGENT:
        #     if not isinstance(self.data, RemoteAgentNodeData):
        #         raise ValueError(f"Invalid remote agent node data: {self.data}")
        return self


class AgentProfileFlow(BaseFlow):
    """Flow Entity. This entity is used to store the flow of the reactflow."""

    nodes: list[AgentProfileNode] | None = None

    @model_validator(mode="after")
    def validate_root_node(self) -> AgentProfileFlow:
        """Validate that only AI_AGENT type node can be root node.

        If there is a non-AI_AGENT type node with root_node=True, raise validation error.
        """
        if not self.nodes:
            return self

        root_node_count = 0
        for node in self.nodes:
            if node.type != NodeType.AI_AGENT and node.root_node:
                raise ValueError(
                    f"Only AI_AGENT type node can be root node. Found {node.type} type node with root_node=True"
                )

            # NOTE: for the multi-agent flow, the AI_AGENT type node can be root node or not
            # if node.type == AgentProfileNodeType.AI_AGENT and not node.root_node:
            #     raise ValueError(
            #         f"AI_AGENT type node must be root node. Found {node.type} type node with root_node=False"
            #     )

            # if node.type == AgentProfileNodeType.AI_AGENT and node.root_node:
            #     root_node_count += 1

            if node.root_node:
                root_node_count += 1

        if root_node_count > 1:
            raise ValueError(
                f"Only one AI_AGENT type node can be root node. Found {root_node_count} AI_AGENT type nodes with root_node=True"
            )

        return self


class AgentProfile(NamedCoreBaseModel):
    """Reactflow Agent Profile Entity. This entity is used to store the profile of the reactflow."""

    description: str | None = Field(
        None,
        description="The description of the agent node.",
        min_length=1,
        max_length=2000,
    )
    icon_url: str | None = Field(
        None,
        description="The icon url of the agent node.",
        min_length=1,
        max_length=255,
    )
    version: int | None = Field(None, description="The version of the agent node.")
    type: ProfileType = Field(
        default=ProfileType.SINGLE_AGENT,
        description="The type of the agent profile.",
    )
    status: ProfileStatus = Field(
        default=ProfileStatus.DRAFT,
        description="The status of the agent profile.",
    )
    runtime_type: RuntimeType = Field(
        default=RuntimeType.WORKSPACE,
        description="The runtime type of the agent profile.",
    )
    usage_type: UsageType | None = Field(
        None,
        description="The usage type of the agent profile.",
    )
    idle_time: int | None = Field(
        None,
        description="The idle timeout of the agent instance.",
    )
    labels: dict[str, str] | None = Field(
        None, description="The labels of the agent node."
    )

    trigger_type: TriggerType | None = Field(
        None,
        description="The trigger type of the agent profile.",
    )

    is_published_to_workspace: bool | None = Field(
        None,
        description="Whether the agent profile is published to the workspace.",
    )

    shared_target: SharedTarget | None = None

    flow: AgentProfileFlow | None = None

    # NOTE: These fields are not used in the agent profile. Is has been moved to the agent profile provsion status.
    # auth_config: AuthenticationConfig | None = Field(
    #     None,
    #     description="The authentication config of the agent profile.",
    # )
    # """ This is the auth config for the agent profile.
    # It is an optional field and used to authenticate the agent profile when the agent profile is deployed as a standalone agent.
    # """
    # endpoint_config: EndpointConfig | None = Field(
    #     None,
    #     description="The endpoint config of the agent profile.",
    # )
    # """ This is the endpoint config for the agent profile.
    # It is an optional field and used to use the custom domain name and webhook path for the agent profile when the agent profile is deployed as a standalone agent.
    # """
    # deployment_mode: DeploymentMode | None = Field(
    #     None,
    #     description="The deployment mode of the agent profile.",
    # )
    # NOTE: These fields are not used anymore. It has been moved to the agent profile provision status.
    # provisioned_version: str | None = Field(
    #     None,
    #     description="The provisioned version of the agent node.",
    #     min_length=1,
    #     max_length=255,
    # )

    @field_serializer("version", when_used="json")
    def _serialize_version(self, version: str | None) -> str | None:
        if version is None:
            return None
        else:
            return f"v{version}"

    @property
    def root_node(self) -> AgentNodeData | None:
        """Get AgentNodeData of the root AI agent node in the profile flow."""
        if not self.flow or not self.flow.nodes:
            return None

        for node in self.flow.nodes:
            if node.root_node:
                if node.type == NodeType.AI_AGENT:
                    if node.data and isinstance(node.data, AgentNodeData):
                        return node.data

        return None

    def get_node_by_type(self, node_type: NodeType) -> AgentProfileNode:
        """Get the agent profile node by the node type."""
        if not self.flow or not self.flow.nodes:
            raise ValueError("Agent profile node does not have any nodes")

        for node in self.flow.nodes:
            if node.type == node_type:
                return node

        raise ValueError(
            f"Agent profile node is not found: {node_type}",
        )
