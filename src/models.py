from datetime import datetime
from .extensions import db

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')

    def as_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'customer': self.customer_name,  # alias for frontend convenience
            'created_at': self.created_at.isoformat(),
            'total': float(self.total),
            'items': [i.as_dict() for i in self.items]
        }

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price),
            'quantity': self.quantity
        }
