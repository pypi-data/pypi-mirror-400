# reckomate_sdk/services/qdrant_service.py

from typing import Dict, Any


class QdrantService:
    """
    SDK proxy for Qdrant-related backend APIs.

    Backend file:
    app/services/qdrant_service.py

    SDK does NOT talk to Qdrant directly.
    """

    def __init__(self, client):
        self.client = client

    # --------------------------------------------------
    # Get content by file_id
    # --------------------------------------------------
    def get_content_by_file_id(
        self,
        *,
        file_id: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Retrieve stored text content for a file.

        Backend:
        GET /admin/qdrant/content/{file_id}?limit=20

        Requires:
        - Admin access token
        """

        return self.client.get(
            f"/admin/qdrant/content/{file_id}",
            params={"limit": limit}
        )
