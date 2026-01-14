from wexa_sdk import WexaClient


def test_tables_new_endpoints(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    # create records by collection
    c.tables.create_records_by_collection("p1", "coll", [{"a": 1}])
    # delete records bulk
    c.tables.delete_records_bulk("p1", "t1", ["id1", "id2"])
    # add columns with ignore_existing_columns
    c.tables.add_columns("p1", "t1", [{"column_name": "x"}], ignore_existing_columns=True)
    # bulk update records
    c.tables.bulk_update_records("p1", "t1", records={"status": "ok"}, record_ids={"storage_ids": ["id1"]})
    # update column name
    c.tables.update_column_name("p1", column_id="c1", column_name="New", table_id="t1")
    # patch column
    c.tables.patch_column("t1", {"column_name": "y"})
    # delete column extended
    c.tables.delete_column_extended("p1", table_id="t1", column_id="c1")
    # rename table extended
    c.tables.rename_table_extended("p1", table_id="t1", table_name="NewTable")
    # column mapper
    c.tables.column_mapper(column_names=[{"column_name": "Name", "column_id": "c1"}], csv_headers=["Name"])
    # field count
    c.tables.field_count("p1", "t1", [{"field": "status", "op": "eq", "value": "ok"}])

    assert calls[0] == ("POST", "/storage/p1/coll", None, [{"a": 1}])
    assert calls[1] == ("DELETE", "/storage/p1/t1", None, {"storage_ids": ["id1", "id2"]})
    assert calls[2] == ("POST", "/column/storage/p1/t1", {"ignore_existing_columns": True}, [{"column_name": "x"}])
    assert calls[3] == ("PUT", "/bulk/storage/p1/t1", None, {"records": {"status": "ok"}, "record_ids": {"storage_ids": ["id1"]}})
    assert calls[4] == ("PUT", "/edit/columns/p1", None, {"column_id": "c1", "column_name": "New", "table_id": "t1"})
    assert calls[5] == ("PATCH", "/edit/columns/t1", None, {"column_name": "y"})
    assert calls[6] == ("DELETE", "/delete/column/p1", None, {"table_id": "t1", "column_id": "c1"})
    assert calls[7] == ("PUT", "/table/rename/p1", None, {"table_id": "t1", "table_name": "NewTable"})
    assert calls[8] == ("POST", "/table/column_mapper", None, {"column_names": [{"column_name": "Name", "column_id": "c1"}], "csv_headers": ["Name"]})
    assert calls[9] == ("POST", "/table/fieldcount/p1/t1", None, [{"field": "status", "op": "eq", "value": "ok"}])



