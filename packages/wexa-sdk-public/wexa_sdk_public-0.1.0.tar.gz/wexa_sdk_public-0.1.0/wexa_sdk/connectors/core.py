from __future__ import annotations
from typing import Any, Optional

from ..core.http import HttpClient
from .google_drive import GoogleDrive

class Connectors:
    def __init__(self, http: HttpClient):
        self.http = http
        self.google_drive = GoogleDrive(http)

    # POST /actions/{CATEGORY}/{ACTION}/{connector_id?}
    def action(self, category: str, action: str, connector_id: Optional[str] = None, *, body: Optional[dict] = None, projectID: Optional[str] = None) -> Any:
        path = f"/actions/{category}/{action}/{connector_id}" if connector_id else f"/actions/{category}/{action}"
        params = {"projectID": projectID} if projectID else None
        return self.http.request("POST", path, params=params, json=body)

    # POST /actions/{CATEGORY}/config?projectID=...
    def set_config(self, category: str, project_id: str, body: dict) -> Any:
        return self.http.request("POST", f"/actions/{category}/config", params={"projectID": project_id}, json=body)

    # GET /actions/{CATEGORY}/config/{projectID}
    def get_config(self, category: str, project_id: str) -> Any:
        return self.http.request("GET", f"/actions/{category}/config/{project_id}")
