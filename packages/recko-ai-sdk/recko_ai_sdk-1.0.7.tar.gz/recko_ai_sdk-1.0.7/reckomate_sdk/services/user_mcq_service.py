# reckomate_sdk/services/user_mcq_service.py

from typing import Dict, Any, List


class UserMCQService:
    """
    SDK proxy for User MCQ operations.

    Backend file:
    app/services/user_mcq_service.py
    """

    def __init__(self, client):
        self.client = client

    # --------------------------------------------------
    # USER → Get assigned MCQs
    # GET /user/mcqs
    # --------------------------------------------------
    def get_visible_mcqs(self) -> List[Dict[str, Any]]:
        """
        Get list of MCQs assigned to the logged-in user.
        Access token must be USER token.
        """
        return self.client.get("/user/mcqs")

    # --------------------------------------------------
    # USER → Start MCQ Test
    # POST /user/startMcqTest
    # --------------------------------------------------
    def start_mcq(self, *, mcq_id: str) -> Dict[str, Any]:
        """
        Start or resume an MCQ test.
        """
        payload = {
            "mcq_id": mcq_id
        }
        return self.client.post("/user/startMcqTest", json=payload)

    # --------------------------------------------------
    # USER → Submit MCQ Test
    # POST /user/submitMcqTest
    # --------------------------------------------------
    def submit_mcq(
        self,
        *,
        mcq_id: str,
        answers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Submit MCQ answers.

        answers format:
        {
            "0": "A",
            "1": "C",
            "2": "B"
        }
        """
        payload = {
            "mcq_id": mcq_id,
            "answers": answers
        }
        return self.client.post("/user/submitMcqTest", json=payload)

    # --------------------------------------------------
    # ADMIN → Get all MCQ results
    # GET /user/admin/results
    # --------------------------------------------------
    def get_all_results(self) -> List[Dict[str, Any]]:
        """
        Get all MCQ submissions (Admin only).
        Requires ADMIN access token.
        """
        return self.client.get("/user/admin/results")
