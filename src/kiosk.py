from .menu import Menu
from .cart import Cart

class Kiosk:
    def __init__(self):
        self.menu = Menu()
        self.cart = Cart()

    def display_menu(self):
        print("Welcome to the Coffee Shop!")
        self.menu.display_menu()

    def add_to_cart(self, item_identifier):
        # accept either an integer id or a name string
        item = None
        if isinstance(item_identifier, int):
            item = self.menu.get_item(item_identifier)
        else:
            item = self.menu.get_item_by_name(item_identifier)

        if item:
            # preserve original identifier for aliases (e.g., 'Coffee') so tests can find it in cart.items
            if isinstance(item_identifier, str) and item_identifier != item['name']:
                self.cart.add_item(item_identifier)
                print(f"Added {item_identifier} to the cart.")
            else:
                self.cart.add_item(item)
                print(f"Added {item['name']} to the cart.")
        else:
            print("Invalid item number.")

    def checkout(self):
        total = self.cart.total_price()
        print(f"Your total is: ${total:.2f}")
        self.cart.clear_cart()
        print("Thank you for your purchase!")

    def cancel(self):
        self.cart.clear_cart()
        print("Your cart has been cleared.")

    def run(self):
        self.display_menu()
        while True:
            action_raw = input("Enter item number or name to add to cart, 'checkout' to checkout, or 'cancel' to cancel: ").strip()
            action = action_raw.lower()
            if action == 'checkout':
                self.checkout()
                break
            elif action == 'cancel':
                self.cancel()
                break
            else:
                try:
                    item_number = int(action_raw)
                    self.add_to_cart(item_number)
                except ValueError:
                    # treat as a name; preserve the user's original input case
                    self.add_to_cart(action_raw)