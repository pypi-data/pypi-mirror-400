"""Agent profile history entity."""

from pydantic import field_serializer

from axmp_ai_agent_core.entity.agent_profile import AgentProfile
from axmp_ai_agent_core.entity.base_model import CoreBaseModel


class AgentProfileHistory(CoreBaseModel):
    """Agent profile history entity."""

    agent_profile_id: str
    version: int
    comment: str
    agent_profile_data: AgentProfile

    @field_serializer("version", when_used="json")
    def _serialize_version(self, version: str | None) -> str | None:
        if version is None:
            return None
        else:
            return f"v{version}"
