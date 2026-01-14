"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Annotated, Any

from langchain_core.runnables import RunnableConfig, ensure_config


@dataclass(kw_only=True)
class Configuration:
    """The configuration for the agent."""

    user_id: str = field(
        default="",
        metadata={
            "description": "The user ID to use for the agent's interactions. "
            "This ID is used to identify the user and their interactions with the agent."
        },
    )

    thread_id: str = field(
        default="",
        metadata={
            "description": "The thread ID to use for the agent's interactions. "
            "This ID is used to identify the thread and its interactions with the agent."
        },
    )

    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="openai/gpt-4.1-mini",
        metadata={
            "description": "The name of the language model to use for the agent's main interactions. "
            "Should be in the form: provider/model-name."
        },
    )

    provider_and_model: str = field(
        default="",
        metadata={
            "description": "The provider and model to use for the agent's main interactions. "
            "Should be in the form: provider:model-name."
        },
    )

    max_tokens: int = field(
        default=5000,
        metadata={
            "description": "The maximum number of output tokens to use for the language model."
        },
    )

    temperature: float = field(
        default=0.0,
        metadata={"description": "The temperature to use for the language model."},
    )

    system_message: str = field(
        default="",
        metadata={
            "description": "The system message to use for the agent's interactions."
        },
    )

    streaming: bool = field(
        default=True,
        metadata={
            "description": "Whether to use streaming for the language model. "
            "If True, the language model will stream the output."
        },
    )

    # Deprecated
    language: str = field(
        default="English",
        metadata={
            "description": "The language to use for generating reports. "
            "This language is used in the report generation prompt."
        },
    )

    @classmethod
    def from_runnable_config(
        cls, config: RunnableConfig | None = None
    ) -> Configuration:
        """Create a Configuration instance from a RunnableConfig object."""
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})

    def model_dump(self) -> dict[str, Any]:
        """Dump the configuration to a dictionary."""
        return {f.name: getattr(self, f.name) for f in fields(self) if f.init}
