"""Local storage utilities."""

import os
from typing import List

from axmp_ai_agent_studio.entity.image_upload_target import ImageUploadTarget
from axmp_ai_agent_studio.setting import studio_settings
from axmp_ai_agent_studio.util.files_utils import IMAGE_EXTENSIONS


async def upload_file_to_local_storage(
    file_bytes: bytes,
    filename: str,
    image_type: ImageUploadTarget,
) -> str:
    """Upload a file to local storage and return the full URL."""
    image_dir = f"{studio_settings.image_path}/{image_type.value}"

    base_name, extension = os.path.splitext(filename)
    unique_filename = filename

    # If the file already exists, add a number to the filename
    full_file_path = os.path.join(image_dir, unique_filename)
    counter = 1

    while os.path.exists(full_file_path):
        unique_filename = f"{base_name}_{counter}{extension}"
        full_file_path = os.path.join(image_dir, unique_filename)
        counter += 1

    with open(full_file_path, "wb") as file:
        file.write(file_bytes)

    return (
        f"{studio_settings.image_server_endpoint}/{image_type.value}/{unique_filename}"
    )


async def setup_default_images():
    """Set up default images."""
    for image_type in ImageUploadTarget.get_all_targets():
        default_image_dir = f"{studio_settings.default_image_path}/{image_type}"
        public_image_dir = f"{studio_settings.image_path}/{image_type}"

        if not os.path.exists(public_image_dir):
            os.makedirs(public_image_dir)

        for filename in os.listdir(default_image_dir):
            default_image_path = os.path.join(default_image_dir, filename)
            public_image_path = os.path.join(public_image_dir, filename)
            if os.path.isfile(default_image_path):
                with open(default_image_path, "rb") as file:
                    file_bytes = file.read()
                    with open(public_image_path, "wb") as public_file:
                        public_file.write(file_bytes)


async def setup_icon_template() -> List[dict]:
    """List icon template image URLs under the configured icon template directory."""
    root_dir = studio_settings.icon_template_path
    if not os.path.isdir(root_dir):
        fallback_dir = os.path.join(os.getcwd(), "public", "images", "icon-templates")
        if os.path.isdir(fallback_dir):
            root_dir = fallback_dir
        else:
            return []

    items: List[dict] = []
    for dirpath, _dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in IMAGE_EXTENSIONS:
                continue
            abs_path = os.path.join(dirpath, filename)
            rel_path = abs_path.replace(root_dir, "").lstrip("/\\")
            web_path = f"icon-templates/{rel_path}".replace("\\", "/")
            full_url = f"{studio_settings.image_server_endpoint}/{web_path}"
            items.append({"icon_url": full_url})

    return items
