"""S3 utils."""

from datetime import datetime
from uuid import uuid4

from boto3.session import Session

from axmp_ai_agent_core.setting import s3_settings
from axmp_ai_agent_core.util.time_utils import DEFAULT_TIME_ZONE


def upload_file_to_s3(
    file_bytes: bytes, filename: str, content_type: str = "application/octet-stream"
) -> str:
    """Upload a file to S3 and return the URL."""
    yyyymm = datetime.now(DEFAULT_TIME_ZONE).strftime("%Y%m")
    ext = filename.split(".")[-1] if "." in filename else "bin"
    s3_key = f"images/{yyyymm}/{uuid4().hex}.{ext}"

    session = Session()
    s3 = session.client(
        "s3",
        aws_access_key_id=s3_settings.access_key_id,
        aws_secret_access_key=s3_settings.secret_access_key,
        region_name=s3_settings.default_region,
    )
    s3.put_object(
        Bucket=s3_settings.s3_bucket_name,
        Key=s3_key,
        Body=file_bytes,
        ContentType=content_type,
    )

    url = f"https://{s3_settings.s3_bucket_name}.s3.{s3_settings.default_region}.amazonaws.com/{s3_key}"

    return url
