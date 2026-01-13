from typing import TYPE_CHECKING

from vector_bridge.schema.errors.history import raise_for_history_error_detail
from vector_bridge.schema.history import HistoryChangeType, ItemType, PaginatedHistory

if TYPE_CHECKING:
    from vector_bridge import VectorBridgeClient


class HistoryClient:
    """Client for history operations."""

    def __init__(self, client: "VectorBridgeClient"):
        self.client = client

    def get_item_history(
        self,
        item_id: str,
        item_type: ItemType | str,
        integration_name: str = "default",
        limit: int = 50,
        last_evaluated_key: str | None = None,
    ) -> PaginatedHistory:
        """
        Get history for a specific item.

        Args:
            item_id: The ID of the item
            item_type: The type of the item
            integration_name: The name of the Integration
            limit: The number of history entries to retrieve
            last_evaluated_key: Pagination key for the next set of results

        Returns:
            PaginatedHistory: Paginated history entries
        """
        url = f"{self.client.base_url}/v1/history/item/{item_id}"
        headers = self.client._get_auth_headers()

        params = {
            "integration_name": integration_name,
            "item_type": item_type,
            "limit": limit,
        }
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_history_error_detail)
        return PaginatedHistory(**result)

    def get_integration_history(
        self,
        integration_name: str = "default",
        limit: int = 50,
        last_evaluated_key: str | None = None,
        item_type: ItemType | str | None = None,
        change_type: HistoryChangeType | str | None = None,
    ) -> PaginatedHistory:
        """
        Get all history entries for an integration.

        Args:
            integration_name: The name of the Integration
            limit: The number of history entries to retrieve
            last_evaluated_key: Pagination key for the next set of results
            item_type: Filter by item type
            change_type: Filter by change type

        Returns:
            PaginatedHistory: Paginated history entries
        """
        url = f"{self.client.base_url}/v1/history/integration"
        headers = self.client._get_auth_headers()

        params = {
            "integration_name": integration_name,
            "limit": limit,
        }
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key
        if item_type:
            params["item_type"] = item_type
        if change_type:
            params["change_type"] = change_type

        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_history_error_detail)
        return PaginatedHistory(**result)

    def get_user_history(
        self,
        user_id: str,
        integration_name: str = "default",
        limit: int = 50,
        last_evaluated_key: str | None = None,
    ) -> PaginatedHistory:
        """
        Get all history entries created by a specific user.

        Args:
            user_id: The ID of the user
            integration_name: The name of the Integration
            limit: The number of history entries to retrieve
            last_evaluated_key: Pagination key for the next set of results

        Returns:
            PaginatedHistory: Paginated history entries
        """
        url = f"{self.client.base_url}/v1/history/user/{user_id}"
        headers = self.client._get_auth_headers()

        params = {
            "integration_name": integration_name,
            "limit": limit,
        }
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_history_error_detail)
        return PaginatedHistory(**result)

    def get_my_activity(
        self,
        integration_name: str = "default",
        limit: int = 50,
        last_evaluated_key: str | None = None,
    ) -> PaginatedHistory:
        """
        Get all history entries created by the current user.

        Args:
            integration_name: The name of the Integration
            limit: The number of history entries to retrieve
            last_evaluated_key: Pagination key for the next set of results

        Returns:
            PaginatedHistory: Paginated history entries
        """
        url = f"{self.client.base_url}/v1/history/my-activity"
        headers = self.client._get_auth_headers()

        params = {
            "integration_name": integration_name,
            "limit": limit,
        }
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_history_error_detail)
        return PaginatedHistory(**result)

    def delete_history_entry(
        self,
        history_id: str,
        item_id: str,
        item_type: ItemType | str,
        integration_name: str = "default",
    ) -> None:
        """
        Delete a specific history entry.

        Args:
            history_id: The ID of the history entry
            item_id: The ID of the item
            item_type: The type of the item
            integration_name: The name of the Integration
        """
        url = f"{self.client.base_url}/v1/history/entry/{history_id}/delete"
        headers = self.client._get_auth_headers()

        params = {
            "integration_name": integration_name,
            "item_id": item_id,
            "item_type": item_type,
        }

        response = self.client.session.delete(url, headers=headers, params=params)
        self.client._handle_response(response=response, error_callable=raise_for_history_error_detail)

    def delete_item_history(
        self,
        item_id: str,
        item_type: ItemType | str,
        integration_name: str = "default",
    ) -> None:
        """
        Delete all history entries for a specific item.

        Args:
            item_id: The ID of the item
            item_type: The type of the item
            integration_name: The name of the Integration
        """
        url = f"{self.client.base_url}/v1/history/item/{item_id}/delete"
        headers = self.client._get_auth_headers()

        params = {
            "integration_name": integration_name,
            "item_type": item_type,
        }

        response = self.client.session.delete(url, headers=headers, params=params)
        self.client._handle_response(response=response, error_callable=raise_for_history_error_detail)

    def delete_integration_history(
        self,
        integration_name: str = "default",
    ) -> None:
        """
        Delete all history entries for an integration.

        Args:
            integration_name: The name of the Integration
        """
        url = f"{self.client.base_url}/v1/history/integration/delete"
        headers = self.client._get_auth_headers()

        params = {"integration_name": integration_name}

        response = self.client.session.delete(url, headers=headers, params=params)
        self.client._handle_response(response=response, error_callable=raise_for_history_error_detail)
