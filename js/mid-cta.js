document.addEventListener('DOMContentLoaded', function() {
  var ctas = document.querySelectorAll('[data-animate]');
  if (!ctas.length) return;
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });
  ctas.forEach(function(cta) { observer.observe(cta); });
});
