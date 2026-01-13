from typing import Any

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.ai_knowledge.filesystem import (
    AIKnowledgeFileSystemFilters,
    AIKnowledgeFileSystemItem,
    AIKnowledgeFileSystemItemsList,
    AIKnowledgeFileSystemItemUpdate,
    FileSystemItemAggregatedCount,
)
from vector_bridge.schema.ai_knowledge.filesystem import (
    StreamingResponse as FilesystemStreamingResponse,
)
from vector_bridge.schema.errors.ai_knowledge import raise_for_ai_knowledge_detail
from vector_bridge.schema.helpers.enums import FileAccessType
from vector_bridge.schema.queries import Query
from weaviate.collections.classes.filters import _Filters
from weaviate.collections.classes.grpc import _Sorting


class FileStorageAIKnowledge:
    """Client for AI Knowledge file storage management."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def create_folder(
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
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/folders"
        params = {
            "folder_name": folder_name,
            "folder_description": folder_description,
            "integration_name": integration_name,
            "private": private,
        }

        if parent_id:
            params["parent_id"] = parent_id

        if tags:
            params["tags"] = tags

        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params, json=other)
        result = self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
        return AIKnowledgeFileSystemItem.model_validate(result)

    def __get_upload_link_for_document(self, integration_name: str | None = None) -> dict[str, Any]:
        """
        Get a presigned URL for uploading a document.

        Args:
            integration_name: The name of the Integration

        Returns:
            Dict with upload URL and parameters
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/files/upload-link"
        params = {"integration_name": integration_name}

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        return self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)

    def __process_uploaded_file(
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
    ) -> FilesystemStreamingResponse:
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
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/stream/ai-knowledge/file/process-uploaded"
        params = {
            "object_name": object_name,
            "file_name": file_name,
            "integration_name": integration_name,
            "cloud_stored": cloud_stored,
            "vectorized": vectorized,
            "content_uniqueness_check": content_uniqueness_check,
            "private": private,
        }

        if parent_id:
            params["parent_id"] = parent_id

        if tags:
            params["tags"] = tags

        if source_documents_ids:
            params["source_documents_ids"] = source_documents_ids

        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params, json=other, stream=True)
        if response.status_code >= 400:
            self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)

        return FilesystemStreamingResponse(response)

    def upload_file(
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
    ) -> FilesystemStreamingResponse:
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

        import requests

        if file_name is None:
            file_name = os.path.basename(file_path)

        # 1. Get upload link
        upload_link_response = self.__get_upload_link_for_document(integration_name)
        upload_url = upload_link_response["url"]
        object_name = upload_link_response["body"]["key"]

        # 2. Upload file to the presigned URL
        with open(file_path, "rb") as file:
            files = {"file": (file_name, file)}
            upload_response = requests.post(upload_url, data=upload_link_response["body"], files=files)

            if upload_response.status_code >= 300:
                raise Exception(f"Error uploading file: {upload_response.text}")

        # 3. Process the uploaded file
        return self.__process_uploaded_file(
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

    def create_files_reference(
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
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{from_uuid}/references"
        params = {
            "to_uuid": to_uuid,
        }

        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params, json=metadata)
        self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
        return None

    def delete_files_reference(
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
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{from_uuid}/references/{reference_id}"
        params = {}

        headers = self.client._get_auth_headers()
        response = self.client.session.delete(url, headers=headers, params=params)
        self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
        return None

    def rename_file_or_folder(
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
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{item_id}/name"
        params = {
            "new_name": new_name,
            "integration_name": integration_name,
        }

        headers = self.client._get_auth_headers()
        response = self.client.session.patch(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
        return AIKnowledgeFileSystemItem.model_validate(result)

    def update_file_or_folder(
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
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{item_id}"
        params = {
            "integration_name": integration_name,
        }

        _json = updated_properties.to_dict()
        headers = self.client._get_auth_headers()
        response = self.client.session.patch(url, headers=headers, params=params, json=_json)
        result = self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
        return AIKnowledgeFileSystemItem.model_validate(result)

    def delete_file_or_folder(self, item_id: str, integration_name: str | None = None) -> None:
        """
        Delete a file or folder.

        Args:
            item_id: The ID of the file or folder to delete
            integration_name: The name of the Integration
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{item_id}"
        params = {"integration_name": integration_name}

        headers = self.client._get_auth_headers()
        response = self.client.session.delete(url, headers=headers, params=params)
        self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)

    def get_file_or_folder(self, item_id: str, integration_name: str | None = None) -> AIKnowledgeFileSystemItem:
        """
        Get details of a file or folder.

        Args:
            item_id: The ID of the file or folder
            integration_name: The name of the Integration

        Returns:
            File or folder object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{item_id}"
        params = {"integration_name": integration_name}

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
        return AIKnowledgeFileSystemItem.model_validate(result)

    def get_file_or_folder_path(
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
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{item_id}/path"
        params = {"integration_name": integration_name}

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        results = self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
        return [AIKnowledgeFileSystemItem.model_validate(result) for result in results]

    def list_files_and_folders(
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

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items"
        params = {"integration_name": integration_name}

        headers = self.client._get_auth_headers()
        response = self.client.session.post(
            url,
            headers=headers,
            params=params,
            json=filters.to_serializable_non_empty_dict(),
        )
        result = self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
        return AIKnowledgeFileSystemItemsList.model_validate(result)

    def execute_files_and_folders_list_query(
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
        response = self.client.session.post(
            url,
            headers=headers,
            params=params,
            json=query_payload.serialize_bytes(),
        )
        result = self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
        return AIKnowledgeFileSystemItemsList.model_validate(result)

    def count_files_and_folders(
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
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/statistics"
        params = {"parents": parents, "integration_name": integration_name}

        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
        return FileSystemItemAggregatedCount.model_validate(result)

    def get_download_link_for_document(
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
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/files/download-link"
        params = {
            "item_id": item_id,
            "expiration_seconds": expiration_seconds,
            "integration_name": integration_name,
        }

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        return self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)

    def grant_or_revoke_user_access(
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
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{item_id}/permissions/users/{user_id}"
        params = {
            "has_access": has_access,
            "access_type": access_type,
            "integration_name": integration_name,
        }

        headers = self.client._get_auth_headers()
        response = self.client.session.put(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
        return AIKnowledgeFileSystemItem.model_validate(result) if result else None

    def grant_or_revoke_security_group_access(
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
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai-knowledge/items/{item_id}/permissions/groups/{group_id}"
        params = {
            "has_access": has_access,
            "access_type": access_type,
            "integration_name": integration_name,
        }

        headers = self.client._get_auth_headers()
        response = self.client.session.put(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
        return AIKnowledgeFileSystemItem.model_validate(result) if result else None
