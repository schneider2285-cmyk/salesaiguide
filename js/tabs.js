/**
 * Category tab switching
 * Tabs use data-tab attribute, panels use data-panel attribute
 */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var tabContainers = document.querySelectorAll('[data-tabs]');

    tabContainers.forEach(function (container) {
      var tabs = container.querySelectorAll('[data-tab]');
      var panelGroup = document.querySelector(
        '[data-panels="' + container.getAttribute('data-tabs') + '"]'
      );
      if (!panelGroup) return;

      var panels = panelGroup.querySelectorAll('[data-panel]');

      tabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
          var target = this.getAttribute('data-tab');

          // Update tab states
          tabs.forEach(function (t) { t.classList.remove('active'); });
          this.classList.add('active');

          // Update panel visibility
          panels.forEach(function (p) {
            if (p.getAttribute('data-panel') === target) {
              p.classList.add('active');
            } else {
              p.classList.remove('active');
            }
          });
        });
      });
    });
  });
})();
