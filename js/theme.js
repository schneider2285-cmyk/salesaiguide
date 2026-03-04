/**
 * Dark mode toggle — icon management and click handlers
 * Theme attribute is set inline in <head> to prevent FOUC.
 * This file handles icon toggling and user interaction (loaded deferred).
 */
(function () {
  var STORAGE_KEY = 'salesaiguide-theme';

  function getTheme() {
    return document.documentElement.getAttribute('data-theme') || 'light';
  }

  function apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);

    // Update toggle button icons
    document.querySelectorAll('.theme-toggle').forEach(function (btn) {
      var sunIcon = btn.querySelector('.icon-sun');
      var moonIcon = btn.querySelector('.icon-moon');
      if (sunIcon && moonIcon) {
        sunIcon.style.display = theme === 'dark' ? 'block' : 'none';
        moonIcon.style.display = theme === 'dark' ? 'none' : 'block';
      }
      btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    });
  }

  // Initialize icons and bind clicks once DOM is ready
  document.addEventListener('DOMContentLoaded', function () {
    apply(getTheme());

    document.querySelectorAll('.theme-toggle').forEach(function (btn) {
      btn.addEventListener('click', function () {
        apply(getTheme() === 'dark' ? 'light' : 'dark');
      });
    });
  });

  // Respond to system preference changes (only if user hasn't explicitly chosen)
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
    if (!localStorage.getItem(STORAGE_KEY)) {
      apply(e.matches ? 'dark' : 'light');
    }
  });
})();
