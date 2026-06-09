// Sales AI Guide - Main JavaScript

// Affiliate Link Tracking
document.addEventListener('DOMContentLoaded', function() {
    
    // Track affiliate link clicks
    const affiliateLinks = document.querySelectorAll('a[href*="/go/"]');
    affiliateLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const toolName = this.href.split('/go/')[1];
            
            // Log click event
            console.log('Affiliate click:', toolName);
            
            // Google Analytics event (if GA is loaded)
            if (typeof gtag !== 'undefined') {
                gtag('event', 'affiliate_click', {
                    'tool_name': toolName,
                    'link_location': window.location.pathname
                });
            }
            
            // Allow default link behavior
            return true;
        });
    });

    // Derive a non-PII "zone" label for an outbound link (a CTA class if present,
    // else the nearest data-audit zone, else a container hint).
    function outboundZone(a) {
        const cls = (a.className || '').toString();
        const ctaClass = cls.split(/\s+/).find(function (c) { return /btn|cta/i.test(c); });
        if (ctaClass) return ctaClass;
        const zoneEl = a.closest && a.closest('[data-audit]');
        if (zoneEl) return zoneEl.getAttribute('data-audit') || 'other';
        const box = a.closest && a.closest('footer, nav, header, section, aside');
        if (box && box.className) return box.className.toString().split(/\s+/)[0] || 'other';
        return 'other';
    }

    // Track outbound clicks to external vendor sites. These are the direct vendor
    // CTAs the indexation gate requires in review bodies (no /go/), which otherwise
    // fire no analytics. /go/ links are same-origin and keep firing affiliate_click
    // above, so there is no double count. No PII is sent.
    document.addEventListener('click', function (e) {
        const a = e.target.closest ? e.target.closest('a[href]') : null;
        if (!a) return;
        const external = (a.protocol === 'http:' || a.protocol === 'https:') &&
            a.hostname && a.hostname !== window.location.hostname;
        if (!external || typeof gtag === 'undefined') return;
        gtag('event', 'outbound_click', {
            'dest_domain': a.hostname,
            'dest_url': a.href,
            'page_path': window.location.pathname,
            'cta_zone': outboundZone(a)
        });
    });
    
    // Newsletter form handling
    const newsletterForms = document.querySelectorAll('#newsletter-form');
    newsletterForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;
            if (!email) return; // nothing to submit; do not fire a signup event

            // Log a non-PII marker only. Never log the email value (PII).
            console.log('Newsletter signup submitted');

            // Google Analytics event, non-PII only. GA4 must never receive an
            // email or other PII (Google policy and privacy law). Send context instead.
            if (typeof gtag !== 'undefined') {
                gtag('event', 'newsletter_signup', {
                    'method': 'newsletter_form',
                    'page_path': window.location.pathname
                });
            }
            
            // Show success message (customize based on your email provider)
            alert('Thanks for subscribing! Check your email to confirm.');
            this.reset();
        });
    });

    // ButtonDown newsletter forms (embedded on guide pages, post cross-domain to
    // ButtonDown). Fire a non-PII signup event WITHOUT preventing the native submit.
    // "method" distinguishes these from the Beehiiv form above. No email is sent to GA.
    document.querySelectorAll('form[action*="buttondown.com"]').forEach(function (form) {
        form.addEventListener('submit', function () {
            if (typeof gtag !== 'undefined') {
                gtag('event', 'newsletter_signup', {
                    'method': 'buttondown',
                    'page_path': window.location.pathname
                });
            }
        });
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Track scroll depth
    let scrollDepth = 0;
    window.addEventListener('scroll', function() {
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const currentDepth = Math.round((scrollTop + windowHeight) / documentHeight * 100);
        
        // Track milestones: 25%, 50%, 75%, 90%
        if (currentDepth >= 90 && scrollDepth < 90) {
            scrollDepth = 90;
            console.log('Scroll depth: 90%');
            if (typeof gtag !== 'undefined') {
                gtag('event', 'scroll_depth', { 'depth': 90 });
            }
        } else if (currentDepth >= 75 && scrollDepth < 75) {
            scrollDepth = 75;
            console.log('Scroll depth: 75%');
            if (typeof gtag !== 'undefined') {
                gtag('event', 'scroll_depth', { 'depth': 75 });
            }
        } else if (currentDepth >= 50 && scrollDepth < 50) {
            scrollDepth = 50;
            console.log('Scroll depth: 50%');
            if (typeof gtag !== 'undefined') {
                gtag('event', 'scroll_depth', { 'depth': 50 });
            }
        } else if (currentDepth >= 25 && scrollDepth < 25) {
            scrollDepth = 25;
            console.log('Scroll depth: 25%');
            if (typeof gtag !== 'undefined') {
                gtag('event', 'scroll_depth', { 'depth': 25 });
            }
        }
    });
    
    // Track time on page
    const startTime = Date.now();
    window.addEventListener('beforeunload', function() {
        const timeSpent = Math.round((Date.now() - startTime) / 1000); // seconds
        console.log('Time on page:', timeSpent, 'seconds');
        if (typeof gtag !== 'undefined') {
            gtag('event', 'time_on_page', {
                'seconds': timeSpent,
                'page': window.location.pathname
            });
        }
    });
    
});

// Mobile menu toggle (if needed in future)
function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    navMenu.classList.toggle('active');
}
