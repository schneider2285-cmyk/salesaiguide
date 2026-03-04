/**
 * Sticky navbar scroll detection + mobile hamburger toggle
 */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var navbar = document.querySelector('.navbar');
    var hamburger = document.querySelector('.navbar__hamburger');
    var mobileNav = document.querySelector('.mobile-nav');
    var overlay = document.querySelector('.mobile-nav__overlay');

    // --- Scroll detection: add .scrolled class ---
    if (navbar) {
      var scrollThreshold = 10;
      var ticking = false;

      function onScroll() {
        if (!ticking) {
          window.requestAnimationFrame(function () {
            if (window.scrollY > scrollThreshold) {
              navbar.classList.add('scrolled');
            } else {
              navbar.classList.remove('scrolled');
            }
            ticking = false;
          });
          ticking = true;
        }
      }

      window.addEventListener('scroll', onScroll, { passive: true });
      onScroll(); // check initial state
    }

    // --- Mobile hamburger toggle ---
    function openMobile() {
      if (hamburger) hamburger.classList.add('open');
      if (mobileNav) mobileNav.classList.add('open');
      if (overlay) overlay.classList.add('open');
      document.body.style.overflow = 'hidden';
      if (hamburger) {
        hamburger.setAttribute('aria-expanded', 'true');
        hamburger.setAttribute('aria-label', 'Close menu');
      }
    }

    function closeMobile() {
      if (hamburger) hamburger.classList.remove('open');
      if (mobileNav) mobileNav.classList.remove('open');
      if (overlay) overlay.classList.remove('open');
      document.body.style.overflow = '';
      if (hamburger) {
        hamburger.setAttribute('aria-expanded', 'false');
        hamburger.setAttribute('aria-label', 'Open menu');
      }
    }

    if (hamburger) {
      hamburger.addEventListener('click', function () {
        var isOpen = hamburger.classList.contains('open');
        if (isOpen) {
          closeMobile();
        } else {
          openMobile();
        }
      });
    }

    if (overlay) {
      overlay.addEventListener('click', closeMobile);
    }

    // Close on Escape
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && mobileNav && mobileNav.classList.contains('open')) {
        closeMobile();
      }
    });

    // Close on nav link click
    if (mobileNav) {
      mobileNav.querySelectorAll('.mobile-nav__link').forEach(function (link) {
        link.addEventListener('click', closeMobile);
      });
    }

    // Close on resize to desktop
    window.addEventListener('resize', function () {
      if (window.innerWidth > 768 && mobileNav && mobileNav.classList.contains('open')) {
        closeMobile();
      }
    });
  });
})();
