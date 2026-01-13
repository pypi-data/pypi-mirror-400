from vector_bridge import VectorBridgeClient
from vector_bridge.sync_io.client.ai_knowledge.file_storage import FileStorageAIKnowledge


class AIKnowledge:
    """Admin client for AI Knowledge management endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client
        self.file_storage = FileStorageAIKnowledge(client)
