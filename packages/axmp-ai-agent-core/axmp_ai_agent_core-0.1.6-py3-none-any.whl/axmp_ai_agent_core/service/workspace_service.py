"""This module contains the service for the workspace."""

from __future__ import annotations

import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from motor.motor_asyncio import AsyncIOMotorClient

from axmp_ai_agent_core.agent.util.load_chat_model import load_chat_model
from axmp_ai_agent_core.db.conversation_repository import ConversationRepository
from axmp_ai_agent_core.db.llm_provider_repository import LlmProviderRepository
from axmp_ai_agent_core.entity.chat_conversation import Conversation
from axmp_ai_agent_core.entity.llm_provider import LlmProvider
from axmp_ai_agent_core.entity.user_credential import AWS_BEDROCK
from axmp_ai_agent_core.exception.db_exceptions import (
    InvalidObjectIDException,
    ObjectNotFoundException,
    ValueErrorException,
)
from axmp_ai_agent_core.exception.service_exceptions import (
    CoreError,
    CoreServiceException,
)
from axmp_ai_agent_core.filter.chat_conversation_query import (
    ConversationQueryParameters,
)

logger = logging.getLogger(__name__)


class WorkspaceService:
    """The service for the workspace."""

    def __init__(
        self,
        client: AsyncIOMotorClient,
        conversation_repository: ConversationRepository,
        llm_provider_repository: LlmProviderRepository,
    ):
        """Initialize the user service."""
        self._client = client
        self._conversation_repository: ConversationRepository = conversation_repository
        self._llm_provider_repository: LlmProviderRepository = llm_provider_repository

    async def create_conversation(self, *, conversation: Conversation) -> Conversation:
        """Create a new conversation."""
        try:
            conversation_id = await self._conversation_repository.insert(
                item=conversation
            )
            return await self.get_conversation_by_id(id=conversation_id)
        except ValueErrorException as e:
            raise CoreServiceException(
                CoreError.BAD_REQUEST,
                details=f"Conversation thread_id {conversation.thread_id} already exists. Details: {e}",
            )

    async def get_conversation_by_id(self, *, id: str) -> Conversation:
        """Get a conversation by ID."""
        try:
            conversation = await self._conversation_repository.find_by_id(item_id=id)
        except InvalidObjectIDException:
            raise CoreServiceException(
                CoreError.INVALID_OBJECTID,
                details=f"Invalid conversation ID format: {id}",
            )
        except ObjectNotFoundException:
            raise CoreServiceException(
                CoreError.ID_NOT_FOUND,
                details=f"Conversation not found: {id}",
            )

        return conversation

    async def get_conversation_by_thread_id(self, *, thread_id: str) -> Conversation:
        """Get a conversation by thread ID."""
        try:
            conversation = await self._conversation_repository.find_by_thread_id(
                thread_id=thread_id
            )
        except ObjectNotFoundException:
            raise CoreServiceException(
                CoreError.ID_NOT_FOUND,
                details=f"Conversation not found: {thread_id}",
            )

        return conversation

    async def modify_conversation(self, *, conversation: Conversation) -> Conversation:
        """Update a conversation."""
        try:
            updated_conversation = await self._conversation_repository.update(
                item=conversation
            )
            return updated_conversation
        except InvalidObjectIDException:
            raise CoreServiceException(
                CoreError.INVALID_OBJECTID,
                details=f"Invalid conversation ID format: {conversation.id}",
            )
        except ObjectNotFoundException:
            raise CoreServiceException(
                CoreError.ID_NOT_FOUND,
                details=f"Conversation not found: {conversation.id}",
            )

    async def remove_conversation_by_thread_id(self, *, id: str) -> bool:
        """Delete a conversation."""
        try:
            conversation = await self._conversation_repository.find_by_thread_id(
                thread_id=id
            )
            return await self._conversation_repository.delete(item_id=conversation.id)
        except InvalidObjectIDException:
            raise CoreServiceException(
                CoreError.INVALID_OBJECTID,
                details=f"Invalid conversation ID format: {id}",
            )
        except ObjectNotFoundException:
            raise CoreServiceException(
                CoreError.ID_NOT_FOUND,
                details=f"Conversation not found: {id}",
            )

    async def get_all_conversations(
        self,
        *,
        query_parameters: ConversationQueryParameters,
        page_number: int = 1,
        page_size: int = 20,
    ) -> list[Conversation]:
        """Get all conversations with pagination."""
        return await self._conversation_repository.find_all(
            query_parameters=query_parameters,
            page_number=page_number,
            page_size=page_size,
        )

    async def get_all_conversations_without_pagination(
        self, *, query_parameters: ConversationQueryParameters
    ) -> list[Conversation]:
        """Get all conversations without pagination."""
        return await self._conversation_repository.find_all_without_pagination(
            query_parameters=query_parameters,
        )

    async def count_conversations(
        self, *, query_parameters: ConversationQueryParameters
    ) -> int:
        """Count conversations."""
        return await self._conversation_repository.count(
            query_parameters=query_parameters
        )

    async def generate_conversation_title_with_llm(
        self,
        *,
        text: str,
        provider: str,
        model: str,
        api_key: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        aws_region_name: str | None = None,
        base_url: str | None = None,
        max_length: int = 50,
        temperature: float = 0.7,
        max_tokens: int = 5000,
    ) -> str:
        """Generate title using LLM."""
        if provider == AWS_BEDROCK:
            if not all([aws_access_key_id, aws_secret_access_key, aws_region_name]):
                raise CoreServiceException(
                    CoreError.BAD_REQUEST,
                    details="AWS access key ID, secret access key, and region name are required for AWS Bedrock. All of them are required.",
                )
        else:
            if api_key is None:
                raise CoreServiceException(
                    CoreError.BAD_REQUEST,
                    details=f"API key is required for {provider} providers.",
                )
        try:
            model = load_chat_model(
                fully_specified_name=f"{provider}/{model}",
                temperature=temperature,
                max_tokens=max_tokens,
                base_url=base_url,
                api_key=api_key,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_region_name=aws_region_name,
            )
            prompt = PromptTemplate(
                input_variables=["text"],
                template="Please summarize the following text within 15 characters:\n\n{text}",
            )

            chain: Runnable = prompt | model | StrOutputParser()

            summary = chain.invoke({"text": text})

            if len(summary) > max_length:
                summary = summary[: max_length - 3] + "..."

            return summary
        except Exception as e:
            logging.warning(f"Error occurred during LLM summarization: {e}")
            raise CoreServiceException(
                CoreError.INTERNAL_SERVER_ERROR,
                details=f"Error occurred during LLM summarization: {e}",
            )

    async def get_llm_provider_by_id(self, *, id: str) -> LlmProvider:
        """Get an LLM provider by ID."""
        try:
            llm_provider = await self._llm_provider_repository.find_by_id(item_id=id)
        except InvalidObjectIDException:
            raise CoreServiceException(
                CoreError.INVALID_OBJECTID,
                details=f"Invalid LLM provider ID format: {id}",
            )
        except ObjectNotFoundException:
            raise CoreServiceException(
                CoreError.ID_NOT_FOUND,
                details=f"LLM provider not found: {id}",
            )

        return llm_provider
