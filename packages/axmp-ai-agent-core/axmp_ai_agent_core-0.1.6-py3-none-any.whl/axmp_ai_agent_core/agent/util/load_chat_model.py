"""Utility & helper functions."""

import logging
from typing import Any

# from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage

logger = logging.getLogger(__name__)

CURRENT_SUPPORTED_PROVIDERS = [
    "openai",
    "anthropic",
    "google-genai",
    "bedrock",
    # "google-vertexai",
    # "xai",
    # "perplexity",
]


def get_message_text(msg: BaseMessage) -> str:
    """Get the text content of a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


def load_chat_model(
    fully_specified_name: str,
    temperature: float = 0.0,
    max_tokens: int = 5000,
    request_timeout: int = 15,
    max_retries: int = 2,
    api_key: str | None = None,
    aws_access_key_id: str | None = None,
    aws_secret_access_key: str | None = None,
    aws_region_name: str | None = None,
    base_url: str | None = None,
    organization: str | None = None,
    streaming: bool = True,
    **kwargs: Any,
) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
        temperature (float): Temperature for the model.
        max_tokens (int): Maximum tokens for the model.
    """
    if fully_specified_name.find("/") != -1:
        # NOTE: for backward compatibility, support the format 'provider/model'
        provider, model = fully_specified_name.split("/", maxsplit=1)
    elif fully_specified_name.find(":") != -1:
        # NOTE: for new format, support the format 'provider:model'
        provider, model = fully_specified_name.split(":", maxsplit=1)
    else:
        raise ValueError(
            f"Invalid fully specified name: {fully_specified_name}. Please use the format 'provider/model' or 'provider:model'."
        )

    logger.info(f"Provider: {provider} Model: {model} Temperature: {temperature}")

    # NOTE: for the unsupported providers, use the openai model if provider is compatible with openai (e.g. sk.ax)
    if provider not in CURRENT_SUPPORTED_PROVIDERS:
        logger.info(f"Using openai model for unsupported provider: {provider}")
        logger.info(f"Base URL: {base_url}")

        if base_url is None:
            raise ValueError(
                "Base URL is required for unsupported providers. Please provide a base URL."
            )

        try:
            from langchain_openai.chat_models import ChatOpenAI
        except ImportError:
            raise ImportError(
                "Could not import langchain-openai. Please install it with 'pip install langchain-openai'"
            )

        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            organization=organization,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            request_timeout=request_timeout,
            max_retries=max_retries,
            **kwargs,
        )
    else:
        if provider == "openai":
            # Check if langchain-openai is installed
            try:
                from langchain_openai.chat_models import ChatOpenAI
            except ImportError:
                raise ImportError(
                    "Could not import langchain-openai. Please install it with 'pip install langchain-openai'"
                )
            return ChatOpenAI(
                model=model,
                # api_key=api_key,
                # base_url=base_url,
                openai_api_key=api_key,
                openai_api_base=base_url,
                # organization=organization,
                temperature=temperature,
                max_tokens=max_tokens,
                streaming=streaming,
                request_timeout=request_timeout,
                max_retries=max_retries,
                output_version="responses/v1",
                use_responses_api=True,
            )
        elif provider == "anthropic":
            try:
                from langchain_anthropic.chat_models import ChatAnthropic
            except ImportError:
                raise ImportError(
                    "Could not import langchain-anthropic. Please install it with 'pip install langchain-anthropic'"
                )
            return ChatAnthropic(
                model=model,
                # api_key=api_key,
                # base_url=base_url,
                anthropic_api_key=api_key,
                anthropic_api_url=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
                streaming=streaming,
                default_request_timeout=request_timeout,
                max_retries=max_retries,
            )
        elif provider == "google-genai":
            try:
                from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
            except ImportError:
                raise ImportError(
                    "Could not import langchain-google-genai. Please install it with 'pip install langchain-google-genai'"
                )
            return ChatGoogleGenerativeAI(
                model=model,
                # api_key=api_key,
                # base_url=base_url,
                google_api_key=api_key,
                temperature=temperature,
                max_output_tokens=max_tokens,
                disable_streaming=not streaming,
                timeout=request_timeout,
                max_retries=max_retries,
            )
        elif provider == "bedrock":
            try:
                from langchain_aws.chat_models import ChatBedrock
            except ImportError:
                raise ImportError(
                    "Could not import langchain-aws. Please install it with 'pip install langchain-aws'"
                )
            return ChatBedrock(
                model_id=model,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region_name,
                streaming=streaming,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        # elif provider == "google-vertexai":
        #     try:
        #         from langchain_google_vertexai.chat_models import ChatGoogleVertexAI
        #     except ImportError:
        #         raise ImportError(
        #             "Could not import langchain-google-vertexai. Please install it with 'pip install langchain-google-vertexai'"
        #         )
        #     return ChatGoogleVertexAI(
        #         model=model,
        #         api_key=api_key,
        #         base_url=base_url,
        #         organization=organization,
        #         temperature=temperature,
        #         streaming=streaming,
        #         output_version="responses/v1",
        #         use_responses_api=True,
        #     )
        # elif provider == "xai":
        #     try:
        #         from langchain_xai.chat_models import ChatXAI
        #     except ImportError:
        #         raise ImportError(
        #             "Could not import langchain-xai. Please install it with 'pip install langchain-xai'"
        #         )
        #     return ChatXAI(
        #         model=model,
        #         api_key=api_key,
        #         base_url=base_url,
        #         organization=organization,
        #         temperature=temperature,
        #         streaming=streaming,
        #         output_version="responses/v1",
        #         use_responses_api=True,
        #     )
        # elif provider == "perplexity":
        #     try:
        #         from langchain_perplexity.chat_models import ChatPerplexity
        #     except ImportError:
        #         raise ImportError(
        #             "Could not import langchain-perplexity. Please install it with 'pip install langchain-perplexity'"
        #         )
        #     return ChatPerplexity(
        #         model=model,
        #         api_key=api_key,
        #         base_url=base_url,
        #         organization=organization,
        #         temperature=temperature,
        #         streaming=streaming,
        #         output_version="responses/v1",
        #         use_responses_api=True,
        #     )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
