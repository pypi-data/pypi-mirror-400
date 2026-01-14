from wexa_sdk import WexaClient


def test_list_coworker_schedules(monkeypatch):
    captured = {}

    def fake_request(method, path, *, params=None, json=None, headers=None):
        captured["method"] = method
        captured["path"] = path
        captured["params"] = params
        return {"ok": True}

    c = WexaClient(base_url="https://testing.api.wexa.ai", api_key="k")
    monkeypatch.setattr(c.schedules.http, "request", fake_request)

    res = c.schedules.list_coworker_schedules("cw1", projectID="p1", limit=15, page_no=1)
    assert captured["method"] == "GET"
    assert captured["path"] == "/schedules/coworker"
    assert captured["params"] == {"projectID": "p1", "limit": 15, "page_no": 1, "coworker_id": "cw1"}
    assert res == {"ok": True}


def test_create_coworker_schedule(monkeypatch):
    captured = {}

    def fake_request(method, path, *, params=None, json=None, headers=None):
        captured["method"] = method
        captured["path"] = path
        captured["params"] = params
        captured["json"] = json
        return {"ok": True}

    c = WexaClient(base_url="https://testing.api.wexa.ai", api_key="k")
    monkeypatch.setattr(c.schedules.http, "request", fake_request)

    body = {
        "coworker_id": "cw1",
        "goal": {"action": "run"},
        "template": "t",
        "display_template": "dt",
        "schedule": 123,
    }
    res = c.schedules.create_coworker_schedule(projectID="p1", body=body)  # type: ignore[arg-type]
    assert captured["method"] == "POST"
    assert captured["path"] == "/schedule/coworker"
    assert captured["params"] == {"projectID": "p1"}
    assert captured["json"] == body
    assert res == {"ok": True}


def test_get_update_delete_coworker_schedule(monkeypatch):
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):
        calls.append((method, path, params, json))
        return {"ok": True}

    c = WexaClient(base_url="https://testing.api.wexa.ai", api_key="k")
    monkeypatch.setattr(c.schedules.http, "request", fake_request)

    c.schedules.get_coworker_schedule("sid")
    c.schedules.update_coworker_schedule("sid", projectID="p1", body={"schedule": 456})  # type: ignore[arg-type]
    c.schedules.delete_coworker_schedule("sid", projectID="p1")

    assert calls[0][0] == "GET" and calls[0][1] == "/schedule/coworker/sid"
    assert calls[1][0] == "PATCH" and calls[1][1] == "/schedule/coworker/sid" and calls[1][2] == {"projectID": "p1"}
    assert calls[2][0] == "DELETE" and calls[2][1] == "/schedule/coworker/sid" and calls[2][2] == {"projectID": "p1"}


