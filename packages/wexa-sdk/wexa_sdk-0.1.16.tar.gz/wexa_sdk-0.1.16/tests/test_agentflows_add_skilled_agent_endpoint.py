from wexa_sdk import WexaClient


def test_add_skilled_agent_builds_correct_request(monkeypatch):
    captured = {}

    def fake_request(method, path, *, params=None, json=None, headers=None):
        captured["method"] = method
        captured["path"] = path
        captured["params"] = params
        captured["json"] = json
        return {"ok": True}

    c = WexaClient(base_url="https://testing.api.wexa.ai", api_key="k")
    monkeypatch.setattr(c.agentflows.http, "request", fake_request)

    body = {"role": "r", "skills": ["s1"], "llm": {"model": "m", "max_tokens": 1, "temperature": 0}}
    res = c.agentflows.add_skilled_agent("af1", projectID="p1", body=body)

    assert captured["method"] == "POST"
    assert captured["path"] == "/agentflow/af1/skilled"
    assert captured["params"] == {"projectID": "p1"}
    assert captured["json"] == body
    assert res == {"ok": True}


def test_get_by_user_and_project_builds_correct_request(monkeypatch):
    captured = {}

    def fake_request(method, path, *, params=None, json=None, headers=None):
        captured["method"] = method
        captured["path"] = path
        return {"ok": True}

    c = WexaClient(base_url="https://testing.api.wexa.ai", api_key="k")
    monkeypatch.setattr(c.agentflows.http, "request", fake_request)

    res = c.agentflows.get_by_user_and_project("af1", "u1", "p1")
    assert captured["method"] == "GET"
    assert captured["path"] == "/agentflow/af1/user/u1/project/p1"
    assert res == {"ok": True}



