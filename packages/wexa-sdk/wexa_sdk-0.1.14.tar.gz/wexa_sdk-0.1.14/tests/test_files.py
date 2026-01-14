from wexa_sdk import WexaClient


def test_files_endpoints(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    c.files.upload_request("proj", "bucket", {"filenames": ["a.txt"]})
    c.files.get_by_file_id("file1", "proj")
    c.files.list_by_connector("proj", "conn1")

    assert calls[0][0] == "POST" and calls[0][1] == "/files/upload" and calls[0][2] == {"projectID": "proj", "container_name": "bucket"}
    assert calls[1][0] == "GET" and calls[1][1] == "/file/file1/" and calls[1][2] == {"projectID": "proj"}
    assert calls[2][0] == "GET" and calls[2][1] == "/files/proj/connector/conn1"
