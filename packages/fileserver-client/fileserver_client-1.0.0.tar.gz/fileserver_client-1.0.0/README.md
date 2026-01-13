# FileServer Python Client

A Python client library for interacting with the FileServer API.

## Installation

```bash
pip install fileserver-client
```

## Usage

```python
from fileserver_client import FileServerClient

# Initialize
client = FileServerClient("http://localhost:30815", "admin", "adminpassword")

# List files
files = client.list_files()
print(files)

# Upload
client.upload_file("local_file.txt")
```

## Features
- Authentication (JWT)
- File Management (List, Upload, Download)
- Easy to use Pythonic interface
