# Graphon Client - Developer Documentation

This is the internal README for the Graphon client library development.

For the public-facing README (published to PyPI), see `PUBLIC_README.md`.

## Project Structure

```
graphon_client/
├── graphon_client/
│   ├── __init__.py          # Package exports
│   └── client.py            # Main client implementation
├── PUBLIC_README.md         # Public documentation (published to PyPI)
├── README.md               # This file (internal docs)
├── pyproject.toml          # Package configuration
└── test_graphon_client.py  # Test suite and examples
```

## Development Setup

### 1. Install in Development Mode

From the `graphon_client` directory:

```bash
pip install -e .
```

This installs the package in editable mode, so changes are reflected immediately.

### 2. Set API Key

Get an API key from the Graphon dashboard and set it as an environment variable:

```bash
export GRAPHON_API_KEY="your_api_key_here"
```

### 3. Run Tests

Edit `test_graphon_client.py` and uncomment one of the example workflows at the bottom:

```bash
python test_graphon_client.py
```

## Testing Locally

### Quick Test Script

Create a file `test_local.py`:

```python
import asyncio
from graphon_client import GraphonClient

async def test():
    client = GraphonClient(api_key="your_api_key_here")
    
    # Test with a small file
    files = ["/path/to/test.pdf"]
    
    file_objects = await client.upload_and_process_files(
        files,
        poll_until_complete=True
    )
    
    print(f"✅ Uploaded: {file_objects}")
    
    # Create group
    group_id = await client.create_group(
        [f.file_id for f in file_objects],
        "Test Group",
        wait_for_ready=True
    )
    
    print(f"✅ Group created: {group_id}")
    
    # Query
    response = await client.query_group(group_id, "Summarize this")
    print(f"✅ Answer: {response.answer}")

asyncio.run(test())
```

### Using Different Environments

```python
# Production (default)
client = GraphonClient(api_key="sk_live_...")

# Development/Staging
client = GraphonClient(
    api_key="sk_test_...",
    base_url="http://localhost:8081"
)
```

## Building and Publishing

### 1. Update Version

Edit `pyproject.toml`:

```toml
version = "0.2.1"  # Increment version
```

### 2. Build Package

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build
python -m build
```

This creates:
- `dist/graphon_client-0.2.0-py3-none-any.whl` (wheel)
- `dist/graphon-client-0.2.0.tar.gz` (source distribution)

### 3. Test Installation

Test the built package in a clean virtual environment:

```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate

# Install from local build
pip install dist/graphon_client-0.2.0-py3-none-any.whl

# Test import
python -c "from graphon_client import GraphonClient; print('✅ Import successful')"

# Clean up
deactivate
rm -rf test_env
```

### 4. Publish to PyPI

```bash
# Install twine if needed
pip install twine

# Upload to PyPI
python -m twine upload dist/*
```

You'll be prompted for your PyPI credentials.

### 5. Verify Published Package

```bash
# In a new environment
pip install graphon-client==0.2.0

# Test
python -c "from graphon_client import GraphonClient; print(GraphonClient.__doc__)"
```

## API Architecture

### Authentication Flow

```
User → GraphonClient (X-API-Key) → BFF API → Workflow Backend
```

- Client uses API key authentication (`X-API-Key` header)
- BFF validates API key and forwards requests to backend
- Backend processes files and builds knowledge graphs

### File Processing Flow

```
1. get_signed_upload_url()
   ↓
2. upload_to_gcs()
   ↓
3. process_file()
   ↓
4. poll_file_until_complete()
   ↓
5. create_group()
   ↓
6. poll_group_until_ready()
   ↓
7. query_group()
```

### Response Models

All API responses are typed with dataclasses:

- `FileObject`: Simplified file representation
- `FileDetail`: Complete file metadata
- `GroupDetail`: Complete group metadata
- `QueryResponse`: Query result with answer and sources

## Code Style

- Use `async`/`await` for all I/O operations
- Type hints for all public methods
- Docstrings for all public methods (Google style)
- Log important operations at INFO level
- Raise descriptive exceptions with context

## Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Now all httpx and client logs will be visible
```

### Common Issues

**401 Unauthorized**: Check API key is valid and active

**403 Forbidden**: API key doesn't have permission for this operation

**404 Not Found**: File/group doesn't exist or doesn't belong to you

**400 Bad Request**: Usually validation error (check file size, status, etc.)

**Timeout**: Increase timeout or check file/group status manually

## Version History

### 0.2.0 (Current)
- ✨ Complete rewrite for new BFF API architecture
- ✨ API key authentication
- ✨ Automatic file type detection
- ✨ Built-in polling methods
- ✨ Response dataclasses
- ✨ One-shot convenience method
- 💥 Breaking changes from v0.1.x (see migration guide in PUBLIC_README.md)

### 0.1.8 (Legacy)
- Bearer token authentication
- Manual upload URL generation
- UUID-based group creation

## Contributing

1. Create feature branch from `main`
2. Make changes
3. Test locally with `test_graphon_client.py`
4. Update `PUBLIC_README.md` if adding features
5. Bump version in `pyproject.toml`
6. Create PR

## Support

For internal questions, contact the backend team.

For user-facing issues, see PUBLIC_README.md for support channels.
