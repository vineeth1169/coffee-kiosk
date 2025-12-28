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

      // sizes (as selectable badges)
      let sizesHtml = '';
      if (item.sizes && item.sizes.length) {
        item.sizes.forEach((sz, i) => {
          const sel = i === 0 ? ' selected' : '';
          sizesHtml += `<span class="badge${sel}" data-size="${sz.name}" data-price="${sz.price}">${sz.name}</span>`;
        });
        sizesHtml = `<div class="sizes" aria-hidden="true">${sizesHtml}</div>`;
      }

      // top modifiers (show up to 3 representative options as chips for quick discovery)
      let modsHtml = '';
      if (item.modifiers) {
        // flatten first options from modifier groups
        const flat = [];
        Object.values(item.modifiers).forEach((arr) => {
          if (Array.isArray(arr)) arr.forEach(o => flat.push(o));
        });
        flat.slice(0,3).forEach((m) => {
          modsHtml += `<span class="chip" data-mod="${m.name}">${m.name}</span>`;
        });
        if (modsHtml) modsHtml = `<div class="mods">${modsHtml}</div>`;
      }

      card.innerHTML = `
        <div class="card-header"><span class="icon">${icon}</span><div class="title-wrap"><h4>${item.name}</h4><div class="small-tag">${item.tags && item.tags.length ? item.tags.join(', ') : ''}</div></div></div>
        <p class="muted">${item.category}</p>
        ${sizesHtml}
        ${modsHtml}
        <div class="price">Starting at $${item.base_price.toFixed(2)}</div>
        <div class="card-actions">
          <button class="btn btn-outline quick-add" data-name="${item.name}">Add</button>
          <button class="btn btn-primary customize" data-name="${item.name}">Customize</button>
          <button class="btn btn-info info" data-name="${item.name}">Info</button>
        </div>
      `;
      // helpful for debugging/selection
      card.dataset.name = item.name;
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

  // Quick add / info / customize handlers (also handle badge/chip clicks)
  menuGrid.addEventListener('click', (e) => {
    if (e.target.matches('.quick-add')) {
      const name = e.target.dataset.name;
      const btn = e.target;
      const card = btn.closest('.menu-card');
      const item = menu.find(m => m.name === name);
      if (!item || !card) return;
      // find selected size badge on the card
      const sel = card.querySelector('.badge.selected');
      const size = sel ? sel.dataset.size : undefined;
      const sizePrice = sel ? Number(sel.dataset.price) || 0 : 0;
      const total = Number(item.base_price) + sizePrice;
      const opts = {};
      if (size) opts.size = size;
      cart.push({ name: item.name, qty: 1, opts, total });
      renderCart();
    } else if (e.target.matches('.customize')) {
      const name = e.target.dataset.name;
      const item = menu.find(m => m.name === name);
      openCustomizeModal(item);
    } else if (e.target.matches('.info')) {
      const name = e.target.dataset.name;
      const item = menu.find(m => m.name === name);
      openDetailsModal(item);
    } else if (e.target.matches('.badge')) {
      // size badge clicked: toggle selection within this sizes container
      const badge = e.target;
      const container = badge.parentElement;
      const badges = container.querySelectorAll('.badge');
      badges.forEach(b => b.classList.remove('selected'));
      badge.classList.add('selected');
    } else if (e.target.matches('.chip')) {
      // chips are discovery-only (visual); toggle selected state for quick feedback
      e.target.classList.toggle('selected');
    }
  });

  // Modal logic
  const modal = document.getElementById('customize-modal');
  const modalBody = document.getElementById('modal-body');
  const modalClose = document.getElementById('modal-close');
  const modalCancel = document.getElementById('modal-cancel');
  const modalAddBtn = document.getElementById('modal-add');
  // Details modal elements
  const detailsModal = document.getElementById('details-modal');
  const detailsClose = document.getElementById('details-close');
  const detailsCancel = document.getElementById('details-cancel');
  const detailsCustomize = document.getElementById('details-customize');
  const detailsTitle = document.getElementById('details-title');
  const detailsTags = document.getElementById('details-tags');
  const detailsDesc = document.getElementById('details-desc');
  const detailsSizes = document.getElementById('details-sizes');

  let activeItem = null;
  let previouslyFocused = null;

  function openCustomizeModal(item) {
    // item may come with `.details` (notes) from the details modal; keep a copy
    const notes = item.details || '';
    // preserve a shallow copy so we don't mutate original menu objects
    const modalItem = Object.assign({}, item);
    modalItem.details = notes;

    activeItem = modalItem;
    modalBody.innerHTML = '';
    // Sizes
    if (modalItem.sizes && modalItem.sizes.length) {
      const sizeField = document.createElement('div');
      sizeField.innerHTML = '<label>Size:</label>';
      modalItem.sizes.forEach((sz, i) => {
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

    // Notes (pre-filled when coming from details modal)
    const notes = document.createElement('div');
    notes.innerHTML = '<label>Notes / Research:<br/><textarea id="modal-notes" rows="3" style="width:100%;"></textarea></label>';
    modalBody.appendChild(notes);

    // populate notes if item had them
    const notesInput = modalBody.querySelector('#modal-notes');
    if(item.details) notesInput.value = item.details || '';

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

  // Details modal handlers
  function openDetailsModal(item){
    if(!item) return;
    activeItem = item;
    detailsTitle.textContent = item.name;
    detailsTags.textContent = item.tags && item.tags.length ? item.tags.join(' · ') : '';
    detailsDesc.textContent = item.description || `A lovely ${item.category.toLowerCase()} crafted with care.`;
    detailsSizes.textContent = item.sizes && item.sizes.length ? 'Sizes: ' + item.sizes.map(s => `${s.name} (+$${s.price.toFixed(2)})`).join(', ') : '';

    previouslyFocused = document.activeElement;
    detailsModal.classList.add('open');
    detailsModal.setAttribute('aria-hidden','false');
    detailsModal.focus();
    const first = detailsModal.querySelector('button, a, input');
    if(first) first.focus();
  }

  function closeDetails(){
    detailsModal.classList.remove('open');
    detailsModal.setAttribute('aria-hidden','true');
    if(previouslyFocused && previouslyFocused.focus){ previouslyFocused.focus(); }
    activeItem = null;
  }

  detailsClose.addEventListener('click', closeDetails);
  detailsCancel.addEventListener('click', closeDetails);
  detailsCustomize.addEventListener('click', () => {
    if(activeItem){
      // capture notes locally, close details modal, then open customize with notes preserved
      const notesEl = document.getElementById('details-notes');
      const notes = notesEl ? (notesEl.value || '') : (activeItem.details || '');
      const itemCopy = Object.assign({}, activeItem, { details: notes });
      closeDetails();
      openCustomizeModal(itemCopy);
    }
  });

  // allow Esc / Enter key behavior on details modal
  detailsModal.addEventListener('keydown', (e) => {
    if(e.key === 'Escape') { e.preventDefault(); closeDetails(); }
    if(e.key === 'Enter') { e.preventDefault(); detailsCustomize.click(); }
  });
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

    // capture notes from modal notes textarea
    const notesInput = modalBody.querySelector('#modal-notes');
    const details = notesInput ? (notesInput.value || '') : (activeItem.details || '');

    total = total * qty;
    cart.push({ name: activeItem.name, qty, opts, total, details });
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