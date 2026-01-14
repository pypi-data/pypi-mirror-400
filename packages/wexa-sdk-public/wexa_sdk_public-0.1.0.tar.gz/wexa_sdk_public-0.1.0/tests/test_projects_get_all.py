import os
from wexa_sdk import WexaClient


def test_projects_get_all_path_and_params(monkeypatch):
    base_url = os.getenv("WEXA_BASE_URL", "https://api.wexa.ai")
    api_key = os.getenv("WEXA_API_KEY", "key")

    c = WexaClient(base_url=base_url, api_key=api_key)
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        # Simulate API shape
        return {"items": [], "count": 0}

    # Patch HTTP layer to avoid real network
    c.http.request = fake_request  # type: ignore

    res = c.projects.get_all(
        status="published",
        user_id="66f3cdde22bc63eb7490e23c",
        org_id="66f3cdde22bc63eb7490e23e",
        page=1,
        limit=12,
    )

    # Assert method and path
    assert calls[0][0] == "GET"
    assert calls[0][1] == "/v1/project"  # versioned path

    # Assert query params
    assert calls[0][2] == {
        "status": "published",
        "userId": "66f3cdde22bc63eb7490e23c",
        "orgId": "66f3cdde22bc63eb7490e23e",
        "page": 1,
        "limit": 12,
    }

    # Assert returned structure from our fake
    assert res == {"items": [], "count": 0}
