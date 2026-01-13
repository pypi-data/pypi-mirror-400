# hf-s3-mirror

CLI tool for mirroring HuggingFace models to S3-compatible storage.

## Installation

```bash
pip install hf-s3-mirror
```

## Configuration

Create `.env` file in your working directory:

```bash
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
S3_ENDPOINT_URL=http://your-s3-endpoint
S3_REGION=ru-1
S3_BUCKET=model-bucket
S3_USE_SSL=false
```

Or export environment variables:

```bash
export S3_ACCESS_KEY=your_access_key
export S3_SECRET_KEY=your_secret_key
export S3_ENDPOINT_URL=http://your-s3-endpoint
export S3_REGION=ru-1
export S3_BUCKET=model-bucket
```

## Usage

### Upload model from HuggingFace to S3

```bash
# Basic usage
hf-s3 upload openai/whisper-large-v3

# With custom bucket and prefix
hf-s3 upload lab-ii/whisper-large-v3 -b my-bucket -p models/
```

### Upload local directory to S3

```bash
hf-s3 upload-local ./my-model -b model-bucket -p models/
```

### Download model from S3 mirror

```bash
hf-s3 download lab-ii/whisper-large-v3 -o ./models
```

### List bucket contents

```bash
# List root
hf-s3 list-bucket

# List specific path
hf-s3 list-bucket -p models--lab-ii--whisper-large-v3
```

### Delete model from S3

```bash
# By repo_id (will ask for confirmation)
hf-s3 delete lab-ii/whisper-large-v3

# By direct path
hf-s3 delete models--lab-ii--whisper-large-v3

# Skip confirmation (for scripts)
hf-s3 delete lab-ii/bad-model --force
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `upload <repo_id>` | Download from HuggingFace and upload to S3 |
| `upload-local <path>` | Upload local directory to S3 |
| `download <repo_id>` | Download from S3 mirror to local |
| `list-bucket` | List S3 bucket contents |
| `delete <path>` | Delete folder from S3 (with confirmation) |

## Common Options

| Option | Short | Description |
|--------|-------|-------------|
| `--bucket` | `-b` | S3 bucket name (overrides env) |
| `--prefix` | `-p` | S3 prefix path |
| `--help` | | Show command help |

## S3 Storage Structure

Models are stored with the following naming convention:

```
bucket/
  models--organization--model-name/
    config.json
    model.bin
    tokenizer.json
    ...
```

## License

Apache 2.0
