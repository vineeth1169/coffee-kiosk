import json
from src.models import Order, OrderItem
from src.extensions import db


def test_create_order_success(client, app):
    payload = {"customer_name": "Bob", "items": [{"name": "Latte", "quantity": 1}, {"name": "Espresso", "quantity": 2}]}
    resp = client.post('/api/orders', data=json.dumps(payload), content_type='application/json')
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['customer_name'] == 'Bob'
    assert 'id' in data
    # DB record exists
    saved = Order.query.get(data['id'])
    assert saved is not None
    assert len(saved.items) == 2


def test_create_order_validation(client):
    resp = client.post('/api/orders', data=json.dumps({}), content_type='application/json')
    assert resp.status_code == 400
    assert resp.get_json().get('error')


def test_list_orders(client, app):
    # create an order via models
    o = Order(customer_name='Carol', total=5.0)
    oi = OrderItem(name='Mocha', price=3.75, quantity=1)
    o.items.append(oi)
    db.session.add(o)
    db.session.commit()

    resp = client.get('/api/orders')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert any(d['customer_name'] == 'Carol' for d in data)


def test_create_order_with_customization(client, app):
    # Latte base 3.5, Grande +0.75, Almond milk +0.5 -> unit price 4.75
    payload = {"customer": "Dana", "items": [{"name": "Latte", "qty": 2, "opts": {"size": "Grande", "milk": ["Almond"]}}]}
    resp = client.post('/api/orders', data=json.dumps(payload), content_type='application/json')
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['customer_name'] == 'Dana'
    assert data['total'] == 9.5
    # DB record & items
    from src.models import Order
    saved = Order.query.get(data['id'])
    assert saved is not None
    assert saved.total == 9.5


def test_create_order_invalid_modifier(client, app):
    payload = {"customer": "X", "items": [{"name": "Latte", "qty": 1, "opts": {"milk": ["UnicornMilk"]}}]}
    resp = client.post('/api/orders', data=json.dumps(payload), content_type='application/json')
    assert resp.status_code == 400
    assert 'invalid modifier' in resp.get_json().get('error')


def test_create_order_invalid_size(client, app):
    payload = {"customer": "Y", "items": [{"name": "Espresso", "qty": 1, "opts": {"size": "Grande"}}]}
    resp = client.post('/api/orders', data=json.dumps(payload), content_type='application/json')
    assert resp.status_code == 400
    assert 'invalid size' in resp.get_json().get('error')
