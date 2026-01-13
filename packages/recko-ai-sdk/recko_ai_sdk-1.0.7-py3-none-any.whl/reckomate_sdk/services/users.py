from typing import Dict, Optional
from pathlib import Path

from ..client import ReckomateClient
from ..exceptions import ReckomateAPIError


class UserService:
    """
    SDK wrapper for all /user APIs
    """

    def __init__(self, client: ReckomateClient):
        self.client = client

    # ======================================================
    # 🔐 AUTH
    # ======================================================

    def login(self, *, email: str | None = None, phone: str | None = None) -> Dict:
        res = self.client.post(
            "/user/login",
            json={"email": email, "phone": phone}
        )
        return self._handle(res)

    def register(self, *, email: str | None = None, phone: str | None = None) -> Dict:
        res = self.client.post(
            "/user/register",
            json={"email": email, "phone": phone}
        )
        return self._handle(res)

    def resend_otp(self, *, email: str | None = None, phone: str | None = None) -> Dict:
        res = self.client.post(
            "/user/resend-otp",
            json={"email": email, "phone": phone}
        )
        return self._handle(res)

    def verify_otp(
        self,
        *,
        otp: str,
        email: str | None = None,
        phone: str | None = None,
        fcm_token: str | None = None,
    ) -> Dict:
        res = self.client.post(
            "/user/verify-otp",
            json={
                "otp": otp,
                "email": email,
                "phone": phone,
                "fcm_token": fcm_token,
            }
        )
        return self._handle(res)

    # ======================================================
    # 👤 PROFILE
    # ======================================================

    def get_profile(self, user_id: str) -> Dict:
        res = self.client.get(f"/user/profile/{user_id}")
        return self._handle(res)

    def update_own_profile(
        self,
        *,
        name: str,
        email: str,
        phone: str,
        profile_image_path: Optional[str] = None,
    ) -> Dict:
        """
        POST / PUT /user/profile
        (JWT required)
        """
        data = {
            "name": name,
            "email": email,
            "phone": phone,
        }

        files = None
        if profile_image_path:
            p = Path(profile_image_path)
            files = {
                "profile_image": (p.name, open(p, "rb"), "application/octet-stream")
            }

        res = self.client.post(
            "/user/profile",
            data=data,
            files=files
        )
        return self._handle(res)

    def update_profile_by_user_id(
        self,
        *,
        user_id: str,
        name: str,
        email: str,
        phone: str,
        profile_image_path: Optional[str] = None,
    ) -> Dict:
        """
        PUT /user/profile/edit/{user_id}
        (Admin / internal)
        """
        data = {
            "name": name,
            "email": email,
            "phone": phone,
        }

        files = None
        if profile_image_path:
            p = Path(profile_image_path)
            files = {
                "profile_image": (p.name, open(p, "rb"), "application/octet-stream")
            }

        res = self.client.put(
            f"/user/profile/edit/{user_id}",
            data=data,
            files=files
        )
        return self._handle(res)

    # ======================================================
    # 📄 FILE UPLOAD (QDRANT INGEST)
    # ======================================================

    def upload_document(self, file_path: str) -> Dict:
        p = Path(file_path)
        if not p.exists():
            raise ValueError("File does not exist")

        files = {
            "file": (p.name, open(p, "rb"), "application/octet-stream")
        }

        res = self.client.post(
            "/user/uploadDocument",
            files=files
        )
        return self._handle(res)

    # ======================================================
    # 🔧 INTERNAL RESPONSE HANDLER
    # ======================================================

    def _handle(self, response):
        try:
            data = response.json()
        except Exception:
            raise ReckomateAPIError(
                response.status_code,
                "Invalid JSON response from server"
            )

        if response.status_code >= 400:
            raise ReckomateAPIError(
                response.status_code,
                data.get("message")
                or data.get("detail")
                or "User API error",
                data,
            )

        return data
