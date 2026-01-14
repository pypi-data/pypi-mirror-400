"""ChatOps Agent Graph.

This graph is used to manage chatops in Axmp AI Agent Studio.
"""

import logging
from datetime import UTC, datetime
from functools import partial
from typing import Dict, List, Literal, cast

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.prompts import (
    load_prompt,
)
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from langgraph.store.base import BaseStore

from axmp_ai_agent_core.agent.configuration import Configuration
from axmp_ai_agent_core.agent.state import InputState, OverallState
from axmp_ai_agent_core.agent.util.load_chat_model import load_chat_model

logger = logging.getLogger(__name__)


async def call_model(
    state: OverallState,
    config: RunnableConfig,
    tools: list[BaseTool],
    prompt_path: str,
    system_message: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    aws_access_key_id: str | None = None,
    aws_secret_access_key: str | None = None,
    aws_region_name: str | None = None,
    max_tokens: int = 5000,
    temperature: float = 0.0,
) -> Dict[str, List[AIMessage]]:
    """Call the LLM powering our "agent".

    This function prepares the prompt, initializes the model, and processes the response.

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.
        tools (list[BaseTool]): The tools to use.
        prompt_path (str): The path to the prompt file.
        system_message (str | None): The system message to use.
        base_url (str | None): The base URL to use.
        api_key (str | None): The API key to use.
        max_tokens (int): The maximum number of tokens to use. Default is 5000.
        temperature (float): The temperature to use. Default is 0.0.

    Returns:
        dict: A dictionary containing the model's response message.
    """
    configuration = Configuration.from_runnable_config(config)

    logger.info(f"Configuration: {configuration}")

    model: BaseChatModel = load_chat_model(
        fully_specified_name=configuration.provider_and_model,
        api_key=api_key or None,
        base_url=base_url or None,
        aws_access_key_id=aws_access_key_id or None,
        aws_secret_access_key=aws_secret_access_key or None,
        aws_region_name=aws_region_name or None,
        max_tokens=max_tokens,
        temperature=temperature,
    ).bind_tools(tools)

    # if system message is not provided, create a system message
    if not state.messages or not isinstance(state.messages[0], SystemMessage):
        if system_message is not None:
            system_message = SystemMessage(
                content=f"{system_message}\n\nSystem Time: {datetime.now(tz=UTC).isoformat()}"
            )
        else:
            try:
                system_message = SystemMessage(
                    content=load_prompt(prompt_path).format(
                        system_time=datetime.now(tz=UTC).isoformat(),
                    )
                )
            except Exception as e:
                logger.error(f"Error loading system message: {e}")
                system_message = SystemMessage(
                    content="You are a helpful assistant. Please answer the question."
                )
        messages = [system_message, *state.messages]
    else:
        messages = state.messages

    # Get the model's response
    response = cast(
        AIMessage,
        await model.ainvoke(messages, config),
    )

    logger.debug(f"Response: {response}")

    # Handle the case when it's the last step and the model still wants to use a tool
    if state.is_last_step and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, I could not find an answer to your question in the specified number of steps.",
                )
            ]
        }

    # Return the model's response as a list to be added to existing messages
    return {"messages": [response]}


async def create_langgraph_agent(
    *,
    tools: list[BaseTool],
    checkpointer: BaseCheckpointSaver,
    store: BaseStore,
    agent_name: str,
    prompt_path: str,
    system_message: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    aws_access_key_id: str | None = None,
    aws_secret_access_key: str | None = None,
    aws_region_name: str | None = None,
    max_tokens: int = 5000,
    temperature: float = 0.0,
) -> CompiledStateGraph:
    """Build the graph."""
    builder = StateGraph(
        state_schema=OverallState,
        config_schema=Configuration,
        input=InputState,
    )

    # Define the two nodes we will cycle between
    builder.add_node(
        "call_model",
        partial(
            call_model,
            tools=tools,
            prompt_path=prompt_path,
            system_message=system_message,
            base_url=base_url,
            api_key=api_key,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_region_name=aws_region_name,
            max_tokens=max_tokens,
            temperature=temperature,
        ),
    )
    builder.add_node("tools", ToolNode(tools))

    # Set the entrypoint as `call_model`
    # This means that this node is the first one called
    builder.add_edge("__start__", "call_model")

    def route_model_output(state: OverallState) -> Literal["__end__", "tools"]:
        """Determine the next node based on the model's output.

        This function checks if the model's last message contains tool calls.

        Args:
            state (State): The current state of the conversation.

        Returns:
            str: The name of the next node to call ("__end__" or "tools").
        """
        last_message = state.messages[-1]
        if not isinstance(last_message, AIMessage):
            raise ValueError(
                f"Expected AIMessage in output edges, but got {type(last_message).__name__}"
            )
        # If there is no tool call, then we finish
        if not last_message.tool_calls:
            return "__end__"
        # Otherwise we execute the requested actions
        return "tools"

    # Add a conditional edge to determine the next step after `call_model`
    builder.add_conditional_edges(
        "call_model",
        route_model_output,
    )

    # Add a normal edge from `tools` to `call_model`
    # This creates a cycle: after using tools, we always return to the model
    builder.add_edge("tools", "call_model")

    # Compile the builder into an executable graph
    graph_workflow = builder.compile(
        interrupt_before=[],
        interrupt_after=[],
        checkpointer=checkpointer,
        store=store,
    )
    graph_workflow.name = agent_name

    return graph_workflow
