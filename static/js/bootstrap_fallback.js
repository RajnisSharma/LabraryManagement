/* eslint-disable no-var */
/* Minimal Bootstrap fallback for dropdown/collapse.
   Runs only if Bootstrap JS isn't available (e.g. CDN blocked). */

(function () {
  if (typeof window === 'undefined' || typeof document === 'undefined') return;
  if (window.bootstrap && (window.bootstrap.Dropdown || window.bootstrap.Collapse)) return;

  function closest(el, selector) {
    return el && el.closest ? el.closest(selector) : null;
  }

  function setExpanded(toggle, expanded) {
    if (!toggle) return;
    toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
  }

  function getDropdownParts(toggleEl) {
    var dropdown = closest(toggleEl, '.dropdown');
    if (!dropdown) return null;
    var menu = dropdown.querySelector('.dropdown-menu');
    return menu ? { dropdown: dropdown, toggle: toggleEl, menu: menu } : null;
  }

  function closeDropdown(parts) {
    if (!parts) return;
    parts.menu.classList.remove('show');
    parts.dropdown.classList.remove('show');
    parts.toggle.classList.remove('show');
    setExpanded(parts.toggle, false);
  }

  function closeAllDropdowns(exceptDropdown) {
    document.querySelectorAll('.dropdown.show').forEach(function (dd) {
      if (exceptDropdown && dd === exceptDropdown) return;
      var toggle = dd.querySelector('[data-bs-toggle="dropdown"]');
      var menu = dd.querySelector('.dropdown-menu');
      if (!toggle || !menu) return;
      closeDropdown({ dropdown: dd, toggle: toggle, menu: menu });
    });
  }

  function toggleDropdown(parts) {
    var isOpen = parts.menu.classList.contains('show');
    closeAllDropdowns(parts.dropdown);
    if (isOpen) {
      closeDropdown(parts);
      return;
    }
    parts.dropdown.classList.add('show');
    parts.toggle.classList.add('show');
    parts.menu.classList.add('show');
    setExpanded(parts.toggle, true);
  }

  function resolveCollapseTarget(toggleEl) {
    var sel = toggleEl.getAttribute('data-bs-target') || toggleEl.getAttribute('href');
    if (!sel || sel === '#') return null;
    try {
      return document.querySelector(sel);
    } catch (e) {
      return null;
    }
  }

  document.addEventListener('click', function (event) {
    var dropdownToggle = closest(event.target, '[data-bs-toggle="dropdown"]');
    if (dropdownToggle) {
      event.preventDefault();
      var parts = getDropdownParts(dropdownToggle);
      if (parts) toggleDropdown(parts);
      return;
    }

    // Close when clicking menu items (links/buttons)
    var menuItem = closest(event.target, '.dropdown-menu a, .dropdown-menu button');
    if (menuItem) {
      var parentDropdown = closest(menuItem, '.dropdown');
      if (parentDropdown) closeAllDropdowns();
      return;
    }

    // Close if click outside any dropdown
    if (!closest(event.target, '.dropdown-menu') && !closest(event.target, '.dropdown')) {
      closeAllDropdowns();
    }
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') closeAllDropdowns();
  });

  // Collapse fallback (navbar toggler)
  document.addEventListener('click', function (event) {
    var collapseToggle = closest(event.target, '[data-bs-toggle="collapse"]');
    if (!collapseToggle) return;
    var target = resolveCollapseTarget(collapseToggle);
    if (!target) return;
    event.preventDefault();
    var willShow = !target.classList.contains('show');
    target.classList.toggle('show', willShow);
    setExpanded(collapseToggle, willShow);
  });
})();

