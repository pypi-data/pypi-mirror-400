from __future__ import annotations
from typing import Any, Dict

from .core.http import HttpClient

class Marketplace:
    def __init__(self, http: HttpClient):
        self.http = http

    # GET /public/connectors/all?search_key=...&projectID=...&filter_type=...
    def list_connectors(self, *, search_key: str, projectID: str, filter_type: str):
        """
        Get all connectors.
        GET /public/connectors/all?search_key=...&projectID=...&filter_type=...

        Retrieve All Available Connectors.

        Use this endpoint to retrieve a comprehensive list of all connectors available in your 
        Wexa.ai environment. Connectors serve as bridges between your automation workflows and 
        external applications, enabling seamless data exchange and integration.

        Args:
            search_key: Search key for filtering connectors (required)
            projectID: The unique identifier of the project (required)
            filter_type: Type of filter to apply (e.g., "all") (required)

        Returns:
            List of available connectors containing metadata about each connector including 
            name, description, category, configuration details, and other relevant information.

        Example:
            >>> connectors = client.marketplace.list_connectors(
            ...     search_key="",
            ...     projectID="68072c6d6532ce93160f2db9",
            ...     filter_type="all"
            ... )
        """
        params: Dict[str, Any] = {"search_key": search_key, "projectID": projectID, "filter_type": filter_type}
        return self.http.request("GET", "/public/connectors/all", params=params)

    # GET /public/marketplace/coworkers?search_key=...&limit=...
    def list_coworkers(self, *, search_key: str, limit: int | str):
        """
        Get marketplace coworkers.
        GET /public/marketplace/coworkers?search_key=...&limit=...

        Retrieve All Marketplace Coworkers.

        Use this endpoint to retrieve a comprehensive list of all AI Coworkers available in the 
        Wexa.ai Marketplace. These pre-built automation solutions are designed to streamline 
        specific tasks or processes within your organization, enabling rapid deployment and 
        integration into your workflows.

        Args:
            search_key: Search key for filtering coworkers (required)
            limit: Maximum number of coworkers to retrieve (required, can be int or string, e.g., 20 or "20")

        Returns:
            List of marketplace coworkers containing metadata about each coworker including 
            name, description, category, configuration details, and other relevant information.

        Example:
            >>> coworkers = client.marketplace.list_coworkers(
            ...     search_key="",
            ...     limit="20"
            ... )
        """
        params: Dict[str, Any] = {"search_key": search_key, "limit": limit}
        return self.http.request("GET", "/public/marketplace/coworkers", params=params)

    # GET /public/marketplace/coworker/{coworker_id}
    def get_coworker_by_id(self, coworker_id: str):
        """
        Get marketplace coworker by id.
        GET /public/marketplace/coworker/{coworker_id}

        Retrieve a Specific AI Coworker from the Marketplace.

        Use this endpoint to retrieve detailed information about a specific AI Coworker available 
        in the Wexa.ai Marketplace by its unique coworker_id. This allows you to explore the 
        capabilities, features, and integration options of individual AI Coworkers before 
        onboarding them into your workflows.

        Args:
            coworker_id: The unique identifier of the coworker (required)

        Returns:
            Detailed information about the marketplace coworker including name, description, 
            capabilities, features, integration options, configuration details, and other 
            relevant information.

        Example:
            >>> coworker = client.marketplace.get_coworker_by_id(
            ...     coworker_id="coworker-id-123"
            ... )
        """
        return self.http.request("GET", f"/public/marketplace/coworker/{coworker_id}")

    # POST /marketplace/coworker/{coworker_id}/purchase?organization_id=...
    def purchase_coworker(self, coworker_id: str, *, organization_id: str, body: Dict[str, Any] | None = None):
        """
        Hire a coworker.
        POST /marketplace/coworker/{coworker_id}/purchase?organization_id=...

        Hire an AI Coworker from the Marketplace.

        Use this endpoint to hire a specific AI Coworker from the Wexa.ai Marketplace by providing 
        its unique coworker_id. Hiring a coworker integrates it into your selected workspace, 
        enabling it to perform predefined automation tasks and workflows tailored to your 
        organization's needs.

        Args:
            coworker_id: The unique identifier of the coworker to hire (required)
            organization_id: The unique identifier of the organization (required)
            body: Optional body containing additional configuration or metadata (optional)

        Returns:
            Hired coworker object containing metadata about the newly hired coworker including 
            integration details, workspace assignment, and other relevant information.

        Example:
            >>> result = client.marketplace.purchase_coworker(
            ...     coworker_id="coworker-id-123",
            ...     organization_id="67fdea40aac77be632954f0f",
            ...     body={}
            ... )
        """
        params = {"organization_id": organization_id}
        return self.http.request("POST", f"/marketplace/coworker/{coworker_id}/purchase", params=params, json=(body or {}))

    # GET /marketplace/coworker/update/{coworker_id}/check
    def check_coworker_update(self, coworker_id: str):
        """
        Check marketplace coworker update.
        GET /marketplace/coworker/update/{coworker_id}/check

        Check Marketplace Coworker Update.

        Use this endpoint to check if there are any updates available for a specific AI Coworker 
        from the Wexa.ai Marketplace by providing its unique coworker_id. This allows you to 
        verify whether the coworker has been updated with new features, bug fixes, or 
        improvements that you can apply to your workspace.

        Args:
            coworker_id: The unique identifier of the coworker to check for updates (required)

        Returns:
            Update check response containing information about available updates for the 
            marketplace coworker including version details, update status, and other 
            relevant information.

        Example:
            >>> update_info = client.marketplace.check_coworker_update(
            ...     coworker_id="coworker-id-123"
            ... )
        """
        return self.http.request("GET", f"/marketplace/coworker/update/{coworker_id}/check")
