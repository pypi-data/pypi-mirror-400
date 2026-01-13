"""CLI interface for HuggingFace to S3 mirror."""

import tempfile
from pathlib import Path
from typing import Optional

import typer
from huggingface_hub import snapshot_download

from .s3_client import (
    download_from_s3,
    get_default_bucket,
    get_s3_client,
    upload_to_s3,
)

app = typer.Typer(
    name="hf-s3",
    help="CLI tool for mirroring HuggingFace models to S3 storage",
)


@app.command()
def upload(
    repo_id: str = typer.Argument(..., help="HuggingFace repository ID (e.g., 'lab-ii/whisper-large-v3')"),
    bucket: Optional[str] = typer.Option(None, "--bucket", "-b", help="S3 bucket name"),
    prefix: str = typer.Option("", "--prefix", "-p", help="S3 prefix path"),
) -> None:
    """Download model from HuggingFace and upload to S3."""
    bucket = bucket or get_default_bucket()
    model_name = "models--" + repo_id.replace("/", "--")
    s3_path = f"s3://{bucket}/{prefix}/{model_name}".replace("//", "/").replace("s3:/", "s3://")

    typer.echo(f"Downloading {repo_id} from HuggingFace...")

    with tempfile.TemporaryDirectory() as tmpdir:
        local_dir = Path(tmpdir)
        snapshot_download(repo_id=repo_id, local_dir=str(local_dir))
        _upload_to_s3(local_dir, s3_path)

    typer.echo(f"Successfully uploaded {repo_id} to {s3_path}")


def _upload_to_s3(local_dir: Path, s3_path: str) -> None:
    """Upload local directory to S3."""
    s3 = get_s3_client()

    typer.echo(f"Uploading to {s3_path}...")
    upload_to_s3(local_dir, s3_path, s3)


@app.command()
def upload_local(
    local_path: str = typer.Argument(..., help="Local directory path to upload"),
    bucket: Optional[str] = typer.Option(None, "--bucket", "-b", help="S3 bucket name"),
    prefix: str = typer.Option("", "--prefix", "-p", help="S3 prefix path"),
) -> None:
    """Upload local directory to S3."""
    bucket = bucket or get_default_bucket()
    s3_path = f"s3://{bucket}/{prefix}".rstrip("/") + "/"

    local_dir = Path(local_path)
    if not local_dir.exists():
        typer.echo(f"Error: {local_path} does not exist", err=True)
        raise typer.Exit(1)

    s3 = get_s3_client()

    typer.echo(f"Uploading {local_path} to {s3_path}...")
    upload_to_s3(local_dir, s3_path, s3)
    typer.echo(f"Successfully uploaded to {s3_path}")


@app.command()
def download(
    repo_id: str = typer.Argument(..., help="Repository ID to download (e.g., 'lab-ii/whisper-large-v3')"),
    local_path: str = typer.Option(".", "--output", "-o", help="Local output directory"),
    bucket: Optional[str] = typer.Option(None, "--bucket", "-b", help="S3 bucket name"),
    prefix: str = typer.Option("", "--prefix", "-p", help="S3 prefix path"),
) -> None:
    """Download model from S3 mirror to local directory."""
    bucket = bucket or get_default_bucket()
    model_name = "models--" + repo_id.replace("/", "--")
    s3_url = f"s3://{bucket}/{prefix}/{model_name}".replace("//", "/").replace("s3:/", "s3://")

    local_dir = Path(local_path)
    local_dir.mkdir(parents=True, exist_ok=True)

    s3 = get_s3_client()

    typer.echo(f"Downloading from {s3_url}...")
    download_from_s3(s3_url, local_dir, s3)
    typer.echo(f"Successfully downloaded to {local_dir}")


@app.command()
def list_bucket(
    bucket: Optional[str] = typer.Option(None, "--bucket", "-b", help="S3 bucket name"),
    prefix: str = typer.Option("", "--prefix", "-p", help="S3 prefix path"),
) -> None:
    """List contents of S3 bucket."""
    bucket = bucket or get_default_bucket()
    s3_path = f"{bucket}/{prefix}".rstrip("/")

    s3 = get_s3_client()

    try:
        contents = s3.ls(s3_path)
        for item in contents:
            typer.echo(item)
    except Exception as e:
        typer.echo(f"Error listing bucket: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def delete(
    path: str = typer.Argument(..., help="Path to delete (e.g., 'models--lab-ii--whisper' or repo_id 'lab-ii/whisper')"),
    bucket: Optional[str] = typer.Option(None, "--bucket", "-b", help="S3 bucket name"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete folder from S3 bucket."""
    bucket = bucket or get_default_bucket()

    # Convert repo_id format to S3 path format
    if "/" in path and not path.startswith("models--"):
        path = "models--" + path.replace("/", "--")

    s3_path = f"{bucket}/{path}"
    s3 = get_s3_client()

    # Check if path exists and list contents
    try:
        contents = s3.ls(s3_path)
        if not contents:
            typer.echo(f"Path not found: {s3_path}", err=True)
            raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo(f"Path not found: {s3_path}", err=True)
        raise typer.Exit(1)

    # Show what will be deleted
    typer.echo(f"\nWill delete: {s3_path}")
    typer.echo(f"Contents ({len(contents)} items):")
    for item in contents[:10]:
        typer.echo(f"  - {item}")
    if len(contents) > 10:
        typer.echo(f"  ... and {len(contents) - 10} more items")

    # Confirmation
    if not force:
        confirm = typer.confirm("\nAre you sure you want to delete?")
        if not confirm:
            typer.echo("Cancelled")
            raise typer.Exit(0)

    # Delete
    try:
        s3.rm(s3_path, recursive=True)
        typer.echo(f"Successfully deleted {s3_path}")
    except Exception as e:
        typer.echo(f"Error deleting: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
