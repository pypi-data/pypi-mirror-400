"""S3 client configuration and operations."""

import os
from pathlib import Path

import s3fs
from dotenv import load_dotenv

load_dotenv()


def get_s3_client() -> s3fs.S3FileSystem:
    """Create and return configured S3 client."""
    return s3fs.S3FileSystem(
        anon=False,
        key=os.getenv("S3_ACCESS_KEY"),
        secret=os.getenv("S3_SECRET_KEY"),
        endpoint_url=os.getenv("S3_ENDPOINT_URL"),
        use_ssl=os.getenv("S3_USE_SSL", "false").lower() == "true",
        client_kwargs={"region_name": os.getenv("S3_REGION", "ru-1")},
    )


def get_default_bucket() -> str:
    """Get default S3 bucket from environment."""
    return os.getenv("S3_BUCKET", "model-bucket")


def upload_to_s3(local_path: Path, s3_path: str, s3: s3fs.S3FileSystem) -> None:
    """Upload local directory or file to S3."""
    if local_path.is_dir():
        s3.put(str(local_path) + "/*", s3_path, recursive=True)
    else:
        s3.put(str(local_path), s3_path)


def download_from_s3(s3_path: str, local_path: Path, s3: s3fs.S3FileSystem) -> None:
    """Download from S3 to local directory."""
    s3.get(s3_path, lpath=str(local_path), recursive=True)
