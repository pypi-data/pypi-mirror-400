"""LLM provider entity."""

from __future__ import annotations

from enum import Enum

from axmp_openapi_helper import AuthConfig

from axmp_ai_agent_core.entity.base_model import CoreBaseModel

AWS_BEDROCK = "bedrock"


class UserCredentialType(str, Enum):
    """User credential type."""

    LLM_PROVIDER = "LLM_PROVIDER"
    BACKEND_SERVER = "BACKEND_SERVER"
    MCP_SERVER = "MCP_SERVER"


class UserCredential(CoreBaseModel):
    """User credential entity."""

    username: str
    display_name: str
    credential_type: UserCredentialType
    provider: str | None = None
    llm_api_key: str | None = (
        None  # only for the llm provider api key. if type is LLM_PROVIDER, this field is required. openapi is bearer token, the other is api key
    )
    auth_config: AuthConfig | None = (
        None  # backend-server and mcp-server credentials. if type is BACKEND_SERVER or MCP_SERVER, this field is required
    )
    # NOTE: Only for the aws credentials. if provider is bedrock, these field is required.
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    region_name: str | None = None
