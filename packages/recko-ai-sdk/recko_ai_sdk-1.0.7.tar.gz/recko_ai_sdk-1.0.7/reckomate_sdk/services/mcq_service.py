# reckomate_sdk/services/mcq_service.py

from typing import Dict, Any


class MCQService:
    """
    SDK proxy for Admin MCQ APIs.
    Backend file: app/services/mcq_service.py
    """

    def __init__(self, client):
        self.client = client

    # --------------------------------------------------
    # Generate MCQs from content + store
    # --------------------------------------------------
    def generate_mcq(
        self,
        *,
        file_id: str,
        difficulty: str,
        time_limit: int,
        number_of_questions: int,
        choices: int
    ) -> Dict[str, Any]:
        """
        Generate and store MCQs.

        Backend:
        POST /admin/generate-mcq

        Requires:
        - Admin access token
        """

        payload = {
            "file_id": file_id,
            "difficulty": difficulty,
            "time_limit": time_limit,
            "number_of_questions": number_of_questions,
            "choices": choices
        }

        return self.client.post(
            "/admin/generate-mcq",
            json=payload
        )
