# VectorBridge Python SDK

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

A modern Python SDK for the [VectorBridge.ai](https://vectorbridge.ai) API with first‑class support for both synchronous and asynchronous usage. Access authentication, user/admin operations, AI knowledge management, vector queries, workflows, history tracking, OTP authentication, and more.

## Installation

```bash
pip install vector-bridge
```

## Choose Sync or Async

- Sync client: `VectorBridgeClient`
- Async client: `AsyncVectorBridgeClient`
- Factory: `create_client(async_client: bool = False, **kwargs)`

```python
from vector_bridge import VectorBridgeClient, AsyncVectorBridgeClient, create_client
```

## Quick Start (Sync)

```python
from vector_bridge import VectorBridgeClient

# API key auth (application access)
client = VectorBridgeClient(integration_name="default", api_key="your_api_key")
print(client.ping())  # "OK"

# Or username/password (admin access)
admin = VectorBridgeClient(integration_name="default")
admin.login(username="your_email@example.com", password="your_password")
print(admin.ping())
```

## Quick Start (Async)

```python
import asyncio
from vector_bridge import AsyncVectorBridgeClient

async def main():
    async with AsyncVectorBridgeClient(integration_name="default", api_key="your_api_key") as client:
        print(await client.ping())  # "OK"

        # Or login
        # await client.login(username="your_email@example.com", password="your_password")

asyncio.run(main())
```

## Using the Factory

```python
from vector_bridge import create_client

# Sync
client = create_client(integration_name="default", api_key="your_api_key")

# Async
async_client = create_client(integration_name="default", api_key="your_api_key", async_client=True)
```

## History Tracking

Track changes to items, users, and integrations with comprehensive history endpoints:

```python
from vector_bridge.schema.helpers.enums import ItemType, HistoryChangeType

# Sync - Get history for a specific item
history = client.history.get_item_history(
    item_id="item123",
    item_type=ItemType.FILE,
    limit=50
)

# Get all history for current integration
history = client.history.get_integration_history(
    limit=50,
    item_type=ItemType.FOLDER,
    change_type=HistoryChangeType.CREATED
)

# Get history by user
history = client.history.get_user_history(
    user_id="user123",
    limit=25
)

# Get my activity
my_activity = client.history.get_my_activity(limit=25)

# Delete history entries
client.history.delete_history_entry(
    history_id="hist123",
    item_id="item123",
    item_type=ItemType.FILE
)

# Async equivalents
# await client.history.get_item_history(...)
# await client.history.get_integration_history(...)
# await client.history.get_user_history(...)
# await client.history.get_my_activity(...)
# await client.history.delete_history_entry(...)
```

## OTP Authentication

Generate and validate one-time passwords for authentication:

```python
# Sync - Generate OTP for login
response = client.otp.generate_otp(email="user@example.com")

# Validate OTP and get token
token = client.otp.validate_otp(email="user@example.com", code="123456")

# Generate sign-up code
response = client.otp.generate_sign_up_code(email="newuser@example.com")

# Validate sign-up code
client.otp.validate_sign_up_code(email="newuser@example.com", code="123456")

# Reset password
client.otp.reset_password(
    email="user@example.com",
    code="123456",
    password="new_secure_password"
)

# Async equivalents
# await client.otp.generate_otp(...)
# await client.otp.validate_otp(...)
# await client.otp.generate_sign_up_code(...)
# await client.otp.validate_sign_up_code(...)
# await client.otp.reset_password(...)
```


## Vector Queries

```python
from weaviate.collections.classes.filters import Filter

# Sync search
search = client.queries.run_search_query(
    vector_schema="Documents",
    near_text="attention mechanism",
    limit=5,
)

# Sync find similar
# from uuid import UUID
# similar = client.queries.run_find_similar_query(
#     vector_schema="Documents",
#     near_id=UUID("8c03ff2f-36f9-45f7-9918-48766c968f45"),
#     limit=5,
# )

# Async equivalents
# await client.queries.run_search_query(...)
# await client.queries.run_find_similar_query(...)
```

## Workflows

Workflows provide multi‑step processes with status tracking, output capture, caching, and error handling. Both sync and async modes are available.

### Sync Workflow

```python
from vector_bridge import VectorBridgeClient
from vector_bridge.schema.workflows import WorkflowCreate, WorkflowStatus
from vector_bridge.sync_io.client.workflows import Workflow, workflow_runner, cache_result


class ReportWorkflow(Workflow):
    @workflow_runner
    def run(self, user_id: str):
        data = self.fetch(user_id)
        return self.process(data)

    @cache_result
    def fetch(self, user_id: str):
        return client.queries.run_search_query("Documents", near_text="summary", limit=3)

    @cache_result
    def process(self, data):
        # Process the query results
        return {"report": data, "processed": True}


client = VectorBridgeClient(integration_name="default", api_key="your_api_key")
wf = ReportWorkflow(client, WorkflowCreate(workflow_id="wf_1", workflow_name="Report", status=WorkflowStatus.PENDING))
result = wf.run("user123")
```

### Async Workflow

```python
import asyncio
from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.workflows import WorkflowCreate, WorkflowStatus
from vector_bridge.async_io.client.workflows import AsyncWorkflow, async_workflow_runner, async_cache_result


class AsyncReportWorkflow(AsyncWorkflow):
    @async_workflow_runner
    async def run(self, user_id: str):
        data = await self.fetch(user_id)
        return await self.process(data)

    @async_cache_result
    async def fetch(self, user_id: str):
        return await client.queries.run_search_query("Documents", near_text="summary", limit=3)

    @async_cache_result
    async def process(self, data):
        # Process the query results
        return {"report": data, "processed": True}


async def main():
    async with AsyncVectorBridgeClient(integration_name="default", api_key="your_api_key") as client:
        wf = AsyncReportWorkflow(
            client,
            WorkflowCreate(workflow_id="wf_1", workflow_name="Report", status=WorkflowStatus.PENDING)
        )
        await wf.initialize()
        result = await wf.run("user123")


asyncio.run(main())
```

## Client Highlights (Sync/Async)

Most day‑to‑day endpoints are under `client.<module>` (not `client.admin`). Available client modules:

### User Modules
- `client.users` - User management (get me, list users, update profile, change password)
- `client.otp` - One-time password authentication (generate, validate, sign-up, password reset)
- `client.history` - Track changes to items, users, and integrations
- `client.ai_knowledge` - AI knowledge management (file storage, vector DB)
- `client.queries` - Vector search and similarity queries
- `client.workflows` - Multi-step workflow execution
- `client.logs` - Application logs
- `client.api_keys` - API key management
- `client.usage` - Usage statistics and metrics

### Admin Modules
- `client.admin.organization` - Organization management
- `client.admin.security_groups` - Security group management
- `client.admin.integrations` - Integration configuration
- `client.admin.database` - VectorDB schema management
- `client.admin.settings` - System settings and DB connection checks

Example (sync):
```python
me = client.users.get_me()
logs = client.logs.list_logs(integration_name=client.integration_name, limit=25)
history = client.history.get_my_activity(limit=10)
users = client.users.get_users_in_my_organization(limit=50)
```

Example (async):
```python
# me = await client.users.get_me()
# logs = await client.logs.list_logs(integration_name=client.integration_name, limit=25)
# history = await client.history.get_my_activity(limit=10)
# users = await client.users.get_users_in_my_organization(limit=50)
```

## AI Knowledge: File Storage (Sync and Async)

The AI Knowledge file storage API has been updated to align with the latest VectorBridge API (v2.2.1). All endpoints now use RESTful resource paths.

### Sync file workflow
```python
from vector_bridge import VectorBridgeClient
from vector_bridge.schema.ai_knowledge.filesystem import AIKnowledgeFileSystemFilters, AIKnowledgeFileSystemItemUpdate
from vector_bridge.schema.helpers.enums import FileAccessType

client = VectorBridgeClient(integration_name="default", api_key="your_api_key")

# Create folder
folder = client.ai_knowledge.file_storage.create_folder(
    folder_name="Project Documents",
    folder_description="Docs for Q4",
    private=True,
)

# Upload a file with vectorization and progress
upload = client.ai_knowledge.file_storage.upload_file(
    file_path="./docs/spec.pdf",
    parent_id=folder.uuid,
    vectorized=True,
    tags=["spec", "q4"],
)

for p in upload.progress_updates:
    print("progress:", p)
item = upload.item

# Update metadata
client.ai_knowledge.file_storage.update_file_or_folder(
    item_id=item.uuid,
    updated_properties=AIKnowledgeFileSystemItemUpdate(starred=True, tags=["spec", "approved"]) 
)

# Share read-only with a user
client.ai_knowledge.file_storage.grant_or_revoke_user_access(
    item_id=item.uuid, user_id="user-123", has_access=True, access_type=FileAccessType.READ
)

# Share with a security group
client.ai_knowledge.file_storage.grant_or_revoke_security_group_access(
    item_id=item.uuid, group_id="group-456", has_access=True, access_type=FileAccessType.WRITE
)

# List items under folder
items = client.ai_knowledge.file_storage.list_files_and_folders(
    filters=AIKnowledgeFileSystemFilters(parent_id=folder.uuid)
)

# Create file reference (link between files)
client.ai_knowledge.file_storage.create_files_reference(
    from_uuid=item.uuid,
    to_uuid="other-file-uuid",
    metadata={"relation": "attachment"}
)

# Delete file reference
client.ai_knowledge.file_storage.delete_files_reference(
    from_uuid=item.uuid,
    reference_id="reference-id-123"
)

# Download link
link = client.ai_knowledge.file_storage.get_download_link_for_document(item_id=item.uuid)

# Get item path
path = client.ai_knowledge.file_storage.get_file_or_folder_path(item_id=item.uuid)

# Delete item
client.ai_knowledge.file_storage.delete_folder_or_file(item_id=item.uuid)
```

### Async file workflow
```python
import asyncio
from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.ai_knowledge.filesystem import AIKnowledgeFileSystemFilters, AIKnowledgeFileSystemItemUpdate
from vector_bridge.schema.helpers.enums import FileAccessType

async def main():
    async with AsyncVectorBridgeClient(integration_name="default", api_key="your_api_key") as client:
        folder = await client.ai_knowledge.file_storage.create_folder(
            folder_name="Research",
            folder_description="ML papers",
            private=False,
        )

        upload = await client.ai_knowledge.file_storage.upload_file(
            file_path="./papers/attention.pdf",
            parent_id=folder.uuid,
            vectorized=True,
            tags=["nlp", "transformers"],
        )

        async for p in upload.progress_updates:
            print("progress:", p)
        item = await upload.item

        await client.ai_knowledge.file_storage.update_file_or_folder(
            item_id=item.uuid,
            updated_properties=AIKnowledgeFileSystemItemUpdate(starred=True)
        )

        await client.ai_knowledge.file_storage.grant_or_revoke_user_access(
            item_id=item.uuid, user_id="user-123", has_access=True, access_type=FileAccessType.READ
        )

        await client.ai_knowledge.file_storage.grant_or_revoke_security_group_access(
            item_id=item.uuid, group_id="group-456", has_access=True, access_type=FileAccessType.WRITE
        )

        items = await client.ai_knowledge.file_storage.list_files_and_folders(
            filters=AIKnowledgeFileSystemFilters(parent_id=folder.uuid)
        )

        await client.ai_knowledge.file_storage.create_files_reference(
            from_uuid=item.uuid,
            to_uuid="other-file-uuid",
            metadata={"relation": "citation"}
        )

        link = await client.ai_knowledge.file_storage.get_download_link_for_document(item_id=item.uuid)

        path = await client.ai_knowledge.file_storage.get_file_or_folder_path(item_id=item.uuid)

asyncio.run(main())
```

## System Settings (Admin)

The admin settings module provides system configuration and database connection testing:

```python
# Get system settings
settings = client.admin.settings.get_settings()
print(settings.distribution_type)  # DistributionType.SELF_HOSTED
print(settings.files.max_size_bytes)  # File upload limits
print(settings.files.types)  # Supported file types

# Check VectorDB connection
client.admin.settings.check_db_connection(
    url="https://your-weaviate-instance.com",
    api_key="your-weaviate-api-key"
)

# Async
# settings = await client.admin.settings.get_settings()
# await client.admin.settings.check_db_connection(url="...", api_key="...")
```

## Error Handling

Errors are raised as domain‑specific exceptions. For generic HTTP errors you may see `HTTPException` with `status_code` and `detail`.

```python
from vector_bridge import VectorBridgeClient
from vector_bridge.schema.error import HTTPException

client = VectorBridgeClient(integration_name="default")
try:
    client.login(username="user@example.com", password="wrong_password")
except HTTPException as e:
    print(f"HTTP {e.status_code}: {e.detail}")
```

## License

MIT License. See `LICENSE` for details.