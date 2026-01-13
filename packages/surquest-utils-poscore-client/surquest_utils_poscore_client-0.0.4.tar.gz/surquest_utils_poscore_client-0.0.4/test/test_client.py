import unittest
import os
import json
import uuid

from surquest.utils.poscore.credentials import Credentials
from surquest.utils.poscore.client import Client


class TestClientIntegration(unittest.TestCase):

    def setUp(self):
        creds_json = os.environ.get("POSCORE_CREDENTIALS")
        if not creds_json:
            self.skipTest("POSCORE_CREDENTIALS environment variable not set")

        try:
            creds = json.loads(creds_json)
            self.username = list(creds.keys())[0] if creds else None
            self.password = list(creds.values())[0] if creds else None
        except json.JSONDecodeError:
            self.fail("POSCORE_CREDENTIALS must be a valid JSON string")

        if not self.username or not self.password:
            self.fail("POSCORE_CREDENTIALS must contain 'username' and 'password'")

    def test_get_campaigns_big_page_size(self):
        """Test fetching campaigns with a large size parameter."""
        creds = Credentials(self.username, self.password)
        client = Client(creds)

        campaigns = client.get_campaigns(size=99999, fetch_all=False)

        assert isinstance(campaigns, list)
        assert len(campaigns) <= 99999

    def test_get_campaigns_page_vs_all(self):
        """Verify fetch_all collects at least as many items as a single page."""
        creds = Credentials(self.username, self.password)
        client = Client(creds)

        page = client.get_campaigns(size=5, fetch_all=False)
        all_ = client.get_campaigns(size=5, fetch_all=True)

        assert isinstance(page, list)
        assert isinstance(all_, list)
        assert len(page) <= 5
        assert len(all_) >= len(page)

    def test_get_campaigns_expand_toggle(self):
        """Call endpoint with expand True/False and ensure responses parse."""
        creds = Credentials(self.username, self.password)
        client = Client(creds)

        r_true = client.get_campaigns(size=3, expand=True, fetch_all=False)
        r_false = client.get_campaigns(size=3, expand=False, fetch_all=False)

        assert isinstance(r_true, list)
        assert isinstance(r_false, list)

    def test_get_campaigns_with_params(self):
        """Basic sanity-check when passing ordering and params."""
        creds = Credentials(self.username, self.password)
        client = Client(creds)

        res = client.get_campaigns(size=2, orderby="created desc", fetch_all=False)
        assert isinstance(res, list)

    def test_get_campaigns_installations(self):
        """Test fetching campaign installations summary."""
        creds = Credentials(self.username, self.password)
        client = Client(creds)

        # Use a known campaign ID for testing; replace with a valid one.
        campaign_id = 6737
        result = client.get_campaign_installations(campaign_id=campaign_id)

        assert result is not None

    def test_fetch_document_full_size(self):
        """Test fetching a document with full size."""
        creds = Credentials(self.username, self.password)
        client = Client(creds)

        # Document ID:
        document_id = uuid.UUID("e627e4e7-c5e5-4cbb-ae3a-56ccd7873c5d")
        blob = client.fetch_document(document_id=document_id, thumbnail=False)

        assert isinstance(blob.content, bytes)
        assert len(blob.content) > 15000  # Expecting a reasonably sized document
        assert isinstance(blob.content_type, str)
        assert isinstance(blob.file_name, str)

    def test_fetch_document_thumbnail(self):
        """Test fetching a document thumbnail."""
        creds = Credentials(self.username, self.password)
        client = Client(creds)

        # Document ID:
        document_id = uuid.UUID("e627e4e7-c5e5-4cbb-ae3a-56ccd7873c5d")
        payload = client.fetch_document(document_id=document_id, thumbnail=True)

        assert isinstance(payload.content, bytes)
        assert len(payload.content) < 15000  # Expecting a smaller thumbnail
        assert isinstance(payload.content_type, str)
        assert isinstance(payload.file_name, str)


    def test_export_photos(self):
        """Test exporting photos for a campaign."""
        creds = Credentials(self.username, self.password)
        client = Client(creds)

        # Use a known campaign ID for testing; replace with a valid one.
        campaign_id = 6695
        blob = client.export_photos(
            campaign_id=campaign_id,
            all=True
        )

        assert isinstance(blob.content, bytes)
        assert len(blob.content) > 0  # Expecting some content
        assert isinstance(blob.content_type, str)
        assert isinstance(blob.file_name, str)