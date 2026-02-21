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
    
    // Newsletter form handling
    const newsletterForms = document.querySelectorAll('#newsletter-form');
    newsletterForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;
            
            // Log newsletter signup
            console.log('Newsletter signup:', email);
            
            // Google Analytics event
            if (typeof gtag !== 'undefined') {
                gtag('event', 'newsletter_signup', {
                    'email': email
                });
            }
            
            // Show success message (customize based on your email provider)
            alert('Thanks for subscribing! Check your email to confirm.');
            this.reset();
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
