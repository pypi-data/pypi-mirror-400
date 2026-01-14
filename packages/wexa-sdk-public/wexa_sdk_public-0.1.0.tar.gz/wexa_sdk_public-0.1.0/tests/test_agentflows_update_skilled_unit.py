from wexa_sdk import WexaClient


def test_agentflows_update_skilled_builds_request(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    captured = {}

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        captured["method"] = method
        captured["path"] = path
        captured["params"] = params
        captured["json"] = json
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    body = {
        "role": "assistant",
        "title": "Create a Call",
        "skills": ["skill-1"],
        "prompt": {"template": "t", "variables": [], "display_template": "d"},
        "context": [],
        "triggers": [],
        "llm": {"model": "m", "max_tokens": 1000, "temperature": 0},
        "role_description": "desc",
        "memory": {"memory_type": "lt"},
        "has_knowledge_base": False,
        "is_user_specific_task": False,
        "is_preview_mode_enabled": False,
    }

    resp = c.agentflows.update_skilled_agent(
        agentflow_id="aflow-1",
        agent_id="agent-1",
        projectID="proj-1",
        body=body,
    )

    assert captured["method"] == "POST"
    assert captured["path"] == "/agentflow/aflow-1/update/skilled/agent-1"
    assert captured["params"] == {"projectID": "proj-1"}
    assert captured["json"] == body
    assert resp == {"ok": True}
