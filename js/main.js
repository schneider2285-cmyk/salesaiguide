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

    // ─── Navbar Scroll State ──────────────────────────────────────────────
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            navbar.classList.toggle('scrolled', window.scrollY > 50);
        }, { passive: true });
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

    // ─── Newsletter Form Handling ─────────────────────────────────────────
    const newsletterForms = document.querySelectorAll('#newsletter-form');
    newsletterForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;
            console.log('Newsletter signup:', email);
            if (typeof gtag !== 'undefined') {
                gtag('event', 'newsletter_signup', { 'email': email });
            }
            alert('Thanks for subscribing! Check your email to confirm.');
            this.reset();
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

});

// Mobile menu toggle
function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    navMenu.classList.toggle('active');
}
