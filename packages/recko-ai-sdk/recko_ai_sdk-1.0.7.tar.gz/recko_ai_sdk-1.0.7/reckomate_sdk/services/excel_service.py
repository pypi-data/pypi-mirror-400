# reckomate_sdk/services/excel_service.py

from typing import Any, Dict
from pathlib import Path


class ExcelService:
    """
    SDK proxy for Admin Excel upload APIs
    """

    def __init__(self, client):
        self.client = client

    def upload_excel(self, file_path: str) -> Dict[str, Any]:
        """
        Upload Excel file to backend for processing

        Args:
            file_path: Path to .xlsx file

        Returns:
            Backend response
        """

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix not in [".xls", ".xlsx"]:
            raise ValueError("Only .xls or .xlsx files are allowed")

        with open(file_path, "rb") as f:
            files = {
                "file": (
                    file_path.name,
                    f,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            }

            return self.client.post(
                "/admin/uploadExcel",
                files=files
            )
