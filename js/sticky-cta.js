(function () {
  'use strict';

  var STORAGE_KEY = 'salesaiguide-sticky-cta-dismissed';

  if (sessionStorage.getItem(STORAGE_KEY)) return;

  function init() {
    var heroEl = document.querySelector('.review-hero');
    var verdictEl = document.getElementById('verdict');
    if (!heroEl || !verdictEl) return;

    var titleEl = document.querySelector('.review-hero__title');
    var scoreEl = document.querySelector('.review-hero__score');
    var priceEl = document.querySelector('.review-hero__price');
    var goLink = document.querySelector('a[href*="/go/"]');

    if (!titleEl || !goLink) return;

    // Parse tool name from h1
    var rawTitle = titleEl.textContent.trim();
    var toolName = rawTitle.split(' Review')[0].trim();

    // Parse score
    var score = scoreEl ? scoreEl.textContent.trim().split('/')[0].trim() : '';

    // Parse price
    var priceText = '';
    if (priceEl) {
      var priceSource = priceEl.querySelector('a') || priceEl;
      priceText = priceSource.textContent.trim().replace(/\s+/g, ' ');
    }

    // Get affiliate URL
    var affiliateUrl = goLink.getAttribute('href');

    // Determine CTA text
    var specsCta = document.querySelector('.specs-cta');
    var isDemo = specsCta && specsCta.textContent.toLowerCase().indexOf('demo') !== -1;
    var ctaText = isDemo ? 'Request Demo \u2192' : 'Try Free \u2192';

    // Build bar using safe DOM methods
    var bar = document.createElement('div');
    bar.className = 'sticky-cta';
    bar.setAttribute('aria-label', 'Quick action bar');

    var inner = document.createElement('div');
    inner.className = 'sticky-cta__inner';

    var info = document.createElement('div');
    info.className = 'sticky-cta__info';

    var nameSpan = document.createElement('span');
    nameSpan.className = 'sticky-cta__name';
    nameSpan.textContent = toolName;
    info.appendChild(nameSpan);

    if (score) {
      var ratingSpan = document.createElement('span');
      ratingSpan.className = 'sticky-cta__rating';
      var starSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      starSvg.setAttribute('viewBox', '0 0 20 20');
      starSvg.setAttribute('aria-hidden', 'true');
      var starPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      starPath.setAttribute('d', 'M10 1.3l2.39 6.03h6.11l-4.95 3.94 1.86 6.23L10 13.77 4.59 17.5l1.86-6.23L1.5 7.33h6.11z');
      starSvg.appendChild(starPath);
      ratingSpan.appendChild(starSvg);
      var scoreText = document.createTextNode(score);
      ratingSpan.appendChild(scoreText);
      info.appendChild(ratingSpan);
    }

    if (priceText) {
      var priceSpan = document.createElement('span');
      priceSpan.className = 'sticky-cta__price';
      priceSpan.textContent = priceText;
      info.appendChild(priceSpan);
    }

    inner.appendChild(info);

    var actions = document.createElement('div');
    actions.className = 'sticky-cta__actions';

    var ctaBtn = document.createElement('a');
    ctaBtn.className = 'sticky-cta__btn';
    ctaBtn.href = affiliateUrl;
    ctaBtn.target = '_blank';
    ctaBtn.rel = 'noopener noreferrer';
    ctaBtn.textContent = ctaText;
    actions.appendChild(ctaBtn);

    var closeBtn = document.createElement('button');
    closeBtn.className = 'sticky-cta__close';
    closeBtn.setAttribute('aria-label', 'Dismiss');
    closeBtn.type = 'button';
    var closeSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    closeSvg.setAttribute('viewBox', '0 0 14 14');
    closeSvg.setAttribute('aria-hidden', 'true');
    var closePath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    closePath.setAttribute('d', 'M1 1l12 12M13 1L1 13');
    closePath.setAttribute('stroke', 'currentColor');
    closePath.setAttribute('stroke-width', '1.5');
    closePath.setAttribute('stroke-linecap', 'round');
    closePath.setAttribute('fill', 'none');
    closeSvg.appendChild(closePath);
    closeBtn.appendChild(closeSvg);
    actions.appendChild(closeBtn);

    inner.appendChild(actions);
    bar.appendChild(inner);
    document.body.appendChild(bar);

    // Dismiss handler
    closeBtn.addEventListener('click', function () {
      bar.classList.remove('visible');
      sessionStorage.setItem(STORAGE_KEY, '1');
    });

    // Scroll visibility logic
    var ticking = false;
    var isVisible = false;

    function update() {
      var heroBottom = heroEl.getBoundingClientRect().bottom;
      var verdictTop = verdictEl.getBoundingClientRect().top;
      var shouldShow = heroBottom < 0 && verdictTop >= window.innerHeight;

      if (shouldShow !== isVisible) {
        isVisible = shouldShow;
        bar.classList.toggle('visible', shouldShow);
      }
      ticking = false;
    }

    window.addEventListener('scroll', function () {
      if (!ticking) {
        requestAnimationFrame(update);
        ticking = true;
      }
    }, { passive: true });

    update();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
