document.addEventListener('DOMContentLoaded', function() {
  // Mobile TOC toggle
  var mobileToc = document.querySelector('.mobile-toc');
  if (mobileToc) {
    var toggle = mobileToc.querySelector('.mobile-toc__toggle');
    toggle.addEventListener('click', function() {
      var isOpen = mobileToc.classList.toggle('mobile-toc--open');
      toggle.setAttribute('aria-expanded', isOpen);
    });
    // Close mobile TOC when a link is clicked
    var mobileLinks = mobileToc.querySelectorAll('.mobile-toc__list a');
    mobileLinks.forEach(function(link) {
      link.addEventListener('click', function() {
        mobileToc.classList.remove('mobile-toc--open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // Scroll-spy for both desktop and mobile TOC
  var sections = document.querySelectorAll('#overview, #features, #pricing, #pros-cons, #who-its-for, #verdict');
  var desktopLinks = document.querySelectorAll('.review-toc a');
  var mobileLinksAll = document.querySelectorAll('.mobile-toc__list a');

  if (sections.length === 0) return;

  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        var id = entry.target.id;
        desktopLinks.forEach(function(link) {
          link.classList.toggle('active', link.getAttribute('href') === '#' + id);
        });
        mobileLinksAll.forEach(function(link) {
          link.classList.toggle('active', link.getAttribute('href') === '#' + id);
        });
      }
    });
  }, {
    rootMargin: '-20% 0px -75% 0px',
    threshold: 0
  });

  sections.forEach(function(section) { observer.observe(section); });
});
