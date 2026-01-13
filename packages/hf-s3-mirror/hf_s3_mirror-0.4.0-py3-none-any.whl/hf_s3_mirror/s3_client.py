"""S3 client configuration and operations."""

import os
from pathlib import Path

import s3fs
from dotenv import load_dotenv
from tqdm import tqdm

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


def _format_size(size_bytes: int) -> str:
    """Format bytes to human readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"


def upload_to_s3(local_path: Path, s3_path: str, s3: s3fs.S3FileSystem) -> None:
    """Upload local directory or file to S3 with progress bar."""
    if local_path.is_dir():
        files = [f for f in local_path.rglob("*") if f.is_file()]
        total_size = sum(f.stat().st_size for f in files)

        with tqdm(total=total_size, unit="B", unit_scale=True, desc="Uploading") as pbar:
            for file in files:
                rel_path = file.relative_to(local_path)
                target = f"{s3_path}/{rel_path}".replace("//", "/")
                file_size = file.stat().st_size
                s3.put(str(file), target)
                pbar.update(file_size)
    else:
        file_size = local_path.stat().st_size
        with tqdm(total=file_size, unit="B", unit_scale=True, desc="Uploading") as pbar:
            s3.put(str(local_path), s3_path)
            pbar.update(file_size)


def download_from_s3(s3_path: str, local_path: Path, s3: s3fs.S3FileSystem) -> None:
    """Download from S3 to local directory."""
    s3.get(s3_path, lpath=str(local_path), recursive=True)
