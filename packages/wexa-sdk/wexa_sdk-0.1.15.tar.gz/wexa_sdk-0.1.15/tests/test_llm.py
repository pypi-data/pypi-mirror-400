from wexa_sdk import WexaClient


def test_llm_call_builds_correct_request(monkeypatch):
    captured = {}

    def fake_request(method, path, *, params=None, json=None, headers=None):
        captured["method"] = method
        captured["path"] = path
        captured["json"] = json
        return {"ok": True}

    c = WexaClient(base_url="https://testing.api.wexa.ai", api_key="265d37d8-3496-4758-b0d5-dc64cc29b444")
    monkeypatch.setattr(c.llm.http, "request", fake_request)

    body = {
        "model": "bedrock/amazon.nova-pro-v1",
        "messages": [{"role": "user", "content": "Hello, how are you?"}],
    }
    res = c.llm.llm_call(body)  # type: ignore[arg-type]

    assert captured["method"] == "POST"
    assert captured["path"] == "/llm/execute/calls"
    assert captured["json"] == body
    assert res == {"ok": True}


