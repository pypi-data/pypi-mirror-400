# reckomate_sdk/services/usertest_service.py

from typing import Dict, Any


class UserTestService:
    """
    SDK proxy for User Test APIs.

    Backend:
    app/services/usertest_service.py
    app/routes/usertest_routes.py
    """

    def __init__(self, client):
        self.client = client

    # --------------------------------------------------
    # USER → Start Test
    # POST /user-test/start
    # --------------------------------------------------
    def start_test(self, *, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start a user test.

        body example:
        {
            "user_id": "64fdc9...",
            "test_id": "665fa0...",
            "timer": 30
        }
        """
        return self.client.post(
            "/user-test/start",
            json=body
        )

    # --------------------------------------------------
    # USER → Submit Test
    # POST /user-test/submit
    # --------------------------------------------------
    def submit_test(self, *, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit test answers.

        body example:
        {
            "test_id": "665fa0...",
            "arrayofMcq": [
                {
                    "question": "What is Python?",
                    "selected_answer": "A"
                }
            ]
        }
        """
        return self.client.post(
            "/user-test/submit",
            json=body
        )

    # --------------------------------------------------
    # USER → Check Test Status
    # GET /user-test/status/{user_id}/{test_id}
    # --------------------------------------------------
    def check_test_status(
        self,
        *,
        user_id: str,
        test_id: str
    ) -> Dict[str, Any]:
        """
        Check test status or auto-submit when time is up.
        """
        return self.client.get(
            f"/user-test/status/{user_id}/{test_id}"
        )
