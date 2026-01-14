from wexa_sdk import WexaClient


def test_inbox_endpoints(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    c.inbox.create({"x": 1})
    c.inbox.list("p1", limit=2, status="pending", type="preview", search_key="k", after_id="aid", view="ui")
    c.inbox.update_runtime("exec1", "p1", {"is_submitted": True, "values": {"x": "y"}, "agent_id": "a1"})
    c.inbox.update_anomaly("exec2", "p1", {"is_approved": True})
    c.inbox.update_preview("exec3", "p1", {"agent_id": "a1", "is_approved": False, "preview_input": {"k": "v"}})
    c.inbox.get("inb1", "p1")

    assert calls[0] == ("POST", "/inbox/create", None, {"x": 1})
    assert calls[1] == ("GET", "/inbox", {"projectID": "p1", "limit": 2, "status": "pending", "type": "preview", "search_key": "k", "after_id": "aid", "view": "ui"}, None)
    assert calls[2] == ("POST", "/inbox/update/runtime_input/exec1", {"projectID": "p1"}, {"is_submitted": True, "values": {"x": "y"}, "agent_id": "a1"})
    assert calls[3] == ("POST", "/inbox/update/anomaly_detection/exec2", {"projectID": "p1"}, {"is_approved": True})
    assert calls[4] == ("POST", "/inbox/update/preview/exec3", {"projectID": "p1"}, {"agent_id": "a1", "is_approved": False, "preview_input": {"k": "v"}})
    assert calls[5] == ("GET", "/inbox/inb1", {"projectID": "p1"}, None)
