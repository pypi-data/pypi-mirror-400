# reckomate_sdk/services/linktestwithphone_service.py

from typing import Dict, Any


class LinkTestWithPhoneService:
    """
    SDK proxy for MCQ assignment & leaderboard APIs.
    Backend service: linkTestWithPhone_service.py
    """

    def __init__(self, client):
        self.client = client

    # --------------------------------------------------
    # Assign MCQ to phones using Excel upload
    # --------------------------------------------------
    def assign_mcq(
        self,
        mcq_id: str,
        excel_upload_id: str
    ) -> Dict[str, Any]:
        """
        Assign MCQ to phone numbers from Excel upload.

        Backend:
        POST /admin/mcq/assign
        """

        payload = {
            "mcq_id": mcq_id,
            "excel_upload_id": excel_upload_id
        }

        return self.client.post(
            "/admin/mcq/assign",
            json=payload
        )

    # --------------------------------------------------
    # Get MCQ leaderboard
    # --------------------------------------------------
    def get_leaderboard(self, mcq_id: str) -> Dict[str, Any]:
        """
        Get leaderboard for a MCQ.

        Backend:
        GET /admin/mcq/leaderboard/{mcq_id}
        """

        return self.client.get(
            f"/admin/mcq/leaderboard/{mcq_id}"
        )
