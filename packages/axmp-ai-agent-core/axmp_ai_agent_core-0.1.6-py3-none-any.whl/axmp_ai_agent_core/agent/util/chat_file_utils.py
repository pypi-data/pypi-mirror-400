"""Chat file utils."""

import base64
from typing import Any, Literal

import httpx

from axmp_ai_agent_core.agent.util.load_chat_model import CURRENT_SUPPORTED_PROVIDERS
from axmp_ai_agent_core.entity.base_model import CoreBaseModel

SUPPORTED_IMAGE_MIME_TYPES = [
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/gif",
    "image/webp",
]

SUPPORTED_FILE_MIME_TYPES = [
    "application/pdf",
]


class ChatFile(CoreBaseModel):
    """Chat files model."""

    upload_url: str | None = None
    file_name: str | None = None
    mime_type: str | None = None
    project_id: str | None = None


def check_supported_image_mime_type(mime_type: str) -> bool:
    """Check if the file url is a supported image mime type."""
    return mime_type in SUPPORTED_IMAGE_MIME_TYPES


def check_supported_file_mime_type(mime_type: str) -> bool:
    """Check if the file url is a supported file mime type."""
    return mime_type in SUPPORTED_FILE_MIME_TYPES


def get_file_type(mime_type: str) -> Literal["image", "file"]:
    """Get the file type."""
    if mime_type.startswith("image/"):
        return "image"
    else:
        return "file"


# NOTE: use CURRENT_SUPPORTED_PROVIDERS instead of SUPPORTED_LLM_MODELS_PROVIDERS
# SUPPORTED_LLM_MODELS_PROVIDERS = [
#     "openai",
#     "anthropic",
#     "google_genai",
# ]


def check_supported_llm_model(llm_model: str) -> bool:
    """Check if the llm model is supported."""
    provider = llm_model.split("/")[0]
    if provider is None or provider == "":
        # NOTE: support the format 'provider:model'
        provider = llm_model.split(":")[0]
    return provider in CURRENT_SUPPORTED_PROVIDERS


def generate_multimodal_messages(
    chat_files: list[ChatFile], prompt: str, llm_model: str
) -> list[dict[str, Any]]:
    """Generate the multimodal messages."""
    messages: list[dict[str, Any]] = []
    if chat_files is None or len(chat_files) == 0:
        messages.append({"type": "text", "text": prompt})
        return messages

    if chat_files is not None and len(chat_files) > 0:
        for file in chat_files:
            if get_file_type(file.mime_type) == "image":
                if not check_supported_image_mime_type(file.mime_type):
                    raise ValueError(
                        f"Unsupported image mime type: {file.mime_type}. "
                        f"Please use one of the following mime types: {', '.join(SUPPORTED_IMAGE_MIME_TYPES)}.",
                    )
                # set the image url to the messages
                messages.append(
                    {"type": "image_url", "image_url": {"url": file.upload_url}}
                )

            else:
                if not check_supported_file_mime_type(file.mime_type):
                    raise ValueError(
                        f"Unsupported file mime type: {file.mime_type}. "
                        f"Please use one of the following mime types: {', '.join(SUPPORTED_FILE_MIME_TYPES)}.",
                    )

                if not check_supported_llm_model(llm_model):
                    raise ValueError(
                        f"Unsupported llm model: {llm_model}. "
                        f"Please use one of the following models: {', '.join(CURRENT_SUPPORTED_PROVIDERS)}.",
                    )

                # download the file from the upload url
                file_data = httpx.get(file.upload_url).content
                # encode and decode the file data to base64
                base64_data = base64.b64encode(file_data).decode("utf-8")
                if llm_model.startswith("openai/"):
                    messages.append(
                        {
                            "type": "file",
                            "file": {
                                "filename": file.file_name,
                                "file_data": f"data:{file.mime_type};base64,{base64_data}",
                                "file_url": file.upload_url,
                            },
                        }
                    )
                else:
                    messages.append(
                        {
                            "type": "file",
                            "source_type": "base64",
                            "mime_type": file.mime_type,
                            "data": base64_data,
                            "filename": file.file_name,
                            "file_url": file.upload_url,
                        }
                    )

        messages.append({"type": "text", "text": prompt})

    return messages
