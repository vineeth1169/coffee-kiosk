def test_index_page_loads(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'Coffee Shop Live Dashboard' in resp.data
