/**
 * Compare bar state management
 * Add/remove tools (max 3), update UI
 */
(function () {
  var MAX_TOOLS = 3;
  var STORAGE_KEY = 'salesaiguide-compare';
  var tools = [];

  function load() {
    try {
      var stored = JSON.parse(localStorage.getItem(STORAGE_KEY));
      if (Array.isArray(stored)) tools = stored.slice(0, MAX_TOOLS);
    } catch (_) {
      tools = [];
    }
  }

  function save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tools));
  }

  function addTool(slug, name) {
    if (tools.length >= MAX_TOOLS) return false;
    if (tools.some(function (t) { return t.slug === slug; })) return false;
    tools.push({ slug: slug, name: name });
    save();
    render();
    syncCheckboxes();
    return true;
  }

  function removeTool(slug) {
    tools = tools.filter(function (t) { return t.slug !== slug; });
    save();
    render();
    syncCheckboxes();
  }

  function hasTool(slug) {
    return tools.some(function (t) { return t.slug === slug; });
  }

  function getTools() {
    return tools.slice();
  }

  function clear() {
    tools = [];
    save();
    render();
    syncCheckboxes();
  }

  function createFilledSlot(tool) {
    var slot = document.createElement('div');
    slot.className = 'compare-bar__slot';

    var nameSpan = document.createElement('span');
    nameSpan.textContent = tool.name;
    slot.appendChild(nameSpan);

    var removeBtn = document.createElement('button');
    removeBtn.className = 'compare-bar__slot-remove';
    removeBtn.setAttribute('data-slug', tool.slug);
    removeBtn.setAttribute('aria-label', 'Remove ' + tool.name);
    removeBtn.textContent = '\u00d7';
    removeBtn.addEventListener('click', function () {
      removeTool(tool.slug);
    });
    slot.appendChild(removeBtn);

    return slot;
  }

  function createEmptySlot() {
    var slot = document.createElement('div');
    slot.className = 'compare-bar__slot compare-bar__slot--empty';
    slot.textContent = 'Select a tool';
    return slot;
  }

  function render() {
    var bar = document.querySelector('.compare-bar');
    if (!bar) return;

    // Show/hide bar
    if (tools.length > 0) {
      bar.classList.add('visible');
    } else {
      bar.classList.remove('visible');
      return;
    }

    // Render slots
    var slotsContainer = bar.querySelector('.compare-bar__slots');
    if (!slotsContainer) return;

    // Clear existing slots using DOM methods
    while (slotsContainer.firstChild) {
      slotsContainer.removeChild(slotsContainer.firstChild);
    }

    for (var i = 0; i < MAX_TOOLS; i++) {
      if (tools[i]) {
        slotsContainer.appendChild(createFilledSlot(tools[i]));
      } else {
        slotsContainer.appendChild(createEmptySlot());
      }
    }

    // Update compare button
    var action = bar.querySelector('.compare-bar__action');
    if (action) {
      if (tools.length < 2) {
        action.classList.add('disabled');
        action.disabled = true;
        action.setAttribute('aria-disabled', 'true');
        action.removeAttribute('data-href');
      } else {
        action.classList.remove('disabled');
        action.disabled = false;
        action.setAttribute('aria-disabled', 'false');
        var slugs = tools.map(function (t) { return t.slug; }).sort();
        action.setAttribute('data-href', '/compare/' + slugs.join('-vs-') + '/');
      }
    }
  }

  function syncCheckboxes() {
    document.querySelectorAll('[data-compare-slug]').forEach(function (cb) {
      cb.checked = hasTool(cb.getAttribute('data-compare-slug'));
    });
  }

  // Initialize
  load();

  document.addEventListener('DOMContentLoaded', function () {
    render();
    syncCheckboxes();

    // Compare button navigation
    var actionBtn = document.querySelector('.compare-bar__action');
    if (actionBtn) {
      actionBtn.addEventListener('click', function () {
        var href = this.getAttribute('data-href');
        if (href) window.location.href = href;
      });
    }

    // Delegate checkbox changes
    document.addEventListener('change', function (e) {
      var cb = e.target.closest('[data-compare-slug]');
      if (!cb) return;
      var slug = cb.getAttribute('data-compare-slug');
      var name = cb.getAttribute('data-compare-name') || slug;
      if (cb.checked) {
        if (!addTool(slug, name)) {
          cb.checked = false; // max reached
        }
      } else {
        removeTool(slug);
      }
    });
  });

  // Public API
  window.CompareBar = {
    add: addTool,
    remove: removeTool,
    has: hasTool,
    get: getTools,
    clear: clear
  };
})();
