from src.models import Order, OrderItem
from src.extensions import db


def test_order_item_relationship(app):
    # create order and items and save to db
    o = Order(customer_name='Alice', total=0)
    oi1 = OrderItem(name='Latte', price=3.5, quantity=2)
    oi2 = OrderItem(name='Espresso', price=2.5, quantity=1)
    o.items.append(oi1)
    o.items.append(oi2)
    o.total = sum(i.price * i.quantity for i in o.items)
    db.session.add(o)
    db.session.commit()

    assert o.id is not None
    # reload
    from src.models import Order as OrderModel
    saved = OrderModel.query.get(o.id)
    assert saved is not None
    assert len(saved.items) == 2
    assert float(saved.total) == float(oi1.price * oi1.quantity + oi2.price * oi2.quantity)
