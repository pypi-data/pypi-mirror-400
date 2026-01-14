from __future__ import annotations
from typing import Any, Dict, Optional, TypedDict

from .core.http import HttpClient

class Files:
    def __init__(self, http: HttpClient):
        self.http = http

    # POST /files/upload?projectID=...&container_name=...
    # body example: { "filenames": ["file.pdf"], "tags": ["resume"], "source_type": "STORAGE", "org_id": "..." }
    class UploadFilesBody(TypedDict):
        """Body for uploading files."""
        filenames: list[str]
        tags: list[str]
        projectID: str
        source_type: str
        org_id: str

    def upload_request(self, project_id: str, container_name: str, body: UploadFilesBody):
        """
        File Upload.
        POST /files/upload?projectID=...&container_name=...

        Files upload.

        This endpoint uploads a document to the knowledge base with the provided tags. 
        Use this endpoint to upload files to your Wexa.ai environment, enabling your AI 
        coworkers to access and utilize them for various tasks in the knowledge base.

        Args:
            project_id: The unique identifier of the project (required)
            container_name: The name of the container where files will be uploaded (required)
            body: Upload request body containing:
                - filenames: List of file names to upload (required)
                - tags: List of tags associated with the files (required)
                - projectID: The unique identifier of the project (required)
                - source_type: The source type of the files (e.g., "STORAGE") (required)
                - org_id: The unique identifier of the organization (required)

        Returns:
            Upload response containing metadata about the uploaded files to the knowledge base.

        Example:
            >>> upload_body = {
            ...     "filenames": ["file.pdf"],
            ...     "tags": ["resume", "knowledge-base"],
            ...     "projectID": "68c3b3f4f68066a18c3c25e8",
            ...     "source_type": "STORAGE",
            ...     "org_id": "68dbdfb92797c909223ea38f"
            ... }
            >>> result = client.files.upload_request(
            ...     project_id="68c3b3f4f68066a18c3c25e8",
            ...     container_name="68c3b3f4f68066a18c3c25e8",
            ...     body=upload_body
            ... )
        """
        params: Dict[str, Any] = {"projectID": project_id, "container_name": container_name}
        return self.http.request("POST", "/files/upload", params=params, json=body)

    # GET /file/{fileId}/?projectID=...
    def get_by_file_id(self, file_id: str, project_id: Optional[str] = None):
        """
        Get files by file ID.
        GET /file/{file_id}/?projectID=...

        Retrieve File by ID.

        Use this endpoint to retrieve detailed information about a specific file within your 
        Wexa.ai environment by providing its unique file_id. This functionality allows you to 
        access metadata such as the file's name, size, type, associated tags, and the timestamp 
        of when it was uploaded. It's essential for managing and monitoring the files your 
        AI coworkers utilize.

        Args:
            file_id: The unique identifier of the file (required)
            project_id: The unique identifier of the project (optional)

        Returns:
            File object containing detailed information including file name, size, type, 
            associated tags, and upload timestamp.

        Example:
            >>> file = client.files.get_by_file_id(
            ...     file_id="file-id-123",
            ...     project_id="68dcb579121a635f13002bf7"
            ... )
        """
        params = {"projectID": project_id} if project_id else None
        return self.http.request("GET", f"/file/{file_id}/", params=params)

    def get_connector_by_file_id(self, project_id: str, file_id: str):
        """
        Get connector by file ID.
        GET /file/{projectID}/{file_id}/connector

        Retrieve Connector by File ID.

        Use this endpoint to retrieve the connector associated with a specific file within a project 
        in your Wexa.ai environment. This functionality allows you to access metadata about the 
        connector, such as its type, configuration, and status, facilitating the management and 
        monitoring of file integrations.

        Args:
            project_id: The unique identifier of the project (required)
            file_id: The unique identifier of the file (required)

        Returns:
            Connector object containing metadata about the connector including its type, 
            configuration, and status.

        Example:
            >>> connector = client.files.get_connector_by_file_id(
            ...     project_id="68dcb579121a635f13002bf7",
            ...     file_id="file-id-123"
            ... )
        """
        return self.http.request("GET", f"/file/{project_id}/{file_id}/connector")

    # GET /files/{projectID}/connector/{connector_id}
    def list_by_connector(self, project_id: str, connector_id: str):
        """
        Get files by connector ID.
        GET /files/{projectID}/connector/{connector_id}

        Retrieve Files by Connector ID.

        This endpoint allows you to retrieve a list of files associated with a specific connector 
        within a given project in your Wexa.ai environment. By providing the projectID and 
        connector_id, you can access metadata such as file names, sizes, types, and associated tags, 
        facilitating the management and monitoring of files linked to external integrations.

        Args:
            project_id: The unique identifier of the project (required)
            connector_id: The unique identifier of the connector (required)

        Returns:
            List of files associated with the connector, containing metadata such as file names, 
            sizes, types, and associated tags.

        Example:
            >>> files = client.files.list_by_connector(
            ...     project_id="68dcb579121a635f13002bf7",
            ...     connector_id="connector-id-123"
            ... )
        """
        return self.http.request("GET", f"/files/{project_id}/connector/{connector_id}")
