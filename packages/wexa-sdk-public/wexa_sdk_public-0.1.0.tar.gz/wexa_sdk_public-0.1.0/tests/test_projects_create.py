from wexa_sdk import WexaClient


def test_projects_create_published(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"_id": "p123"}

    c.http.request = fake_request  # type: ignore

    body = {
        "orgId": "o1",
        "projectName": "My Project",
        "description": "desc",
        "coworker_role": "role",
        "status": "published",
    }

    res = c.projects.create(body)

    # Assert method, path, and payload
    assert calls[0][0] == "POST"
    assert calls[0][1] == "/v1/project"
    assert calls[0][2] is None  # params
    assert calls[0][3] == body  # json body
    assert res == {"_id": "p123"}


def test_projects_create_simple_published(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"_id": "p456"}

    c.http.request = fake_request  # type: ignore

    res = c.projects.create_simple(
        orgId="o1",
        projectName="Simple Project",
        description="desc2",
        coworker_role="role2",
        status="published",
    )

    assert calls[0][0] == "POST"
    assert calls[0][1] == "/v1/project"
    assert calls[0][2] is None
    assert calls[0][3] == {
        "orgId": "o1",
        "projectName": "Simple Project",
        "description": "desc2",
        "coworker_role": "role2",
        "status": "published",
    }
    assert res == {"_id": "p456"}
