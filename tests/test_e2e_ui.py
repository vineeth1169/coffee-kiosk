def test_customize_and_checkout(page, live_server):
    """E2E test: open UI, customize a Latte (Grande + Almond), add to cart, submit order and verify totals and keyboard/accessibility behavior."""
    base = live_server
    page.goto(base)

    # Wait for menu to render
    page.wait_for_selector('.menu-card')

    # Find Latte card and open customize
    latte = page.locator('.menu-card', has_text='Latte').first
    latte.locator('.customize').click()

    # Modal should open and focus should be inside the modal
    page.wait_for_selector('#customize-modal.open')
    assert page.locator('#customize-modal').is_visible()

    # Focus is on the first input in modal (size radio)
    is_focused = page.locator('input[name="size"]').first.evaluate('el => el === document.activeElement')
    assert is_focused

    # Press Escape to close and ensure modal hides
    page.keyboard.press('Escape')
    page.wait_for_selector('#customize-modal', state='hidden')

    # Re-open modal and use keyboard Enter to add
    latte.locator('.customize').click()
    page.wait_for_selector('#customize-modal.open')

    page.locator('input[name="size"][value="Grande"]').check()
    page.locator('input[type="checkbox"][value="Almond"]').check()
    page.fill('#modal-qty', '2')

    # Press Enter to add to cart (keyboard action)
    page.keyboard.press('Enter')
    page.wait_for_selector('#customize-modal', state='hidden')

    # Cart should show the item with computed total
    page.wait_for_selector('#cart li')
    cart_items = page.locator('#cart li').all_text_contents()
    assert any('Latte' in t and 'x2' in t and '$9.50' in t for t in cart_items)

    # Submit order
    page.fill('#customer', 'Eve')
    page.click('#submit-order')

    # Order should appear in live orders with the correct total
    page.wait_for_selector('#orders li')
    orders = page.locator('#orders li').all_text_contents()
    assert any('$9.50' in o for o in orders)