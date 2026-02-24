// Sales AI Guide - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {

    // ─── Scroll Reveal (IntersectionObserver) ─────────────────────────────
    const revealSelector =
        '.tool-card, .compare-card, .category-card, .trust-item, ' +
        '.content-section, .sidebar-card, .feature-card, .pricing-tier';
    const revealEls = document.querySelectorAll(revealSelector);

    if ('IntersectionObserver' in window) {
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('in-view');
                    revealObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.08,
            rootMargin: '0px 0px -30px 0px'
        });

        revealEls.forEach(el => revealObserver.observe(el));
    } else {
        // Fallback: show everything immediately if no IO support
        revealEls.forEach(el => el.classList.add('in-view'));
    }

    // ─── Affiliate Link Tracking ──────────────────────────────────────────
    const affiliateLinks = document.querySelectorAll('a[href*="/go/"]');
    affiliateLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const toolName = this.href.split('/go/')[1];
            console.log('Affiliate click:', toolName);
            if (typeof gtag !== 'undefined') {
                gtag('event', 'affiliate_click', {
                    'tool_name': toolName,
                    'link_location': window.location.pathname
                });
            }
            return true;
        });
    });

    // ─── Newsletter Form Handling (Netlify Forms) ─────────────────────────
    const newsletterForms = document.querySelectorAll('.netlify-newsletter');
    newsletterForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const btn = this.querySelector('button[type="submit"]');
            const msgEl = this.querySelector('.form-message');
            const email = this.querySelector('input[type="email"]').value;

            btn.disabled = true;
            btn.textContent = 'Sending...';

            const body = new URLSearchParams(new FormData(this)).toString();

            fetch('/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: body
            })
            .then(function(res) {
                if (!res.ok) throw new Error('Network response was not ok');
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'newsletter_signup', {
                        'email': email,
                        'form_location': window.location.pathname
                    });
                }
                form.reset();
                btn.textContent = 'Subscribed!';
                if (msgEl) {
                    msgEl.textContent = 'You\'re in! We\'ll send you the best tool insights.';
                    msgEl.className = 'form-message form-success';
                }
            })
            .catch(function() {
                btn.disabled = false;
                btn.textContent = 'Subscribe';
                if (msgEl) {
                    msgEl.textContent = 'Something went wrong. Please try again.';
                    msgEl.className = 'form-message form-error';
                }
            });
        });
    });

    // ─── Smooth Scroll for Anchor Links ───────────────────────────────────
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });

    // ─── Journey Bar Active State ───────────────────────────────────────
    const journeyBar = document.getElementById('journey-bar');
    if (journeyBar) {
        const sectionIds = ['pricing-reality', 'who-should-use', 'decision-snapshot', 'where-it-breaks', 'stack-fit'];
        const journeyObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    document.querySelectorAll('.journey-tab').forEach(t => t.classList.remove('active'));
                    const tab = document.querySelector('.journey-tab[data-section="' + entry.target.id + '"]');
                    if (tab) tab.classList.add('active');
                }
            });
        }, { rootMargin: '-20% 0px -70% 0px' });
        sectionIds.forEach(function(id) {
            var el = document.getElementById(id);
            if (el) journeyObserver.observe(el);
        });
    }

    // ─── Scroll Depth Tracking ────────────────────────────────────────────
    let scrollDepth = 0;
    window.addEventListener('scroll', function() {
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const currentDepth = Math.round((scrollTop + windowHeight) / documentHeight * 100);

        const milestones = [90, 75, 50, 25];
        for (const milestone of milestones) {
            if (currentDepth >= milestone && scrollDepth < milestone) {
                scrollDepth = milestone;
                console.log('Scroll depth:', milestone + '%');
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'scroll_depth', { 'depth': milestone });
                }
                break;
            }
        }
    }, { passive: true });

    // ─── Time on Page Tracking ────────────────────────────────────────────
    const startTime = Date.now();
    window.addEventListener('beforeunload', function() {
        const timeSpent = Math.round((Date.now() - startTime) / 1000);
        console.log('Time on page:', timeSpent, 'seconds');
        if (typeof gtag !== 'undefined') {
            gtag('event', 'time_on_page', {
                'seconds': timeSpent,
                'page': window.location.pathname
            });
        }
    });

    // ─── Reader Selector (compare pages) ────────────────────────────────
    const readerBtns = document.querySelectorAll('.reader-btn');
    if (readerBtns.length) {
        readerBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                readerBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                document.body.classList.toggle('reader-rep', btn.dataset.reader === 'rep');
            });
        });
    }

});

// Mobile menu toggle
function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    navMenu.classList.toggle('active');
}
