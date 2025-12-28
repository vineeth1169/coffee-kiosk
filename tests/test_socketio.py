import time
from src.models import Order
from src.extensions import db


def test_socketio_emits_on_order_creation(client, socketio_client):
    # Ensure no events initially
    socketio_client.get_received()

    payload = {"customer_name": "SocketUser", "items": [{"name": "Latte", "quantity": 1}]}
    r = client.post('/api/orders', json=payload)
    assert r.status_code == 201

    # give socketio a moment to process
    time.sleep(0.1)
    received = socketio_client.get_received()
    # should have events new_order, update_totals, per_item_sales
    event_names = [e['name'] for e in received]
    assert 'new_order' in event_names
    assert 'update_totals' in event_names
    assert 'per_item_sales' in event_names

    # Check that the newest order is in DB
    latest = Order.query.order_by(Order.created_at.desc()).first()
    assert latest.customer_name == 'SocketUser'


def test_update_totals_values(client, socketio_client):
    # create two orders
    client.post('/api/orders', json={"customer_name": "A", "items": [{"name": "Latte", "quantity": 1}]})
    client.post('/api/orders', json={"customer_name": "B", "items": [{"name": "Espresso", "quantity": 2}]})
    time.sleep(0.1)
    received = socketio_client.get_received()
    # find update_totals event
    totals = [e['args'][0] for e in received if e['name'] == 'update_totals']
    assert totals
    last_totals = totals[-1]
    assert 'total_orders' in last_totals and last_totals['total_orders'] >= 2
    assert 'total_revenue' in last_totals and float(last_totals['total_revenue']) > 0
