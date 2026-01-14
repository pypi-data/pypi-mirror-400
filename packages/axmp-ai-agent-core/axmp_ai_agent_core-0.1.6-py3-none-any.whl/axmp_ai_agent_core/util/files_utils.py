"""File utilities."""

from fastapi import UploadFile

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
IMAGE_MIME_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}

FILE_EXTENSIONS = {".pdf"}
FILE_MIME_TYPES = {"application/pdf"}


async def check_image_file_limit(file: UploadFile, image_max_size_mb: int = 3) -> bytes:
    """Check if the file is an image and if it's within the size limit."""
    filename = file.filename
    ext = filename[filename.rfind(".") :].lower()
    content_type = file.content_type
    file_bytes = await file.read()
    size = len(file_bytes)

    if ext not in IMAGE_EXTENSIONS or content_type not in IMAGE_MIME_TYPES:
        raise ValueError("Unsupported image format.")
    if size > image_max_size_mb * 1024 * 1024:
        raise ValueError(f"Image size must be {image_max_size_mb}MB or less.")
    return file_bytes


async def check_pdf_file_limit(file: UploadFile, pdf_max_size_mb: int = 10) -> bytes:
    """Check if the file is a PDF and if it's within the size limit."""
    filename = file.filename
    ext = filename[filename.rfind(".") :].lower()
    content_type = file.content_type
    file_bytes = await file.read()
    size = len(file_bytes)

    if ext not in FILE_EXTENSIONS or content_type not in FILE_MIME_TYPES:
        raise ValueError("Only PDF files are allowed.")
    if size > pdf_max_size_mb * 1024 * 1024:
        raise ValueError(f"File size must be {pdf_max_size_mb}MB or less.")
    return file_bytes
