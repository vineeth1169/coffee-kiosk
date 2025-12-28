from flask import Blueprint, request, jsonify, current_app
from .extensions import db, socketio
from .models import Order, OrderItem
from .menu import Menu

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/menu', methods=['GET'])
def get_menu():
    menu = Menu()
    items = menu.as_list()
    # Attach normalized modifiers to items so the frontend has everything it needs
    modifiers = menu.get_modifiers()
    for it in items:
        it['modifiers'] = modifiers
    return jsonify({
        'items': items,
        'modifiers': modifiers
    })

@bp.route('/orders', methods=['GET'])
def list_orders():
    orders = Order.query.order_by(Order.created_at.desc()).limit(50).all()
    return jsonify([o.as_dict() for o in orders])

@bp.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json() or {}
    # Accept either 'customer' (frontend) or 'customer_name' (legacy callers)
    customer = data.get('customer') or data.get('customer_name') or 'Guest'
    items = data.get('items', [])
    if not items:
        return jsonify({'error': 'items required'}), 400

    menu = Menu()
    items_list = menu.as_list()
    menu_map = {it['name'].lower(): it for it in items_list}
    modifiers = menu.get_modifiers()

    order = Order(customer_name=customer, total=0)
    total = 0.0

    for it in items:
        name = it.get('name')
        qty = int(it.get('qty') or it.get('quantity') or 1)
        opts = it.get('opts') or {}

        unit_price = 0.0
        menu_item = None
        if name:
            menu_item = menu_map.get(name.lower())
            if menu_item:
                unit_price = float(menu_item.get('base_price', 0.0))
                # size
                size_name = opts.get('size')
                if size_name:
                    if not menu_item.get('sizes'):
                        return jsonify({'error': f'size not available for {name}'}), 400
                    matched = False
                    for s in menu_item['sizes']:
                        if s.get('name') == size_name:
                            unit_price += float(s.get('price', 0.0))
                            matched = True
                            break
                    if not matched:
                        return jsonify({'error': f'invalid size "{size_name}" for {name}'}), 400
                # modifiers
                for grp, selected in opts.items():
                    if grp == 'size':
                        continue
                    # selected can be array of choices
                    choices = selected if isinstance(selected, list) else [selected]
                    grp_opts = modifiers.get(grp, [])
                    if not grp_opts:
                        return jsonify({'error': f'invalid modifier group "{grp}" for {name}'}), 400
                    for choice in choices:
                        found = False
                        for o in grp_opts:
                            if o.get('name') == choice:
                                unit_price += float(o.get('price', 0.0))
                                found = True
                                break
                        if not found:
                            return jsonify({'error': f'invalid modifier "{choice}" for group "{grp}" on item {name}'}), 400
        else:
            # fallback price supplied by client
            unit_price = float(it.get('price', 0.0))

        total += unit_price * qty
        oi = OrderItem(name=name or 'Item', price=unit_price, quantity=qty)
        order.items.append(oi)

    order.total = total
    db.session.add(order)
    db.session.commit()

    # Emit socket events (normalized shapes for frontend)
    socketio.emit('new_order', order.as_dict())
    count = Order.query.count()
    revenue = float(db.session.query(db.func.sum(Order.total)).scalar() or 0)
    totals_payload = {'orders': count, 'revenue': revenue, 'total_orders': count, 'total_revenue': revenue}
    socketio.emit('update_totals', totals_payload)

    # per-item sales
    items_sales = db.session.query(OrderItem.name, db.func.sum(OrderItem.quantity).label('qty')).group_by(OrderItem.name).all()
    per_item = {name: qty for name, qty in items_sales}
    socketio.emit('per_item_sales', per_item)

    return jsonify(order.as_dict()), 201
