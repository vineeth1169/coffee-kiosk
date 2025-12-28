document.addEventListener('DOMContentLoaded', () => {
  const socket = io();

  const customerInput = document.getElementById('customer');
  const cartEl = document.getElementById('cart');
  const submitBtn = document.getElementById('submit-order');
  const menuGrid = document.getElementById('menu-grid');

  let cart = [];
  let menu = [];

  async function fetchMenu() {
    const res = await fetch('/api/menu');
    if (!res.ok) return;
    const data = await res.json();
    menu = data.items;
    renderMenu();
  }

  function renderMenu() {
    menuGrid.innerHTML = '';
    menu.forEach((item) => {
      const card = document.createElement('div');
      card.className = 'menu-card';
      const icon = (item.category && item.category.toLowerCase().includes('espresso')) ? '☕️' : '🥤';
    card.innerHTML = `
        <div class="card-header"><span class="icon">${icon}</span><h4>${item.name}</h4></div>
        <p class="muted">${item.category}</p>
        <div class="price">Starting at $${item.base_price.toFixed(2)}</div>
        <div class="card-actions">
          <button class="btn btn-outline quick-add" data-name="${item.name}">Add</button>
          <button class="btn btn-primary customize" data-name="${item.name}">Customize</button>
        </div>
      `;
      menuGrid.appendChild(card);
    });
  }

  function renderCart() {
    cartEl.innerHTML = '';
    cart.forEach((it, idx) => {
      const li = document.createElement('li');
      li.textContent = `${it.name} x${it.qty} - $${it.total.toFixed(2)}`;
      cartEl.appendChild(li);
    });
  }

  // Quick add handler (use base price, qty 1)
  menuGrid.addEventListener('click', (e) => {
    if (e.target.matches('.quick-add')) {
      const name = e.target.dataset.name;
      const item = menu.find(m => m.name === name);
      if (!item) return;
      cart.push({ name: item.name, qty: 1, opts: {}, total: item.base_price });
      renderCart();
    } else if (e.target.matches('.customize')) {
      const name = e.target.dataset.name;
      const item = menu.find(m => m.name === name);
      openCustomizeModal(item);
    }
  });

  // Modal logic
  const modal = document.getElementById('customize-modal');
  const modalBody = document.getElementById('modal-body');
  const modalClose = document.getElementById('modal-close');
  const modalCancel = document.getElementById('modal-cancel');
  const modalAddBtn = document.getElementById('modal-add');
  let activeItem = null;
  let previouslyFocused = null;

  function openCustomizeModal(item) {
    activeItem = item;
    modalBody.innerHTML = '';
    // Sizes
    if (item.sizes && item.sizes.length) {
      const sizeField = document.createElement('div');
      sizeField.innerHTML = '<label>Size:</label>';
      item.sizes.forEach((sz, i) => {
        const id = `size-${i}`;
        sizeField.innerHTML += `<label><input type="radio" name="size" value="${sz.name}" ${i===0? 'checked':''}/> ${sz.name} (+$${sz.price.toFixed(2)})</label>`;
      });
      modalBody.appendChild(sizeField);
    }
    // Modifiers
    if (item.modifiers) {
      Object.entries(item.modifiers).forEach(([group, opts]) => {
        const g = document.createElement('div');
        g.innerHTML = `<label>${group}:</label>`;
        opts.forEach((opt) => {
          g.innerHTML += `<label><input type="checkbox" name="mod-${group}" value="${opt.name}" data-price="${opt.price}"/> ${opt.name} ${opt.price? '(+$'+opt.price.toFixed(2)+')':''}</label>`;
        });
        modalBody.appendChild(g);
      });
    }
    // Quantity
    const qty = document.createElement('div');
    qty.innerHTML = '<label>Quantity: <input id="modal-qty" type="number" value="1" min="1" /></label>';
    modalBody.appendChild(qty);

    // Manage focus and accessibility
    previouslyFocused = document.activeElement;
    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
    modal.focus();
    // focus first input inside modal body if present
    const firstInput = modalBody.querySelector('input, button, select, textarea');
    if (firstInput) firstInput.focus();
  }

  function closeModal() {
    modal.classList.remove('open');
    modal.setAttribute('aria-hidden', 'true');
    activeItem = null;
    // restore previously focused element
    if (previouslyFocused && previouslyFocused.focus) {
      previouslyFocused.focus();
    }
  }

  // Keyboard handling for modal (Escape to close, Enter to add)
  modal.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      e.preventDefault();
      closeModal();
    }
    if (e.key === 'Enter') {
      // If focus is within inputs in modal, treat Enter as add
      const active = document.activeElement;
      if (modal.contains(active)) {
        e.preventDefault();
        modalAddBtn.click();
      }
    }
  });

  modalClose.addEventListener('click', closeModal);
  modalCancel.addEventListener('click', closeModal);

  modalAddBtn.addEventListener('click', () => {
    if (!activeItem) return;
    // collect selections
    const size = modalBody.querySelector('input[name="size"]:checked');
    const qtyInput = modalBody.querySelector('#modal-qty');
    const qty = Number(qtyInput.value) || 1;
    let total = activeItem.base_price;
    if (size) {
      const sz = activeItem.sizes.find(s => s.name === size.value);
      if (sz) total += sz.price;
    }
    const opts = {};
    if (size) opts.size = size.value;
    const checkboxes = modalBody.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach((cb) => {
      if (cb.checked) {
        const group = cb.name.replace(/^mod-/, '');
        opts[group] = opts[group] || [];
        opts[group].push(cb.value);
        total += Number(cb.dataset.price) || 0;
      }
    });
    total = total * qty;
    cart.push({ name: activeItem.name, qty, opts, total });
    renderCart();
    closeModal();
  });

  submitBtn.addEventListener('click', async () => {
    const customer = customerInput.value.trim() || 'Guest';
    if (!cart.length) return alert('Cart is empty');
    const res = await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customer, items: cart }),
    });
    if (res.ok) {
      cart = [];
      renderCart();
      customerInput.value = '';
    } else {
      alert('Failed to submit');
    }
  });

  socket.on('new_order', (order) => {
    const orders = document.getElementById('orders');
    const li = document.createElement('li');
    li.textContent = `${order.customer}: $${order.total.toFixed(2)}`;
    orders.prepend(li);
  });

  socket.on('update_totals', (totals) => {
    const totalsEl = document.getElementById('totals');
    totalsEl.textContent = `Orders: ${totals.orders} — Revenue: $${totals.revenue.toFixed(2)}`;
  });

  socket.on('per_item_sales', (data) => {
    document.getElementById('per-item').textContent = JSON.stringify(data, null, 2);
  });

  fetchMenu();
});