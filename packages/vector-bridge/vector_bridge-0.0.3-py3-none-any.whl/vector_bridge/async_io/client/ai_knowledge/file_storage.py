from typing import Any

import aiofiles
import aiohttp
from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.ai_knowledge.filesystem import (
    AIKnowledgeFileSystemFilters,
    AIKnowledgeFileSystemItem,
    AIKnowledgeFileSystemItemsList,
    AIKnowledgeFileSystemItemUpdate,
    FileSystemItemAggregatedCount,
)
from vector_bridge.schema.ai_knowledge.filesystem import (
    AsyncStreamingResponse as FilesystemAsyncStreamingResponse,
)
from vector_bridge.schema.errors.ai_knowledge import raise_for_ai_knowledge_detail
from vector_bridge.schema.helpers.enums import FileAccessType
from vector_bridge.schema.queries import Query
from weaviate.collections.classes.filters import _Filters
from weaviate.collections.classes.grpc import _Sorting


class AsyncFileStorageAIKnowledge:
    """Async client for AI Knowledge file storage management."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def create_folder(
        self,
        folder_name: str,
        folder_description: str,
        integration_name: str | None = None,
        parent_id: str | None = None,
        tags: list[str] | None = None,
        private: bool = False,
        **other,
    ) -> AIKnowledgeFileSystemItem:
        """
        Create a new folder.

        Args:
            folder_name: The name for the new folder
            folder_description: Description of the folder
            integration_name: The name of the Integration
            parent_id: Parent folder ID (None for root level)
            tags: List of tags for the folder
            private: Whether the folder is private

        Returns:
            Created folder object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/folders"
        params = {
            "folder_name": folder_name,
            "folder_description": folder_description,
            "integration_name": integration_name,
            "private": str(private).lower(),
        }

        if parent_id:
            params["parent_id"] = parent_id

        if tags:
            params["tags"] = tags

        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, params=params, json=other) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
            return AIKnowledgeFileSystemItem.model_validate(result)

    async def __get_upload_link_for_document(self, integration_name: str | None = None) -> dict[str, Any]:
        """
        Get a presigned URL for uploading a document.

        Args:
            integration_name: The name of the Integration

        Returns:
            Dict with upload URL and parameters
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/files/upload-link"
        params = {"integration_name": integration_name}

        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            return await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)

    async def __process_uploaded_file(
        self,
        object_name: str,
        file_name: str,
        parent_id: str | None = None,
        integration_name: str | None = None,
        cloud_stored: bool = True,
        vectorized: bool = True,
        content_uniqueness_check: bool = True,
        tags: list[str] | None = None,
        source_documents_ids: list[str] | None = None,
        private: bool = False,
        **other,
    ) -> FilesystemAsyncStreamingResponse:
        """
        Process an uploaded file.

        Args:
            object_name: The key from the get_upload_link_for_document response
            file_name: The name of the file with extension
            parent_id: Parent folder ID
            integration_name: The name of the Integration
            cloud_stored: Store in VectorBridge storage
            vectorized: Vectorize the file
            content_uniqueness_check: Check for content uniqueness
            tags: List of tags for the file
            source_documents_ids: List of source document IDs
            private: Whether the file is private

        Returns:
            Processed file object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/stream/ai-knowledge/files/process-uploaded"
        params = {
            "object_name": object_name,
            "file_name": file_name,
            "integration_name": integration_name,
            "cloud_stored": str(cloud_stored).lower(),
            "vectorized": str(vectorized).lower(),
            "content_uniqueness_check": str(content_uniqueness_check).lower(),
            "private": str(private).lower(),
        }

        if parent_id:
            params["parent_id"] = parent_id

        if tags:
            params["tags"] = tags

        if source_documents_ids:
            params["source_documents_ids"] = source_documents_ids

        headers = self.client._get_auth_headers()

        response = await self.client.session.post(url, headers=headers, params=params, json=other)
        if response.status >= 400:
            await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)

        return FilesystemAsyncStreamingResponse(response)

    async def upload_file(
        self,
        file_path: str,
        file_name: str | None = None,
        parent_id: str | None = None,
        integration_name: str | None = None,
        cloud_stored: bool = True,
        vectorized: bool = True,
        content_uniqueness_check: bool = True,
        tags: list[str] | None = None,
        source_documents_ids: list[str] | None = None,
        private: bool = False,
        **other,
    ) -> FilesystemAsyncStreamingResponse:
        """
        Upload and process a file in one step.

        Args:
            file_path: Path to the file to upload
            file_name: Name for the file (defaults to basename of file_path)
            parent_id: Parent folder ID
            integration_name: The name of the Integration
            cloud_stored: Store in VectorBridge storage
            vectorized: Vectorize the file
            content_uniqueness_check: Check for content uniqueness
            tags: List of tags for the file
            source_documents_ids: List of source document IDs
            private: Whether the file is private

        Returns:
            Processed file object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        import os

        if file_name is None:
            file_name = os.path.basename(file_path)

        # 1. Get upload link
        upload_link_response = await self.__get_upload_link_for_document(integration_name)
        upload_url = upload_link_response["url"]
        object_name = upload_link_response["body"]["key"]

        # 2. Upload file to the presigned URL using aiohttp
        async with aiofiles.open(file_path, "rb") as file:
            file_data = await file.read()

        # Create multipart form data
        data = aiohttp.FormData()
        for key, value in upload_link_response["body"].items():
            data.add_field(key, value)
        data.add_field("file", file_data, filename=file_name)

        async with aiohttp.ClientSession() as upload_session:
            async with upload_session.post(upload_url, data=data) as upload_response:
                if upload_response.status >= 300:
                    error_text = await upload_response.text()
                    raise Exception(f"Error uploading file: {error_text}")

        # 3. Process the uploaded file
        return await self.__process_uploaded_file(
            object_name=object_name,
            file_name=file_name,
            parent_id=parent_id,
            integration_name=integration_name,
            cloud_stored=cloud_stored,
            vectorized=vectorized,
            content_uniqueness_check=content_uniqueness_check,
            tags=tags,
            source_documents_ids=source_documents_ids,
            private=private,
            **other,
        )

    async def create_files_reference(
        self,
        from_uuid: str,
        to_uuid: str,
        metadata: dict,
        integration_name: str | None = None,
    ) -> None:
        """
        Create a reference between two files.

        Args:
            from_uuid: Source file UUID
            to_uuid: Target file UUID
            metadata: Metadata about the file reference
            integration_name: The name of the Integration

        Returns:
            None
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{from_uuid}/references"
        params = {
            "to_uuid": to_uuid,
        }

        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, params=params, json=metadata) as response:
            await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
        return None

    async def delete_files_reference(
        self,
        from_uuid: str,
        reference_id: str,
        integration_name: str | None = None,
    ) -> None:
        """
        Delete a reference between two files.

        Args:
            from_uuid: Source file UUID
            reference_id: The ID of the reference to delete
            integration_name: The name of the Integration

        Returns:
            None
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{from_uuid}/references/{reference_id}"
        params = {}

        headers = self.client._get_auth_headers()

        async with self.client.session.delete(url, headers=headers, params=params) as response:
            await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
        return None

    async def rename_file_or_folder(
        self, item_id: str, new_name: str, integration_name: str | None = None
    ) -> AIKnowledgeFileSystemItem:
        """
        Rename a file or folder.

        Args:
            item_id: The ID of the file or folder to rename
            new_name: The new name for the file or folder
            integration_name: The name of the Integration

        Returns:
            Updated file or folder object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{item_id}/name"
        params = {
            "new_name": new_name,
            "integration_name": integration_name,
        }

        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
            return AIKnowledgeFileSystemItem.model_validate(result)

    async def update_file_or_folder(
        self,
        item_id: str,
        updated_properties: AIKnowledgeFileSystemItemUpdate,
        integration_name: str | None = None,
    ) -> AIKnowledgeFileSystemItem:
        """
        Update a file or folder.

        Args:
            item_id: The ID of the file or folder to update
            updated_properties: The new properties for the file or folder
            integration_name: The name of the Integration

        Returns:
            Updated file or folder object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{item_id}"
        params = {
            "integration_name": integration_name,
        }

        _json = updated_properties.to_dict()
        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params, json=_json) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
            return AIKnowledgeFileSystemItem.model_validate(result)

    async def delete_file_or_folder(self, item_id: str, integration_name: str | None = None) -> None:
        """
        Delete a file or folder.

        Args:
            item_id: The ID of the file or folder to delete
            integration_name: The name of the Integration
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{item_id}"
        params = {"integration_name": integration_name}

        headers = self.client._get_auth_headers()

        async with self.client.session.delete(url, headers=headers, params=params) as response:
            await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)

    async def get_file_or_folder(self, item_id: str, integration_name: str | None = None) -> AIKnowledgeFileSystemItem:
        """
        Get details of a file or folder.

        Args:
            item_id: The ID of the file or folder
            integration_name: The name of the Integration

        Returns:
            File or folder object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{item_id}"
        params = {"integration_name": integration_name}

        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
            return AIKnowledgeFileSystemItem.model_validate(result)

    async def get_file_or_folder_path(
        self, item_id: str, integration_name: str | None = None
    ) -> list[AIKnowledgeFileSystemItem]:
        """
        Get the path of a file or folder.

        Args:
            item_id: The ID of the file or folder
            integration_name: The name of the Integration

        Returns:
            List of path components as objects
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{item_id}/path"
        params = {"integration_name": integration_name}

        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            results = await self.client._handle_response(
                response=response, error_callable=raise_for_ai_knowledge_detail
            )
            return [AIKnowledgeFileSystemItem.model_validate(result) for result in results]

    async def list_files_and_folders(
        self,
        filters: AIKnowledgeFileSystemFilters | None = None,
        integration_name: str | None = None,
    ) -> AIKnowledgeFileSystemItemsList:
        """
        List files and folders.

        Args:
            filters: Dictionary of filter parameters
            integration_name: The name of the Integration

        Returns:
            Dictionary with items, pagination info, etc.
        """
        if filters is None:
            filters = AIKnowledgeFileSystemFilters()

        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items"
        params = {"integration_name": integration_name}

        headers = self.client._get_auth_headers()

        async with self.client.session.post(
            url,
            headers=headers,
            params=params,
            json=filters.to_serializable_non_empty_dict(),
        ) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
            return AIKnowledgeFileSystemItemsList.model_validate(result)

    async def execute_files_and_folders_list_query(
        self,
        integration_name: str | None = None,
        near_text: str | None = None,
        filters: _Filters | None = None,
        sort: _Sorting | None = None,
        limit: int | None = None,
        offset: int | None = None,
        **kwargs,
    ) -> AIKnowledgeFileSystemItemsList:
        """
        List files and folders.

        Args:
            integration_name: The name of the Integration
            near_text: The query text
            filters: The filters to apply to the query
            sort: The sort to apply to the query
            limit: The maximum number of results to return
            offset: The offset to start with

        Returns:
            Dictionary with items, pagination info, etc.
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        query_payload = Query(
            near_text=near_text,
            filters=filters,
            sort=sort,
            limit=limit,
            offset=offset,
            kwargs=kwargs,
        )

        url = f"{self.client.base_url}/v1/ai-knowledge/items/search"
        params = {"integration_name": integration_name}

        headers = self.client._get_auth_headers()

        async with self.client.session.post(
            url,
            headers=headers,
            params=params,
            json=query_payload.serialize_bytes(),
        ) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
            return AIKnowledgeFileSystemItemsList.model_validate(result)

    async def count_files_and_folders(
        self, parents: list[str], integration_name: str | None = None
    ) -> FileSystemItemAggregatedCount:
        """
        Count files and folders.

        Args:
            parents: List of parent folder IDs
            integration_name: The name of the Integration

        Returns:
            Dictionary with count information
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/statistics"
        params = {"parents": parents, "integration_name": integration_name}

        headers = self.client._get_auth_headers()

        async with self.client.session.put(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
            return FileSystemItemAggregatedCount.model_validate(result)

    async def get_download_link_for_document(
        self, item_id: str, expiration_seconds: int = 60, integration_name: str | None = None
    ) -> str:
        """
        Get a download link for a file.

        Args:
            item_id: The ID of the file
            expiration_seconds: Time in seconds for the link to remain valid
            integration_name: The name of the Integration

        Returns:
            Download URL as a string
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/files/download-link"
        params = {
            "item_id": item_id,
            "expiration_seconds": expiration_seconds,
            "integration_name": integration_name,
        }

        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            return await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)

    async def grant_or_revoke_user_access(
        self,
        item_id: str,
        user_id: str,
        has_access: bool,
        access_type: FileAccessType = FileAccessType.READ,
        integration_name: str | None = None,
    ) -> None | AIKnowledgeFileSystemItem:
        """
        Grant or revoke user access to a file or folder.

        Args:
            item_id: The ID of the file or folder
            user_id: The ID of the user
            has_access: Whether to grant (True) or revoke (False) access
            access_type: Type of access ("READ" or "WRITE")
            integration_name: The name of the Integration

        Returns:
            Updated file or folder object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{item_id}/permissions/users/{user_id}"
        params = {
            "has_access": str(has_access).lower(),
            "access_type": access_type,
            "integration_name": integration_name,
        }

        headers = self.client._get_auth_headers()

        async with self.client.session.put(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
            return AIKnowledgeFileSystemItem.model_validate(result) if result else None

    async def grant_or_revoke_security_group_access(
        self,
        item_id: str,
        group_id: str,
        has_access: bool,
        access_type: FileAccessType = FileAccessType.READ,
        integration_name: str | None = None,
    ) -> None | AIKnowledgeFileSystemItem:
        """
        Grant or revoke security group access to a file or folder.

        Args:
            item_id: The ID of the file or folder
            group_id: The ID of the security group
            has_access: Whether to grant (True) or revoke (False) access
            access_type: Type of access ("READ" or "WRITE")
            integration_name: The name of the Integration

        Returns:
            Updated file or folder object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{item_id}/permissions/groups/{group_id}"
        params = {
            "has_access": str(has_access).lower(),
            "access_type": access_type,
            "integration_name": integration_name,
        }

        headers = self.client._get_auth_headers()

        async with self.client.session.put(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
            return AIKnowledgeFileSystemItem.model_validate(result) if result else None
