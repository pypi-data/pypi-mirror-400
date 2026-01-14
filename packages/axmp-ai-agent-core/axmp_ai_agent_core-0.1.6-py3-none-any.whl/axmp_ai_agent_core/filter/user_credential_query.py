"""Kubernetes configuration query parameters."""

from axmp_ai_agent_core.entity.user_credential import UserCredentialType
from axmp_ai_agent_core.filter.base_search_query import BaseQueryParameters


class UserCredentialQueryParameters(BaseQueryParameters):
    """Query parameters for user credential."""

    username: str
    credential_type: UserCredentialType | None = None
