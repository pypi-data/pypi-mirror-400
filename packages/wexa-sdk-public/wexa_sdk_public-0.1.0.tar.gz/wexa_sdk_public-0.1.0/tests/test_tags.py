from wexa_sdk import WexaClient


def test_tags_get_by_project_id_builds_correct_request(monkeypatch):
    c = WexaClient(base_url="https://app.wexa.ai", api_key="key")
    captured = {}

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        captured["method"] = method
        captured["path"] = path
        captured["params"] = params
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    res = c.tags.get_by_project_id("proj123")
    assert captured["method"] == "GET"
    assert captured["path"] == "/tagsbyprojectId/proj123"
    assert captured["params"] is None
    assert res == {"ok": True}



