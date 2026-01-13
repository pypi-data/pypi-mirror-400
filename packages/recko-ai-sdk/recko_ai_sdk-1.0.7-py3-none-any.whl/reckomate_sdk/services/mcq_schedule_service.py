# reckomate_sdk/services/mcq_schedule_service.py

from typing import Dict, Any
from datetime import datetime


class MCQScheduleService:
    """
    SDK proxy for MCQ scheduling APIs.
    Backend service: mcq_schedule_service.py
    """

    def __init__(self, client):
        self.client = client

    # --------------------------------------------------
    # Schedule MCQ for Excel upload
    # --------------------------------------------------
    def schedule_mcq(
        self,
        *,
        mcq_id: str,
        excel_upload_id: str,
        scheduled_start_time: datetime
    ) -> Dict[str, Any]:
        """
        Schedule an MCQ test for users from an Excel upload.

        Backend:
        POST /admin/mcq/schedule

        Parameters:
        - mcq_id: MCQ ObjectId (string)
        - excel_upload_id: Excel upload ObjectId (string)
        - scheduled_start_time: datetime (IST or UTC as backend expects)
        """

        payload = {
            "mcq_id": mcq_id,
            "excel_upload_id": excel_upload_id,
            "scheduled_start_time": scheduled_start_time.isoformat()
        }

        return self.client.post(
            "/admin/mcq/schedule",
            json=payload
        )
