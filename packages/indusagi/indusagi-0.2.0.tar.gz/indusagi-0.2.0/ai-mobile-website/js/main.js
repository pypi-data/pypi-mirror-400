// Main JavaScript File
// Initialize all functionality when DOM is ready

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modules
    initSmoothScroll();
    initScrollAnimations();
    initNewsletterForms();
    
    console.log('NeuralMobile AI website initialized');
});

// Smooth scroll for anchor links
function initSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Skip if it's just "#"
            if (href === '#') return;
            
            const target = document.querySelector(href);
            
            if (target) {
                e.preventDefault();
                
                // Calculate header height
                const header = document.querySelector('.header');
                const headerHeight = header ? header.offsetHeight : 0;
                
                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
                
                // Update focus for accessibility
                target.focus({ preventScroll: true });
            }
        });
    });
}

// Scroll animations
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements
    const animatedElements = document.querySelectorAll(
        '.feature-card, .product-card, .testimonial-card, .team-card, .value-card, .award-card'
    );
    
    animatedElements.forEach(el => observer.observe(el));
}

// Newsletter forms
function initNewsletterForms() {
    const forms = document.querySelectorAll('.footer__newsletter-form, .newsletter-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const emailInput = this.querySelector('input[type="email"]');
            const email = emailInput.value;
            
            if (email && isValidEmail(email)) {
                // Show success message
                alert('Thank you for subscribing! You will receive our latest updates at ' + email);
                emailInput.value = '';
            } else {
                alert('Please enter a valid email address.');
            }
        });
    });
}

// Email validation helper
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Utility: Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Utility: Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Header scroll effect
let lastScroll = 0;
const header = document.querySelector('.header');

window.addEventListener('scroll', throttle(() => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 100) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
    
    lastScroll = currentScroll;
}, 100));

// Active navigation link highlighting
function updateActiveNavLink() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav__link');
    
    let currentSection = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        const headerHeight = header ? header.offsetHeight : 0;
        
        if (window.pageYOffset >= sectionTop - headerHeight - 100) {
            currentSection = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('nav__link--active');
        
        const href = link.getAttribute('href');
        if (href === `#${currentSection}` || 
            (currentSection === '' && href === 'index.html')) {
            link.classList.add('nav__link--active');
        }
    });
}

window.addEventListener('scroll', throttle(updateActiveNavLink, 100));

// Export functions for use in other files
window.NeuralMobile = {
    debounce,
    throttle,
    isValidEmail
};
