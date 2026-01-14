"""Search query."""

from pydantic import BaseModel

from axmp_ai_agent_core.entity.user_rbac import AccessPermission
from axmp_ai_agent_core.util.list_utils import SortDirection


class Label:
    """Label."""

    key: str
    value: str

    def __init__(self, label: str):
        """Initialize the label."""
        self.key, self.value = label.split(":", 1)


class BaseQueryParameters(BaseModel):
    """Base search query."""

    labels: list[str] | None = None
    sort_field: str | None = None
    access_permission: AccessPermission | None = None
    sort_direction: SortDirection = SortDirection.ASC

    @property
    def parsed_labels(self) -> list[Label]:
        """Parsed labels."""
        if self.labels:
            return [Label(label) for label in self.labels]
        else:
            return None
