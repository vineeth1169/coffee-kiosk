# File: /coffee-kiosk/coffee-kiosk/tests/test_kiosk.py

import unittest
from src.kiosk import Kiosk
from src.menu import Menu
from src.cart import Cart

class TestKiosk(unittest.TestCase):

    def setUp(self):
        self.kiosk = Kiosk()
        self.menu = Menu()
        self.cart = Cart()

    def test_add_item_to_cart(self):
        self.kiosk.add_to_cart('Coffee')
        self.assertIn('Coffee', self.kiosk.cart.items)

    def test_checkout(self):
        self.kiosk.add_to_cart('Latte')
        total_before_checkout = self.kiosk.cart.total_price()
        self.kiosk.checkout()
        self.assertEqual(len(self.kiosk.cart.items), 0)
        self.assertNotEqual(total_before_checkout, self.kiosk.cart.total_price())

    def test_cancel_action(self):
        self.kiosk.add_to_cart('Espresso')
        self.kiosk.cancel()
        self.assertEqual(len(self.kiosk.cart.items), 0)

    def test_clear_cart(self):
        self.kiosk.add_to_cart('Cappuccino')
        self.kiosk.cart.clear()
        self.assertEqual(len(self.kiosk.cart.items), 0)

    def test_menu_display(self):
        menu_items = self.menu.display()
        self.assertEqual(len(menu_items), 7)

    def test_case_insensitive_add(self):
        # add using lowercase names — should be accepted
        self.kiosk.add_to_cart('latte')
        self.assertIn('latte', self.kiosk.cart.items)
        self.kiosk.add_to_cart('coffee')
        self.assertIn('coffee', self.kiosk.cart.items)
        # total should reflect added items
        self.assertGreater(self.kiosk.cart.total_price(), 0)

if __name__ == '__main__':
    unittest.main()