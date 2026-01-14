import pytest
from wexa_sdk import WexaClient


def test_projects_get_by_project_name_builds_correct_request(monkeypatch):
    captured = {}

    def fake_request(method, path, *, params=None, json=None, headers=None):
        captured["method"] = method
        captured["path"] = path
        captured["params"] = params
        captured["json"] = json
        captured["headers"] = headers
        return {"ok": True}

    c = WexaClient(base_url="https://testing.api.wexa.ai", api_key="265d37d8-3496-4758-b0d5-dc64cc29b444")
    monkeypatch.setattr(c.projects.http, "request", fake_request)

    res = c.projects.get_by_project_name("Wexa Recruit")

    assert captured["method"] == "GET"
    assert captured["path"] == "/project/projectName/Wexa%20Recruit"
    assert res == {"ok": True}


