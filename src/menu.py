class Menu:
    def __init__(self):
        # Each item includes sizes and optional modifiers to support customization
        self.items = {
            1: {"name": "Espresso", "base_price": 2.50, "category": "Espresso", "sizes": [{"id":"single","label":"Single","delta":0}], "tags": ["Popular"]},
            2: {"name": "Latte", "base_price": 3.50, "category": "Coffee", "sizes": [{"id":"tall","label":"Tall","delta":0},{"id":"grande","label":"Grande","delta":0.75},{"id":"venti","label":"Venti","delta":1.25}], "tags": ["Popular"]},
            3: {"name": "Cappuccino", "base_price": 3.00, "category": "Coffee", "sizes": [{"id":"tall","label":"Tall","delta":0},{"id":"grande","label":"Grande","delta":0.5}], "tags": []},
            4: {"name": "Americano", "base_price": 2.00, "category": "Coffee", "sizes": [{"id":"tall","label":"Tall","delta":0},{"id":"grande","label":"Grande","delta":0.5}], "tags": []},
            5: {"name": "Mocha", "base_price": 3.75, "category": "Coffee", "sizes": [{"id":"tall","label":"Tall","delta":0},{"id":"grande","label":"Grande","delta":0.75}], "tags": ["Seasonal"]},
            6: {"name": "Macchiato", "base_price": 3.25, "category": "Coffee", "sizes": [{"id":"single","label":"Single","delta":0}], "tags": []},
            7: {"name": "Flat White", "base_price": 3.50, "category": "Coffee", "sizes": [{"id":"tall","label":"Tall","delta":0},{"id":"grande","label":"Grande","delta":0.75}], "tags": []},
        }

        # Global modifiers available for customization
        self.modifiers = {
            "milk": [{"id":"whole","label":"Whole"},{"id":"two","label":"2%"},{"id":"almond","label":"Almond","delta":0.5},{"id":"oat","label":"Oat","delta":0.75}],
            "syrup": [{"id":"vanilla","label":"Vanilla","delta":0.5},{"id":"caramel","label":"Caramel","delta":0.5}],
            "shots": {"label":"Extra shot","delta":0.75}
        }

    def display_menu(self):
        print("Coffee Shop Menu:")
        for item_id, item in self.items.items():
            print(f"{item_id}. {item['name']} - ${item['base_price']:.2f}")

    def get_item(self, item_id):
        return self.items.get(item_id, None)

    def get_item_by_name(self, name):
        """Return an item dict by its name (case-insensitive) or common aliases."""
        if not name:
            return None
        name_lower = name.lower()
        # direct case-insensitive match
        for item in self.items.values():
            if item['name'].lower() == name_lower:
                return item
        # alias: 'coffee' -> 'Espresso'
        if name_lower == 'coffee':
            for item in self.items.values():
                if item['name'] == 'Espresso':
                    return item
        return None

    def as_list(self):
        """Return menu items as serializable list for the API.
        Normalizes sizes to a list of {name, price} so the UI can consume them easily.
        """
        result = []
        for item_id, item in self.items.items():
            it = item.copy()
            it['id'] = item_id
            # ensure numeric values are simple floats for JSON
            it['base_price'] = float(it['base_price'])
            # Normalize sizes: label/delta -> name/price
            sizes = []
            for s in it.get('sizes', []):
                sizes.append({
                    'name': s.get('label') or s.get('id'),
                    'price': float(s.get('delta', 0) or 0)
                })
            it['sizes'] = sizes
            result.append(it)
        return result

    def get_modifiers(self):
        """Return modifiers (milk, syrup, shots) for UI as group -> list of {name, price}."""
        out = {}
        for group, val in self.modifiers.items():
            if isinstance(val, dict):
                # single-option group (e.g., shots)
                out[group] = [{
                    'name': val.get('label') or group,
                    'price': float(val.get('delta', 0) or 0)
                }]
            else:
                # list of options
                opts = []
                for o in val:
                    opts.append({
                        'name': o.get('label') or o.get('id'),
                        'price': float(o.get('delta', 0) or 0)
                    })
                out[group] = opts
        return out


    def display(self):
        """Print and return the list of menu items (list of dicts)."""
        items = list(self.items.values())
        self.display_menu()
        return items

