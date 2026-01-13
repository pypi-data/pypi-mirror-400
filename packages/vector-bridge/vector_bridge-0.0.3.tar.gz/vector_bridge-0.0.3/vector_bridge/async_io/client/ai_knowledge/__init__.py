from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.async_io.client.ai_knowledge.file_storage import (
    AsyncFileStorageAIKnowledge,
)


class AsyncAIKnowledge:
    """Async admin client for AI Knowledge management endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client
        self.file_storage = AsyncFileStorageAIKnowledge(client)
