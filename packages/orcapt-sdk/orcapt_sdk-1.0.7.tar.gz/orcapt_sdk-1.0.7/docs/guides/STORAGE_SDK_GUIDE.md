# Storage SDK Guide

Complete guide to using Orca Storage SDK and building custom storage integrations.

## Table of Contents

- [Overview](#overview)
- [Using Python SDK](#using-python-sdk)
- [API Reference](#api-reference)
- [Building Custom SDKs](#building-custom-sdks)
- [Best Practices](#best-practices)

## Overview

Orca Storage provides a workspace-scoped API for file storage with S3-compatible interface. The Python SDK (`OrcaStorage`) is included in the `orca` package and provides a simple, unified interface for storage operations.

### Features

- ✅ File operations (upload, download, list, delete)
- ✅ Pre-signed URLs
- ✅ Metadata & tagging
- ✅ Folder organization

### Architecture

```
┌─────────────────┐
│   Your App      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  OrcaStorage   │ (Python SDK)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Storage API    │ (REST API)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  S3 / Spaces    │ (Backend)
└─────────────────┘
```

## Using Python SDK

### Installation

The storage SDK is included with `orca`:

```bash
pip install orca
```

### Quick Start

```python
from orca import OrcaStorage

# Initialize client
storage = OrcaStorage(
    workspace="my-workspace",
    token="your-api-token",
    base_url="https://api.example.com/api/v1/storage",
    mode="prod"  # or "dev"
)

# Upload file
file = storage.upload_file(
    "my-bucket",
    "path/to/local/file.jpg",
    folder="uploads/2025"
)

# Get download URL
url = storage.get_download_url("my-bucket", "uploads/2025/file.jpg")
print(f"Download: {url['download_url']}")

# List files
files = storage.list_files("my-bucket", folder="uploads/2025")
for file in files['files']:
    print(f"- {file['key']} ({file['size']} bytes)")
```

### File Operations

#### Upload File

```python
# Upload from file path
file = storage.upload_file(
    bucket="reports",
    file_path="/path/to/report.pdf",
    folder="2025/january",
    visibility="private",
    metadata={"author": "John", "dept": "Sales"},
    tags=["report", "q1"]
)

print(f"Uploaded: {file['key']}")
print(f"URL: {file['download_url']}")
```

#### Upload from Buffer

```python
import io

data = b"Hello, World!"
buffer = io.BytesIO(data)

file = storage.upload_buffer(
    bucket="documents",
    buffer=buffer,
    filename="hello.txt",
    folder="greetings"
)
```

#### List Files

```python
# List all files
result = storage.list_files("reports")

# With pagination
result = storage.list_files(
    bucket="reports",
    folder="2025",
    page=1,
    per_page=50
)

for file in result['files']:
    print(f"{file['key']} - {file['size']} bytes")

print(f"Page {result['pagination']['current_page']} of {result['pagination']['total_pages']}")
```

#### Download File

```python
# Download to file
storage.download_file(
    bucket="reports",
    key="2025/january/report.pdf",
    destination="/local/path/report.pdf"
)

# Get download URL (expires in 60 minutes)
url_info = storage.get_download_url(
    bucket="reports",
    key="2025/january/report.pdf"
)
print(f"URL: {url_info['download_url']}")
print(f"Expires: {url_info['expires_at']}")
```

#### Get File Info

```python
info = storage.get_file_info("reports", "2025/january/report.pdf")
print(f"Size: {info['size']}")
print(f"Type: {info['content_type']}")
print(f"Modified: {info['last_modified']}")
```

#### Delete File

```python
storage.delete_file("reports", "2025/january/report.pdf")
```

## API Reference

### OrcaStorage

```python
class OrcaStorage:
    def __init__(
        self,
        workspace: str,
        token: str,
        base_url: str,
        mode: str = "prod"
    )
```

**Parameters:**

| Parameter   | Type  | Required | Description                        |
| ----------- | ----- | -------- | ---------------------------------- |
| `workspace` | `str` | Yes      | Workspace identifier               |
| `token`     | `str` | Yes      | API authentication token           |
| `base_url`  | `str` | Yes      | Storage API endpoint               |
| `mode`      | `str` | No       | Environment mode (`prod` or `dev`) |

### File Methods

| Method                                         | Description                |
| ---------------------------------------------- | -------------------------- |
| `upload_file(bucket, file_path, folder, ...)`  | Upload file from path      |
| `upload_buffer(bucket, buffer, filename, ...)` | Upload from memory         |
| `list_files(bucket, folder, page, per_page)`   | List files with pagination |
| `download_file(bucket, key, destination)`      | Download to local path     |
| `get_download_url(bucket, key)`                | Get pre-signed URL         |
| `get_file_info(bucket, key)`                   | Get file metadata          |
| `delete_file(bucket, key)`                     | Delete file                |

## Building Custom SDKs

If you need to build a Storage SDK for another language, follow this guide.

### API Fundamentals

**Base URL:**

```
https://your-domain.com/api/v1/storage
```

**Required Headers:**

| Header        | Value           | Description       |
| ------------- | --------------- | ----------------- |
| `x-workspace` | Workspace slug  | Tenant identifier |
| `x-token`     | API token       | Authentication    |
| `x-mode`      | `dev` or `prod` | Environment mode  |

### Core Endpoints

#### File Operations

```
POST   /{bucket}/upload
GET    /{bucket}/files?folder=path&page=1&per_page=50
GET    /{bucket}/download/{key}
GET    /{bucket}/file-info/{key}
DELETE /{bucket}/file/{key}
```

### Implementation Blueprint

```python
class CustomStorageSDK:
    def __init__(self, workspace, token, base_url, mode='prod'):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'x-workspace': workspace,
            'x-token': token,
            'x-mode': mode
        }

    def _request(self, method, path, **kwargs):
        """Centralized request handler"""
        url = f"{self.base_url}{path}"
        response = self.http_client.request(
            method=method,
            url=url,
            headers=self.headers,
            **kwargs
        )

        if not response.ok:
            error = response.json()
            raise StorageError(error['message'], error['code'])

        return response.json()

    def upload_file(self, bucket, file_path, folder='', **options):
        """Upload file (multipart)"""
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            data = {
                'folder_path': folder,
                'visibility': options.get('visibility', 'private'),
                'generate_url': 'true',
            }
            return self._request('POST', f'/{bucket}/upload',
                               data=data, files=files)

    def list_files(self, bucket, folder='', page=1, per_page=50):
        """List files with pagination"""
        params = {
            'folder_path': folder,
            'page': page,
            'per_page': per_page
        }
        return self._request('GET', f'/{bucket}/files', params=params)

    def get_download_url(self, bucket, key):
        """Get pre-signed download URL"""
        return self._request('GET', f'/{bucket}/download/{key}')
```

## Best Practices

### 1. Error Handling

```python
from orca import OrcaStorage
from orca.common.exceptions import OrcaException

storage = OrcaStorage(...)

try:
    file = storage.upload_file("bucket", "file.pdf")
except OrcaException as e:
    print(f"Storage error: {e.message}")
    print(f"Code: {e.error_code}")
```

### 2. Organize Files

```python
# Use folders for organization
storage.upload_file(
    "documents",
    "contract.pdf",
    folder=f"clients/{client_id}/contracts"
)
```

### 3. Handle Large Files

```python
# Upload in chunks for large files
with open("large-file.zip", "rb") as f:
    storage.upload_buffer(
        "backups",
        f,
        filename="large-file.zip",
        folder="2025/january"
    )
```

### 4. Cache Download URLs

```python
# URLs expire in 60 minutes
url_cache = {}

def get_cached_url(bucket, key):
    cache_key = f"{bucket}/{key}"

    if cache_key not in url_cache:
        result = storage.get_download_url(bucket, key)
        url_cache[cache_key] = {
            'url': result['download_url'],
            'expires': result['expires_at']
        }

    return url_cache[cache_key]['url']
```

## See Also

- [Developer Guide](DEVELOPER_GUIDE.md) - Complete development guide
- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Lambda Deploy Guide](LAMBDA_DEPLOY_GUIDE.md) - AWS Lambda deployment
