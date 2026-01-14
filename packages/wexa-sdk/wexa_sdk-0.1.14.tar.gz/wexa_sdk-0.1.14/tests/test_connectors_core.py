from wexa_sdk import WexaClient


def test_connectors_core_actions_and_config(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    # action without connector_id, then with connector_id
    c.connectors.action("drive", "sync", body={"x": 1}, projectID="p1")
    c.connectors.action("drive", "sync", "cid1", body={"y": 2}, projectID="p1")

    # config
    c.connectors.set_config("drive", "p1", {"cfg": True})
    c.connectors.get_config("drive", "p1")

    assert calls[0] == (
        "POST",
        "/actions/drive/sync",
        {"projectID": "p1"},
        {"x": 1},
    )
    assert calls[1] == (
        "POST",
        "/actions/drive/sync/cid1",
        {"projectID": "p1"},
        {"y": 2},
    )
    assert calls[2] == (
        "POST",
        "/actions/drive/config",
        {"projectID": "p1"},
        {"cfg": True},
    )
    assert calls[3] == (
        "GET",
        "/actions/drive/config/p1",
        None,
        None,
    )
