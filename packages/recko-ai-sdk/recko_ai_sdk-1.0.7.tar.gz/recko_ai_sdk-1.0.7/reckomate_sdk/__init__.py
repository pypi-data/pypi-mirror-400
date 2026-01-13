"""
Reckomate SDK
~~~~~~~~~~~~~

Python SDK for interacting with Reckomate backend services.
"""

from .client import ReckomateClient

# Core services
from .services.admin import AdminService
from .services.users import UserService
from .services.users_ingest import UsersIngestService
from .services.question import QuestionService

# Excel & MCQ services
from .services.excel_service import ExcelService
from .services.linktestwithphone_service import LinkTestWithPhoneService
from .services.mcq_schedule_service import MCQScheduleService
from .services.mcq_service import MCQService
from .services.qdrant_service import QdrantService

# User MCQ & User Test services
from .services.user_mcq_service import UserMCQService
from .services.usertest_service import UserTestService


class ReckomateSDK:
    """
    Main SDK entry point.

    This class aggregates all backend services
    and exposes them via a single SDK object.
    """

    def __init__(self, base_url: str, token: str | None = None):
        self._client = ReckomateClient(
            base_url=base_url,
            token=token
        )

        # ==================================================
        # Service bindings
        # ==================================================

        # Admin & user management
        self.admin = AdminService(self._client)
        self.users = UserService(self._client)
        self.users_ingest = UsersIngestService(self._client)

        # Content & question generation
        self.questions = QuestionService(self._client)
        self.qdrant = QdrantService(self._client)

        # Excel & MCQ workflows
        self.excel = ExcelService(self._client)
        self.mcq = MCQService(self._client)
        self.mcq_schedule = MCQScheduleService(self._client)
        self.link_test = LinkTestWithPhoneService(self._client)

        # User-facing MCQ & tests
        self.user_mcq = UserMCQService(self._client)
        self.user_test = UserTestService(self._client)

    # ==================================================
    # Token management
    # ==================================================
    def set_token(self, token: str):
        """
        Update auth token dynamically (after login).
        """
        self._client.set_token(token)


__all__ = [
    "ReckomateSDK",
    "ReckomateClient",

    # Services
    "AdminService",
    "UserService",
    "UsersIngestService",
    "QuestionService",
    "QdrantService",
    "ExcelService",
    "LinkTestWithPhoneService",
    "MCQService",
    "MCQScheduleService",
    "UserMCQService",
    "UserTestService",
]
