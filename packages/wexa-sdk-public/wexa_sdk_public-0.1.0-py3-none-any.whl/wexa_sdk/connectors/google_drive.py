from __future__ import annotations
from typing import Any, Dict, Optional

from ..core.http import HttpClient

class GoogleDrive:
    def __init__(self, http: HttpClient):
        self.http = http

    def list_files(self, connector_id: str, *, folder_id: str, page_size: Optional[int] = None, page_token: Optional[str] = None, fetch_all: Optional[bool] = None):
        body: Dict[str, Any] = {"folder_id": folder_id}
        if page_size is not None:
            body["page_size"] = page_size
        if page_token is not None:
            body["page_token"] = page_token
        if fetch_all is not None:
            body["fetch_all"] = fetch_all
        return self.http.request("POST", f"/actions/google_drive/list_files/{connector_id}", json=body)

    def read(self, connector_id: str, *, file_id: str):
        body = {"file_id": file_id}
        return self.http.request("POST", f"/actions/google_drive/read/{connector_id}", json=body)
