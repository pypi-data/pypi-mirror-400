from vector_bridge import VectorBridgeClient
from vector_bridge.sync_io.admin.integrations import IntegrationsAdmin
from vector_bridge.sync_io.admin.organization import OrganizationAdmin
from vector_bridge.sync_io.admin.security_groups import SecurityGroupsAdmin
from vector_bridge.sync_io.admin.settings import SettingsAdmin
from vector_bridge.sync_io.admin.vector_db import VectorDBAdmin


class AdminClient:
    """Admin client providing access to all admin endpoints that require authentication."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

        # Initialize admin subclients
        self.settings = SettingsAdmin(client)
        self.organization = OrganizationAdmin(client)
        self.security_groups = SecurityGroupsAdmin(client)
        self.integrations = IntegrationsAdmin(client)
        self.vector_db = VectorDBAdmin(client)
