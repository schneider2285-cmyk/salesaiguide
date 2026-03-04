(function () {
  'use strict';

  // ── Search index ────────────────────────────────────────────────────────────

  var TOOLS = [
    { name: 'Instantly.ai',        url: '/tools/instantly-review.html',   type: 'tool' },
    { name: 'Smartlead',           url: '/tools/smartlead-review.html',   type: 'tool' },
    { name: 'Lemlist',             url: '/tools/lemlist-review.html',      type: 'tool' },
    { name: 'Apollo.io',           url: '/tools/apollo-review.html',       type: 'tool' },
    { name: 'ZoomInfo',            url: '/tools/zoominfo-review.html',     type: 'tool' },
    { name: 'Lusha',               url: '/tools/lusha-review.html',        type: 'tool' },
    { name: 'Clay',                url: '/tools/clay-review.html',         type: 'tool' },
    { name: 'Clearbit',            url: '/tools/clearbit-review.html',     type: 'tool' },
    { name: 'Gong',                url: '/tools/gong-review.html',         type: 'tool' },
    { name: 'Chorus',              url: '/tools/chorus-review.html',       type: 'tool' },
    { name: 'Fireflies.ai',        url: '/tools/fireflies-review.html',    type: 'tool' },
    { name: 'Salesloft',           url: '/tools/salesloft-review.html',    type: 'tool' },
    { name: 'Outreach',            url: '/tools/outreach-review.html',     type: 'tool' },
    { name: 'HubSpot Sales Hub',   url: '/tools/hubspot-review.html',      type: 'tool' },
    { name: 'Close',               url: '/tools/close-review.html',        type: 'tool' },
    { name: 'Pipedrive',           url: '/tools/pipedrive-review.html',    type: 'tool' },
    { name: 'Lavender',            url: '/tools/lavender-review.html',     type: 'tool' },
    { name: 'Hunter.io',           url: '/tools/hunter-review.html',       type: 'tool' },
    { name: 'Aircall',             url: '/tools/aircall-review.html',      type: 'tool' },
    { name: 'Kixie',               url: '/tools/kixie-review.html',        type: 'tool' },
    { name: 'Dialpad',             url: '/tools/dialpad-review.html',      type: 'tool' },
    { name: 'JustCall',            url: '/tools/justcall-review.html',     type: 'tool' },
    { name: 'Orum',                url: '/tools/orum-review.html',         type: 'tool' },
    { name: 'Clari',               url: '/tools/clari-review.html',        type: 'tool' },
    { name: 'Freshsales',          url: '/tools/freshsales-review.html',   type: 'tool' },
    { name: 'Seamless.AI',         url: '/tools/seamless-ai-review.html',  type: 'tool' },
    { name: 'Mailshake',           url: '/tools/mailshake-review.html',    type: 'tool' },
    { name: 'Woodpecker',          url: '/tools/woodpecker-review.html',   type: 'tool' },
    { name: 'Reply.io',            url: '/tools/reply-io-review.html',     type: 'tool' },
    { name: 'Vidyard',             url: '/tools/vidyard-review.html',      type: 'tool' },
    { name: 'Calendly',            url: '/tools/calendly-review.html',     type: 'tool' },
    { name: 'Chili Piper',         url: '/tools/chili-piper-review.html',  type: 'tool' },
    { name: 'SavvyCal',            url: '/tools/savvycal-review.html',     type: 'tool' }
  ];

  var CATEGORIES = [
    { name: 'Cold Outreach',            url: '/categories/cold-outreach.html',             type: 'category' },
    { name: 'Lead Prospecting',         url: '/categories/lead-prospecting.html',           type: 'category' },
    { name: 'Data Enrichment',          url: '/categories/data-enrichment.html',            type: 'category' },
    { name: 'Conversation Intelligence',url: '/categories/conversation-intelligence.html',  type: 'category' },
    { name: 'Sales Engagement',         url: '/categories/sales-engagement.html',           type: 'category' },
    { name: 'CRM & Pipeline',           url: '/categories/crm-pipeline.html',               type: 'category' },
    { name: 'Sales Content',            url: '/categories/sales-content.html',              type: 'category' },
    { name: 'Sales Analytics',          url: '/categories/sales-analytics.html',            type: 'category' },
    { name: 'Dialers & Calling',        url: '/categories/dialers-calling.html',            type: 'category' },
    { name: 'Meeting Schedulers',       url: '/categories/meeting-schedulers.html',         type: 'category' }
  ];

  var INDEX = TOOLS.concat(CATEGORIES);
  var MAX_RESULTS = 6;

  // ── Styles ───────────────────────────────────────────────────────────────────

  var styleEl = document.createElement('style');
  styleEl.textContent = [
    '.search-dropdown {',
    '  position: absolute;',
    '  top: calc(100% + 6px);',
    '  left: 0;',
    '  right: 0;',
    '  background: var(--color-surface, #fff);',
    '  border: 1px solid var(--color-border, #e2e8f0);',
    '  border-radius: var(--radius-md, 8px);',
    '  box-shadow: 0 8px 24px rgba(0,0,0,0.12);',
    '  z-index: 9999;',
    '  overflow: hidden;',
    '}',
    '.search-dropdown__item {',
    '  display: flex;',
    '  align-items: center;',
    '  gap: 10px;',
    '  padding: 10px 14px;',
    '  text-decoration: none;',
    '  color: var(--color-text, #1a202c);',
    '  font-size: 0.875rem;',
    '  cursor: pointer;',
    '  border-bottom: 1px solid var(--color-border, #e2e8f0);',
    '  transition: background 0.1s;',
    '}',
    '.search-dropdown__item:last-child {',
    '  border-bottom: none;',
    '}',
    '.search-dropdown__item:hover,',
    '.search-dropdown__item:focus {',
    '  background: var(--color-surface-alt, #f7fafc);',
    '  outline: none;',
    '}',
    '.search-dropdown__badge {',
    '  font-size: 0.7rem;',
    '  font-weight: 600;',
    '  text-transform: uppercase;',
    '  letter-spacing: 0.04em;',
    '  padding: 2px 6px;',
    '  border-radius: 4px;',
    '  margin-left: auto;',
    '  flex-shrink: 0;',
    '}',
    '.search-dropdown__badge--tool {',
    '  background: var(--color-accent-subtle, #ebf4ff);',
    '  color: var(--color-accent, #2563eb);',
    '}',
    '.search-dropdown__badge--category {',
    '  background: var(--color-tag-bg, #f0fdf4);',
    '  color: var(--color-tag-text, #16a34a);',
    '}'
  ].join('\n');
  document.head.appendChild(styleEl);

  // ── DOM setup ────────────────────────────────────────────────────────────────

  var searchWrap = document.querySelector('.navbar__search');
  if (!searchWrap) { return; }

  var input = searchWrap.querySelector('input');
  if (!input) { return; }

  // Make the wrapper relatively positioned so the dropdown can anchor to it.
  searchWrap.style.position = 'relative';

  var dropdown = null;

  // ── Helpers ──────────────────────────────────────────────────────────────────

  function query(text) {
    var lower = text.toLowerCase().trim();
    if (!lower) { return []; }
    return INDEX.filter(function (item) {
      return item.name.toLowerCase().indexOf(lower) !== -1;
    }).slice(0, MAX_RESULTS);
  }

  function closeDropdown() {
    if (dropdown && dropdown.parentNode) {
      dropdown.parentNode.removeChild(dropdown);
    }
    dropdown = null;
  }

  function buildDropdown(results) {
    closeDropdown();

    var ul = document.createElement('ul');
    ul.className = 'search-dropdown';
    ul.setAttribute('role', 'listbox');
    ul.setAttribute('aria-label', 'Search results');

    results.forEach(function (item) {
      var li = document.createElement('li');
      li.setAttribute('role', 'option');

      var a = document.createElement('a');
      a.className = 'search-dropdown__item';
      a.href = item.url;

      var nameSpan = document.createElement('span');
      nameSpan.className = 'search-dropdown__name';
      nameSpan.textContent = item.name;

      var badge = document.createElement('span');
      badge.className = 'search-dropdown__badge search-dropdown__badge--' + item.type;
      badge.textContent = item.type === 'tool' ? 'Tool' : 'Category';

      a.appendChild(nameSpan);
      a.appendChild(badge);
      li.appendChild(a);
      ul.appendChild(li);
    });

    searchWrap.appendChild(ul);
    dropdown = ul;
  }

  // ── Event listeners ──────────────────────────────────────────────────────────

  input.addEventListener('input', function () {
    var results = query(input.value);
    if (results.length === 0) {
      closeDropdown();
    } else {
      buildDropdown(results);
    }
  });

  input.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeDropdown();
      input.blur();
    }
  });

  // Close when clicking outside the search widget.
  document.addEventListener('click', function (e) {
    if (!searchWrap.contains(e.target)) {
      closeDropdown();
    }
  });

  // Close when focus moves completely outside the search widget.
  document.addEventListener('focusin', function (e) {
    if (!searchWrap.contains(e.target)) {
      closeDropdown();
    }
  });

}());
