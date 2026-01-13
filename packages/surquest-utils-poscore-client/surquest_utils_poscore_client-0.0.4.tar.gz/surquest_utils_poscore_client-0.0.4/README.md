# POS Media Data Core Python Client

Lightweight helper package for authenticating against POS Media Data Core and calling its Campaigns API from Python. The library exposes two primary objects:

- `Credentials`: exchanges a username/password for a short-lived Bearer token.
- `Client`: wraps Data Core endpoints (e.g., list campaigns, fetch campaign installations) using an injected `Credentials` instance.

## Installation

```bash
pip install surquest-utils-poscore-client
```

## Quickstart

```python
from surquest.utils.poscore.credentials import Credentials
from surquest.utils.poscore.client import Client
import uuid

# Create token provider
creds = Credentials(
    username="your_username",
    password="your_password",
    # Optional: base_url="https://pos-core.pos-media.eu/gate/api/v1"
)

# Wire the authenticated client
client = Client(credentials=creds)

# 1) List campaigns
campaigns = client.get_campaigns(
    size=50,
    orderby="created desc",
    fetch_all=False # Set to True to auto-paginate through all results
)
for campaign in campaigns:
    print(f"Campaign: {campaign.name} with id: `{campaign.id}`

# 2) Get campaign installations
installations = client.get_campaign_installations(
    campaign_id=12345,
    locations=[], # Optional filters
    cm_carriers=[],
    components=[],
    task_types=[]
)
print(installations)

# 3) Fetch a document
doc_id = uuid.UUID("dc85d712-dc49-4e07-bb6c-876a6aa97ec6")
blob = client.fetch_document(document_id=doc_id, thumbnail=False)
print(f"Downloaded {blob.file_name} ({blob.content_type})")

# 4) Export all photos
blob = client.export_photos(
    campaign_id=12345
)
```

## Concepts

- **Token handling**: `Credentials` handles authentication and attaches the Bearer token to each request. Refresh logic is encapsulated so callers do not manually manage tokens.
- **Thin HTTP wrapper**: `Client` keeps endpoints small and explicit; it accepts request parameters and returns parsed JSON (or content for documents).

## Common Usage Patterns

- **Pagination**: `get_campaigns` supports `fetch_all=True` to automatically retrieve all pages. If `fetch_all=False`, use `page` and `size` to paginate manually.
- **Filtering**: `get_campaign_installations` allows filtering by locations, carriers, components, and task types.
- **Document Retrieval**: `fetch_document` retrieves the binary content of a document along with its filename and content type.

## Error Handling

- **Authentication errors**: raised when credentials are invalid or tokens expire unexpectedly.
- **HTTP errors**: surfaced with status codes and response bodies to aid debugging; wrap calls in `try/except` as needed.

## Development

Development of this package is realized via **Dev Containers**. This ensures a consistent environment for all developers.

### Using Dev Containers (Recommended)

1.  Open the project in VS Code.
2.  When prompted, click **Reopen in Container** (or run the command `Dev Containers: Reopen in Container`).
3.  The environment will be automatically configured with all dependencies.
4.  Run tests using:
    ```bash
    pytest
    ```

## Support

In case you have any questions or suggestions please contact us:

Michal Švarc (michal.svarc@surquest.com)
