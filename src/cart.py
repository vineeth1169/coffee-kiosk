from .menu import Menu

class Cart:
    def __init__(self):
        # store item names (strings) to match tests
        self.items = []

    def add_item(self, item):
        # accept either an item dict or an item name
        if isinstance(item, dict):
            name = item.get('name')
            if name:
                self.items.append(name)
        else:
            self.items.append(item)

    def clear_cart(self):
        self.items.clear()

    def clear(self):
        """Alias used by tests."""
        self.clear_cart()

    def total_price(self):
        # look up prices from Menu by name (supports aliases like 'Coffee')
        menu = Menu()
        total = 0.0
        for name in self.items:
            item = menu.get_item_by_name(name)
            if item:
                price = item.get('price') if 'price' in item else item.get('base_price', 0.0)
                total += float(price)
        return total

    def get_items(self):
        return self.items.copy()