from wexa_sdk import WexaClient


def test_projects_crud_paths(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    c.projects.create({"orgId": "o1", "projectName": "P"})
    c.projects.get_all()
    c.projects.get("p1")
    c.projects.update("p1", {"description": "d"})
    c.projects.delete("p1")

    assert calls[0][0] == "POST" and calls[0][1] == "/v1/project"
    assert calls[1][0] == "GET" and calls[1][1] == "/v1/project"
    assert calls[2][0] == "GET" and calls[2][1] == "/v1/project/p1"
    assert calls[3][0] == "PUT" and calls[3][1] == "/v1/project" and calls[3][2] == {"projectId": "p1"}
    assert calls[4][0] == "DELETE" and calls[4][1] == "/v1/project/p1"
