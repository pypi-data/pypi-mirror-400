from wexa_sdk import WexaClient


def test_knowledgebase_upload_builds_correct_request(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    captured = {}

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        captured["method"] = method
        captured["path"] = path
        captured["params"] = params
        captured["json"] = json
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    body = {"source_type": "STORAGE", "filenames": ["report.pdf"], "tags": ["Invoices"]}
    res = c.knowledgebase.upload(project_id="proj", container_name="bucket", body=body)  # type: ignore[arg-type]

    assert captured["method"] == "POST"
    assert captured["path"] == "/files/upload"
    assert captured["params"] == {"projectID": "proj", "container_name": "bucket"}
    assert captured["json"] == body
    assert res == {"ok": True}



