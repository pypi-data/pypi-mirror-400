from wexa_sdk import WexaClient


def test_projects_create_posts_body(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = {}

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls["method"] = method
        calls["path"] = path
        calls["json"] = json
        return {"_id": "p1"}

    c.http.request = fake_request  # type: ignore

    body = {"orgId": "o1", "projectName": "Test", "description": "d", "coworker_role": "r"}
    res = c.projects.create(body)

    assert calls["method"] == "POST"
    assert calls["path"] == "/v1/project"
    assert calls["json"] == body
    assert res == {"_id": "p1"}
