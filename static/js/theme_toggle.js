/* Theme switcher for LMS: supports light/dark with persistence */
(function () {
  if (typeof window === 'undefined' || typeof document === 'undefined') return;

  var THEME_KEY = 'lms-theme';
  var LIGHT = 'light';
  var DARK = 'dark';

  function isValidTheme(theme) {
    return theme === LIGHT || theme === DARK;
  }

  function getStoredTheme() {
    try {
      var saved = window.localStorage.getItem(THEME_KEY);
      return isValidTheme(saved) ? saved : null;
    } catch (error) {
      return null;
    }
  }

  function getSystemTheme() {
    try {
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return DARK;
      }
    } catch (error) {
      return LIGHT;
    }
    return LIGHT;
  }

  function getInitialTheme() {
    return getStoredTheme() || getSystemTheme();
  }

  function persistTheme(theme) {
    try {
      window.localStorage.setItem(THEME_KEY, theme);
    } catch (error) {
      return;
    }
  }

  function updateToggleUI(theme) {
    var toggles = document.querySelectorAll('[data-theme-toggle]');
    var switchToDark = theme !== DARK;
    var label = switchToDark ? 'Dark mode' : 'Light mode';

    toggles.forEach(function (toggle) {
      toggle.setAttribute('aria-label', 'Switch to ' + label.toLowerCase());
      toggle.setAttribute('title', 'Switch to ' + label.toLowerCase());

      var icon = toggle.querySelector('[data-theme-icon]');
      if (icon) {
        icon.classList.remove('fa-sun', 'fa-moon');
        icon.classList.add(switchToDark ? 'fa-moon' : 'fa-sun');
      }

      var text = toggle.querySelector('[data-theme-label]');
      if (text) {
        text.textContent = label;
      }
    });
  }

  function applyTheme(theme, shouldPersist) {
    var resolvedTheme = isValidTheme(theme) ? theme : LIGHT;
    document.documentElement.setAttribute('data-theme', resolvedTheme);
    document.documentElement.setAttribute('data-bs-theme', resolvedTheme);
    document.documentElement.style.colorScheme = resolvedTheme;
    updateToggleUI(resolvedTheme);
    if (shouldPersist) persistTheme(resolvedTheme);
  }

  function toggleTheme() {
    var current = document.documentElement.getAttribute('data-theme') || LIGHT;
    applyTheme(current === DARK ? LIGHT : DARK, true);
  }

  document.addEventListener('DOMContentLoaded', function () {
    applyTheme(document.documentElement.getAttribute('data-theme') || getInitialTheme(), false);

    var toggles = document.querySelectorAll('[data-theme-toggle]');
    toggles.forEach(function (toggle) {
      toggle.addEventListener('click', function (event) {
        event.preventDefault();
        toggleTheme();
      });
    });
  });

  applyTheme(getInitialTheme(), false);
})();
