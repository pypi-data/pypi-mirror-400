from wexa_sdk import WexaClient


def test_executions_endpoints_build_correct_requests(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    # start
    payload = {
        "agentflow_id": "af1",
        "executed_by": "u1",
        "goal": "g",
        "input_variables": {"k": "v"},
        "projectID": "p1",
    }
    c.executions.start(payload, projectID="p1")
    # get
    c.executions.get("e1")
    # monitor
    c.executions.monitor("af1")
    # pause
    c.executions.pause("e1")
    # resume
    c.executions.resume("e1")
    # cancel
    c.executions.cancel("e1")
    # execute existing
    c.executions.execute("e1", projectID="p1")

    # Assertions
    assert calls[0][0] == "POST" and calls[0][1] == "/execute_flow" and calls[0][2] == {"projectID": "p1"}
    assert calls[1][0] == "GET" and calls[1][1] == "/execute_flow/e1"
    assert calls[2][0] == "GET" and calls[2][1] == "/execute_flow/af1/monitor"
    assert calls[3][0] == "POST" and calls[3][1] == "/execute_flow/e1/pause"
    assert calls[4][0] == "POST" and calls[4][1] == "/execute_flow/e1/resume"
    assert calls[5][0] == "POST" and calls[5][1] == "/execute_flow/e1/cancel"
    assert calls[6][0] == "POST" and calls[6][1] == "/execute_flow/e1/execute" and calls[6][2] == {"projectID": "p1"}



