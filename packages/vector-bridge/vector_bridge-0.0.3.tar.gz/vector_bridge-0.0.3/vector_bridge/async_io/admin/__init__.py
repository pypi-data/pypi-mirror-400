from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.async_io.admin.integrations import AsyncIntegrationsAdmin
from vector_bridge.async_io.admin.organization import AsyncOrganizationAdmin
from vector_bridge.async_io.admin.security_groups import AsyncSecurityGroupsAdmin
from vector_bridge.async_io.admin.settings import AsyncSettingsAdmin
from vector_bridge.async_io.admin.vector_db import AsyncVectorDBAdmin


class AsyncAdminClient:
    """Async admin client providing access to all admin endpoints that require authentication."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

        # Initialize async admin subclients
        self.settings = AsyncSettingsAdmin(client)
        self.organization = AsyncOrganizationAdmin(client)
        self.security_groups = AsyncSecurityGroupsAdmin(client)
        self.integrations = AsyncIntegrationsAdmin(client)
        self.vector_db = AsyncVectorDBAdmin(client)
