"""This module contains the service for the agent."""

from __future__ import annotations

import logging
from typing import Any, List

from axmp_ai_agent_spec.profile_node_data import (
    AgentData,
    AgentMemoryData,
    ChatbotTriggerData,
    LLMModelData,
    McpServerData,
    SchedulerTriggerData,
    WebhookTriggerData,
)
from axmp_ai_agent_spec.profiles.single_agent_profile import (
    NodeOfSingleAgent,
    SingleAgentFlow,
    SingleAgentProfile,
)
from axmp_ai_agent_spec.types import MCPServerType, NodeType, ProfileType, TransportType
from axmp_openapi_helper import AuthenticationType
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.base import BaseStore
from motor.motor_asyncio import AsyncIOMotorClient

from axmp_ai_agent_core.agent.single_spec_agent import SingleSpecAgent
from axmp_ai_agent_core.agent.util.mcp_client_manager import McpServer
from axmp_ai_agent_core.db.agent_profile_history_repository import (
    AgentProfileHistoryRepository,
)
from axmp_ai_agent_core.db.agent_profile_repository import AgentProfileRepository
from axmp_ai_agent_core.db.chat_file_repository import ChatFileRepository
from axmp_ai_agent_core.db.chat_memory_repository import ChatMemoryRepository
from axmp_ai_agent_core.db.llm_provider_repository import LlmProviderRepository
from axmp_ai_agent_core.db.user_credential_repository import UserCredentialRepository
from axmp_ai_agent_core.entity.agent_profile import (
    AgentNodeData,
    AgentProfile,
    AgentProfileFlow,
    AgentProfileNode,
    ChatbotTriggerNodeData,
    ExternalMcpServerNodeData,
    InternalMcpServerNodeData,
    LLMNodeData,
    MemoryNodeData,
    SchedulerTriggerNodeData,
    WebhookTriggerNodeData,
)
from axmp_ai_agent_core.entity.chat_file import ChatFile
from axmp_ai_agent_core.entity.llm_provider import LlmModel
from axmp_ai_agent_core.entity.user_credential import UserCredentialType
from axmp_ai_agent_core.exception.db_exceptions import (
    InvalidObjectIDException,
    ObjectNotFoundException,
)
from axmp_ai_agent_core.exception.service_exceptions import (
    CoreError,
    CoreServiceException,
)
from axmp_ai_agent_core.filter.agent_profile_query import AgentProfileQueryParameters
from axmp_ai_agent_core.filter.chat_file_query import ChatFilesQueryParameters
from axmp_ai_agent_core.setting import core_settings

logger = logging.getLogger(__name__)

MCP_SERVER_CONFIG_KEY = "mcpServers"


class AgentProfileService:
    """The service for the agent."""

    def __init__(
        self,
        client: AsyncIOMotorClient,
        agent_profile_repository: AgentProfileRepository,
        chat_file_repository: ChatFileRepository,
        llm_provider_repository: LlmProviderRepository,
        user_credential_repository: UserCredentialRepository,
        chat_memory_repository: ChatMemoryRepository,
        agent_profile_history_repository: AgentProfileHistoryRepository,
    ):
        """Initialize the agent service."""
        self._client = client
        self._agent_profile_repository: AgentProfileRepository = (
            agent_profile_repository
        )
        self._chat_file_repository: ChatFileRepository = chat_file_repository
        self._llm_provider_repository: LlmProviderRepository = llm_provider_repository
        self._user_credential_repository: UserCredentialRepository = (
            user_credential_repository
        )
        self._chat_memory_repository: ChatMemoryRepository = chat_memory_repository
        self._agent_profile_history_repository: AgentProfileHistoryRepository = (
            agent_profile_history_repository
        )

    async def get_agent_profiles(
        self,
        *,
        query_parameters: AgentProfileQueryParameters,
        page_number: int = 1,
        page_size: int = 10,
    ) -> List[AgentProfile]:
        """Get agent profiles with root node information via pipeline."""
        return await self._agent_profile_repository.find_all(
            query_parameters=query_parameters,
            page_number=page_number,
            page_size=page_size,
        )

    async def get_agent_profile_by_id(self, *, id: str) -> AgentProfile:
        """Get an agent profile by ID."""
        try:
            agent_profile = await self._agent_profile_repository.find_by_id(item_id=id)
        except InvalidObjectIDException:
            raise CoreServiceException(
                CoreError.INVALID_OBJECTID,
                details=f"Invalid agent profile ID format: {id}",
            )
        except ObjectNotFoundException:
            raise CoreServiceException(
                CoreError.ID_NOT_FOUND,
                details=f"Agent profile not found: {id}",
            )

        return agent_profile

    async def get_latest_agent_profile_from_history(self, *, id: str) -> AgentProfile:
        """Get the latest version of the agent profile from the history."""
        try:
            agent_profile = await self._agent_profile_repository.find_by_id(item_id=id)
        except InvalidObjectIDException:
            raise CoreServiceException(
                CoreError.INVALID_OBJECTID,
                details=f"Invalid agent profile ID format: {id}",
            )
        except ObjectNotFoundException:
            raise CoreServiceException(
                CoreError.ID_NOT_FOUND,
                details=f"Agent profile not found: {id}",
            )

        latest_version = await self._agent_profile_history_repository.get_max_version(
            agent_profile_id=id
        )

        if latest_version == 0:
            raise CoreServiceException(
                CoreError.NO_STABLE_VERSION_FOUND,
                details=f"The agent profile ({agent_profile.name}) has no stable version",
            )

        agent_profile_history = (
            await self._agent_profile_history_repository.find_by_profile_id_and_version(
                profile_id=id,
                version=latest_version,
            )
        )

        return agent_profile_history.agent_profile_data

    async def create_chat_file(
        self,
        *,
        chat_file: ChatFile,
    ) -> ChatFile:
        """Create a new file for a project. Just save ChatFiles to DB."""
        file_id = await self._chat_file_repository.insert(item=chat_file)

        return await self.get_chat_file(file_id=file_id)

    async def get_chat_file(self, *, file_id: str) -> ChatFile:
        """Get a file by file_id."""
        try:
            chat_file = await self._chat_file_repository.find_by_id(item_id=file_id)
        except InvalidObjectIDException:
            raise CoreServiceException(
                CoreError.INVALID_OBJECTID,
                details=f"Invalid file ID format: {file_id}",
            )
        except ObjectNotFoundException:
            raise CoreServiceException(
                CoreError.ID_NOT_FOUND,
                details=f"File not found: {file_id}",
            )
        return chat_file

    async def remove_chat_file(self, *, file_id: str) -> bool:
        """Delete a file from a project by file_id."""
        # TODO: Implement S3 file deletion
        try:
            return await self._chat_file_repository.delete(item_id=file_id)
        except ObjectNotFoundException:
            raise CoreServiceException(
                CoreError.ID_NOT_FOUND,
                details=f"File not found: {file_id}",
            )
        except InvalidObjectIDException:
            raise CoreServiceException(
                CoreError.INVALID_OBJECTID,
                details=f"Invalid file ID format: {file_id}",
            )

    async def get_chat_files(
        self,
        *,
        query_parameters: ChatFilesQueryParameters,
    ) -> list[ChatFile]:
        """Get files by file_ids."""
        return await self._chat_file_repository.find_all_without_pagination(
            query_parameters=query_parameters,
        )

    async def get_chat_files_count(
        self,
        *,
        query_parameters: ChatFilesQueryParameters,
    ) -> int:
        """Get files count by file_ids."""
        return await self._chat_file_repository.count(query_parameters=query_parameters)

    async def get_agent_profiles_simple(
        self,
        *,
        query_parameters: AgentProfileQueryParameters,
    ) -> List[AgentProfile]:
        """Get agent profiles simple."""
        return await self._agent_profile_repository.find_all_without_pagination(
            query_parameters=query_parameters,
            include_fields=[
                "id",
                "name",
                "icon_url",
                "status",
                "runtime_type",
                "created_by",
            ],
            exclude_fields=[],
        )

    async def create_agent_based_on_specification(
        self,
        *,
        agent_profile: AgentProfile,
        checkpointer: MemorySaver,
        store: BaseStore,
    ) -> SingleSpecAgent:
        """Transform an agent profile to an agent specification."""
        if agent_profile.type == ProfileType.SINGLE_AGENT:
            flow: AgentProfileFlow = agent_profile.flow
            if flow is None:
                raise CoreServiceException(
                    CoreError.BAD_REQUEST,
                    details=f"Agent profile flow is not found: {agent_profile.id}",
                )

            profile_nodes: list[AgentProfileNode] = flow.nodes
            if profile_nodes is None:
                raise CoreServiceException(
                    CoreError.BAD_REQUEST,
                    details=f"Agent profile nodes are not found: {agent_profile.id}",
                )

            spec_nodes: list[NodeOfSingleAgent] = []
            for node in profile_nodes:
                if node.type == NodeType.TRIGGER:
                    trigger_node_data: (
                        ChatbotTriggerNodeData
                        | WebhookTriggerNodeData
                        | SchedulerTriggerNodeData
                    ) = node.data

                    if isinstance(trigger_node_data, ChatbotTriggerNodeData):
                        spec_nodes.append(
                            NodeOfSingleAgent(
                                id=node.id,
                                type=NodeType.TRIGGER,
                                root_node=node.root_node,
                                data=ChatbotTriggerData(
                                    type=trigger_node_data.type,
                                    init_message=trigger_node_data.init_message,
                                ),
                            )
                        )
                    elif isinstance(trigger_node_data, WebhookTriggerNodeData):
                        spec_nodes.append(
                            NodeOfSingleAgent(
                                id=node.id,
                                type=NodeType.TRIGGER,
                                root_node=node.root_node,
                                data=WebhookTriggerData(
                                    type=trigger_node_data.type,
                                ),
                            )
                        )
                    elif isinstance(trigger_node_data, SchedulerTriggerNodeData):
                        spec_nodes.append(
                            NodeOfSingleAgent(
                                id=node.id,
                                type=NodeType.TRIGGER,
                                root_node=node.root_node,
                                data=SchedulerTriggerData(
                                    type=trigger_node_data.type,
                                    cron_expression=trigger_node_data.cron_expression,
                                    timezone=trigger_node_data.timezone,
                                ),
                            )
                        )
                    else:
                        raise CoreServiceException(
                            CoreError.BAD_REQUEST,
                            details=f"Invalid trigger node data: {trigger_node_data}",
                        )
                elif node.type == NodeType.AI_AGENT:
                    agent_node_data: AgentNodeData = node.data
                    # NOTE: for the issue #19, we need to validate the system prompt
                    try:
                        agent_data: AgentData = AgentData(
                            name=agent_node_data.name,
                            system_prompt=agent_node_data.system_prompt,
                        )
                    except ValueError as e:
                        raise CoreServiceException(
                            CoreError.BAD_REQUEST,
                            details=f"System prompt contains potentially dangerous content: {e}",
                        )

                    spec_nodes.append(
                        NodeOfSingleAgent(
                            id=node.id,
                            type=NodeType.AI_AGENT,
                            root_node=node.root_node,
                            data=agent_data,
                        )
                    )
                elif node.type == NodeType.LLM:
                    llm_node_data: LLMNodeData = node.data

                    llm_provider = await self._llm_provider_repository.find_by_id(
                        item_id=llm_node_data.provider_id
                    )
                    user_credential = await self._user_credential_repository.find_by_id(
                        item_id=llm_node_data.api_key_credential_id
                    )

                    if llm_node_data.api_key_owner_username != user_credential.username:
                        raise CoreServiceException(
                            CoreError.BAD_REQUEST,
                            details=f"API key owner username is not match: {llm_node_data.api_key_owner_username} != {user_credential.username}",
                        )
                    if (
                        user_credential.credential_type
                        != UserCredentialType.LLM_PROVIDER
                    ):
                        raise CoreServiceException(
                            CoreError.BAD_REQUEST,
                            details=f"Credential type is not LLM_PROVIDER: {user_credential.credential_type}",
                        )

                    spec_nodes.append(
                        NodeOfSingleAgent(
                            id=node.id,
                            type=NodeType.LLM,
                            root_node=node.root_node,
                            data=LLMModelData(
                                provider=llm_provider.key,
                                base_url=llm_provider.base_url or None,
                                default_model_id=llm_node_data.default_model or None,
                                temperature=llm_node_data.temperature,
                                max_tokens=llm_node_data.max_tokens,
                                api_key=user_credential.llm_api_key,
                                aws_access_key_id=user_credential.aws_access_key_id,
                                aws_secret_access_key=user_credential.aws_secret_access_key,
                                aws_region_name=user_credential.region_name,
                            ),
                        )
                    )
                elif node.type == NodeType.MEMORY:
                    memory_node_data: MemoryNodeData = node.data
                    agent_memory = await self._chat_memory_repository.find_by_id(
                        item_id=memory_node_data.memory_id
                    )

                    spec_nodes.append(
                        NodeOfSingleAgent(
                            id=node.id,
                            type=NodeType.MEMORY,
                            root_node=node.root_node,
                            data=AgentMemoryData(
                                memory_type=memory_node_data.memory_type,
                                db_uri=agent_memory.db_uri,
                            ),
                        )
                    )
                elif node.type == NodeType.MCP_SERVER:
                    mcp_server_data: (
                        InternalMcpServerNodeData | ExternalMcpServerNodeData
                    ) = node.data

                    if mcp_server_data.mcp_config_json is None:
                        raise CoreServiceException(
                            CoreError.BAD_REQUEST,
                            details=f"The MCP server {mcp_server_data.name} doesn't have mcp_config_json",
                        )

                    mcp_connection: dict[str, Any] = (
                        mcp_server_data.mcp_config_json.mcpServers
                    )

                    if not mcp_connection:
                        raise CoreServiceException(
                            CoreError.BAD_REQUEST,
                            details=f"The MCP server {mcp_server_data.name} doesn't have {MCP_SERVER_CONFIG_KEY} key",
                        )

                    # server_name, connection = mcp_connection.popitem()
                    server_name = next(iter(mcp_connection))
                    connection = mcp_connection[server_name]
                    # NOTE: langgraph mcp adapter requires the transport key
                    if connection.get("transport") is None:
                        connection["transport"] = "stdio"
                    else:
                        # NOTE: langgraph mcp adapter's key for the streamable-http is streamable_http
                        # replace the streamable-http to streamable_http
                        if connection.get("transport") == TransportType.STREAMABLE_HTTP:
                            connection["transport"] = "streamable_http"

                    # build the headers for the internal MCP server using the backend server auth configs
                    # NOTE: currently, openapi-mcp-server supports only the headers of the backend servers
                    # TODO: support the headers of the MCP server later
                    if mcp_server_data.resource_type == MCPServerType.INTERNAL:
                        headers = connection.get("headers", {})
                        for (
                            backend_auth_config
                        ) in mcp_server_data.backend_server_auth_configs:
                            if (
                                backend_auth_config.auth_config.type
                                == AuthenticationType.BASIC
                            ):
                                headers[
                                    f"{backend_auth_config.server_system_name}{core_settings.mcp_server_separator}username"
                                ] = backend_auth_config.auth_config.username
                                headers[
                                    f"{backend_auth_config.server_system_name}{core_settings.mcp_server_separator}password"
                                ] = backend_auth_config.auth_config.password
                            elif (
                                backend_auth_config.auth_config.type
                                == AuthenticationType.BEARER
                            ):
                                headers[
                                    f"{backend_auth_config.server_system_name}{core_settings.mcp_server_separator}bearer_token"
                                ] = backend_auth_config.auth_config.bearer_token
                            elif (
                                backend_auth_config.auth_config.type
                                == AuthenticationType.API_KEY
                            ):
                                headers[
                                    f"{backend_auth_config.server_system_name}{core_settings.mcp_server_separator}{backend_auth_config.auth_config.api_key_name}"
                                ] = backend_auth_config.auth_config.api_key_value

                        connection["headers"] = headers

                    logger.info(
                        f"MCP server : {server_name}, connection:\n{connection}"
                    )

                    new_connection: dict[str, Any] = {}
                    new_connection[server_name] = connection

                    spec_nodes.append(
                        NodeOfSingleAgent(
                            id=node.id,
                            type=NodeType.MCP_SERVER,
                            root_node=node.root_node,
                            data=McpServerData(
                                config=new_connection,
                            ),
                        )
                    )

            flow: SingleAgentFlow = SingleAgentFlow(
                nodes=spec_nodes,
            )

            try:
                agent_spec_profile = SingleAgentProfile(
                    id=agent_profile.id,
                    name=agent_profile.name,
                    system_name=agent_profile.system_name,
                    version=agent_profile.version,
                    runtime_type=agent_profile.runtime_type,
                    # deployment_mode=agent_profile.deployment_mode,
                    # auth_config=agent_profile.auth_config,
                    # endpoint_config=agent_profile.endpoint_config,
                    flow=flow,
                )
            except Exception as e:
                logger.error(f"Error creating agent spec profile: {e}")
                raise CoreServiceException(
                    CoreError.BAD_REQUEST,
                    details=f"Error creating agent spec profile: {e}",
                )

            logger.info(
                f"Agent spec profile: {agent_spec_profile.model_dump_json(indent=2)}"
            )
            agent = SingleSpecAgent(
                memory=checkpointer,
                store=store,
                specification=agent_spec_profile,
            )
            try:
                await agent.initialize()
            except Exception as e:
                logger.error(f"Error initializing agent: {e}")
                raise CoreServiceException(
                    CoreError.INTERNAL_SERVER_ERROR,
                    details=f"Error initializing agent: {e}",
                )

            return agent

        elif agent_profile.type == ProfileType.A2A_HOST_AGENT:
            pass
        elif agent_profile.type == ProfileType.WORKFLOW:
            pass
        else:
            raise CoreServiceException(
                CoreError.BAD_REQUEST,
                details=f"Invalid agent profile type: {agent_profile.type}",
            )

    async def get_agent_profile_node_by_type(
        self, nodes: list[AgentProfileNode], node_type: NodeType
    ) -> AgentProfileNode:
        """Get the agent profile node by the node type."""
        if node_type == NodeType.MCP_SERVER:
            raise CoreServiceException(
                CoreError.BAD_REQUEST,
                details=f"MCP server node is not supported: {node_type}",
            )

        for node in nodes:
            if node.type == node_type:
                return node

        raise CoreServiceException(
            CoreError.BAD_REQUEST,
            details=f"Agent profile node is not found: {node_type}",
        )

    async def get_agent_profile_mcp_servers(
        self, nodes: list[AgentProfileNode]
    ) -> list[McpServer]:
        """Get the MCP servers by the agent profile nodes."""
        mcp_servers = []
        for node in nodes:
            if node.type == NodeType.MCP_SERVER:
                mcp_server_data: (
                    InternalMcpServerNodeData | ExternalMcpServerNodeData
                ) = node.data

                mcp_connection: dict[str, Any] = (
                    mcp_server_data.mcp_config_json.mcpServers
                )

                if not mcp_connection:
                    raise CoreServiceException(
                        CoreError.BAD_REQUEST,
                        details=f"The MCP server {mcp_server_data.name} doesn't have {MCP_SERVER_CONFIG_KEY} key",
                    )
                else:
                    # server_name, connection = mcp_connection.popitem()
                    server_name = next(iter(mcp_connection))
                    # connection = mcp_connection[server_name]

                mcp_servers.append(
                    McpServer(
                        server_name=server_name,
                        # connected=False,
                        # tools=[],
                        registry_id=mcp_server_data.registry_id,
                        resource_type=mcp_server_data.resource_type,
                        transport_type=mcp_server_data.transport_type,
                        icon_url=mcp_server_data.icon_url,
                    )
                )
        return mcp_servers

    async def get_llm_models(self, provider_id: str) -> list[LlmModel]:
        """Get the LLM models by the provider id."""
        try:
            llm_provider = await self._llm_provider_repository.find_by_id(
                item_id=provider_id
            )
        except InvalidObjectIDException:
            raise CoreServiceException(
                CoreError.INVALID_OBJECTID,
                details=f"Invalid provider ID format: {provider_id}",
            )
        except ObjectNotFoundException:
            raise CoreServiceException(
                CoreError.ID_NOT_FOUND,
                details=f"Provider not found: {provider_id}",
            )
        return llm_provider.models if llm_provider.models is not None else []
