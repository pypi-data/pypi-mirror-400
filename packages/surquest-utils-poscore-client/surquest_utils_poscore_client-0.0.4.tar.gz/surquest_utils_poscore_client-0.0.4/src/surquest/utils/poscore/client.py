"""
Client for POS Media Data Core API.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from .credentials import Credentials
import uuid
from .models import CampaignResponse, Campaign, InstallationStatusPayload, Blob


class Client:
    def __init__(self, credentials: Credentials) -> None:
        """
        Initialize the POS Core Client.

        Args:
            credentials: An instance of the Credentials class to handle authentication.
        """
        self.credentials = credentials
        # Reuse the session from credentials if available, otherwise create a new one
        self.session = self.credentials.session

    @staticmethod
    def _extract_filename(content_disposition: str) -> str:
        """Extract filename from a Content-Disposition header value.

        Returns 'unknown' when a filename cannot be determined.
        """
        filename = "unknown"
        if content_disposition:
            parts = content_disposition.split("filename=")
            if len(parts) > 1:
                filename = parts[1].strip().strip('"')

        return filename
    
    def get_campaigns(
        self,
        size: int = 250,
        page: int = 0,
        orderby: str = "created desc",
        expand: bool = True,
        fetch_all: bool = True,
        **kwargs: Any,
    ) -> List[Campaign]:
        """
        Retrieve a list of campaigns.

        Args:
            size: Number of records per page.
            page: Page number (0-based).
            orderby: Sorting criteria (e.g. "created desc").
            expand: Whether to expand related entities.
            fetch_all: Whether to fetch all pages or just the requested one.
            **kwargs: Additional query parameters.

        Returns:
            A list of campaigns (dictionaries).
        """
        endpoint = f"{self.credentials.base_url}/cm/campaigns"
        headers = self.credentials.authorization_header

        campaigns = []

        while True:
            params = {
                "size": size,
                "page": page,
                "orderby": orderby,
                "expand": str(expand).lower(),
            }
            params.update(kwargs)

            response = self.session.get(endpoint, params=params, headers=headers)
            response.raise_for_status()

            response_data = response.json()

            # Convert to CampaignResponse model to leverage Pydantic parsing
            campaign_response = CampaignResponse.model_validate(response_data)

            page_count = campaign_response.pageCount
            current_page = campaign_response.currentPage
            data = campaign_response.data

            campaigns.extend(data)

            if not fetch_all:
                break

            if page_count is not None and current_page is not None:
                if current_page >= page_count:
                    break

            page += 1

        return campaigns

    def get_campaign_installations(
        self,
        campaign_id: int,
        locations: Optional[List[int]] = None,
        cm_carriers: Optional[List[int]] = None,
        components: Optional[List[int]] = None,
        task_types: Optional[List[int]] = None,
    ) -> InstallationStatusPayload:
        """
        Fetch campaign installations progress summary.

        Args:
            campaign_id: The ID of the campaign.
            locations: List of locations to filter by.
            cm_carriers: List of CM carriers to filter by.
            components: List of components to filter by.
            task_types: List of task types to filter by.

        Returns:
            The installation progress summary.
        """
        endpoint = f"{self.credentials.base_url}/cm/campaigns/{campaign_id}/installationprogresssummary"
        headers = self.credentials.authorization_header

        payload = {
            "locations": locations or [],
            "cmCarriers": cm_carriers or [],
            "components": components or [],
            "taskTypes": task_types or [],
        }

        response = self.session.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()

        response_data = response.json()

        installation_status = InstallationStatusPayload.model_validate(response_data)

        return installation_status

    def fetch_document(self, document_id: uuid.UUID, thumbnail: bool = False) -> Blob:
        """Fetch a document by its ID via endpoint: https://pos-core.pos-media.eu/gate/api/v1/cm/documents/dc85d712-dc49-4e07-bb6c-876a6aa97ec6

        Args:
            document_id: The UUID of the document to fetch.
            thumbnail: Whether to fetch the thumbnail version.
        Returns:
            The document content as bytes.
        """
        endpoint = f"{self.credentials.base_url}/cm/documents/{document_id}"
        headers = self.credentials.authorization_header

        if thumbnail is True:

            endpoint += "/thumbnail"

        params = {"skipValidation": True}

        response = self.session.get(endpoint, headers=headers, params=params)
        response.raise_for_status()

        content_disposition = response.headers.get("Content-Disposition", "")
        filename = self._extract_filename(content_disposition)

        return Blob(
            id=document_id,
            file_name=filename,
            content_type=response.headers.get(
                "Content-Type", "application/octet-stream"
            ),
            content=response.content,
        )

    def export_photos(
        self,
        campaign_id: int,
        all=False,
        locations: Optional[List[int]] = None,
        cm_carriers: Optional[List[int]] = None,
        components: Optional[List[int]] = None,
        task_types: Optional[List[int]] = None,
    ) -> Blob:
        """
        Export photos via the export endpoint: https://pos-core.pos-media.eu/gate/api/v1/cm/campaigns/{campaignId}/installationprogresssummary/photos

        Args:
            campaign_id: The ID of the campaign.
            all: Whether to include all photos.
            locations: List of locations to filter by.
            cm_carriers: List of CM carriers to filter by.
            components: List of components to filter by.
            task_types: List of task types to filter by.

        Returns:
            The exported photos content as archive bytes.
        """

        endpoint = f"{self.credentials.base_url}/cm/campaigns/{campaign_id}/installationprogresssummary/photos"
        headers = self.credentials.authorization_header
        params = {"all": str(all).lower()}
        payload = {
            "locations": locations or [],
            "cmCarriers": cm_carriers or [],
            "components": components or [],
            "taskTypes": task_types or [],
        }
        response = self.session.post(endpoint, headers=headers, params=params, json=payload)

        response.raise_for_status()

        content_disposition = response.headers.get("Content-Disposition", "")
        filename = self._extract_filename(content_disposition)

        return Blob(
            id=campaign_id,
            file_name=filename,
            content_type=response.headers.get(
                "Content-Type", "application/octet-stream"
            ),
            content=response.content,
        )
