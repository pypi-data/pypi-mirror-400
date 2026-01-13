// Navigation JavaScript
// Handles mobile menu toggle and navigation interactions

document.addEventListener('DOMContentLoaded', function() {
    initMobileMenu();
    initDropdowns();
});

// Mobile menu toggle
function initMobileMenu() {
    const toggle = document.querySelector('.nav__toggle');
    const menu = document.querySelector('.nav__menu');
    
    if (!toggle || !menu) return;
    
    toggle.addEventListener('click', function() {
        const isExpanded = this.getAttribute('aria-expanded') === 'true';
        
        // Toggle aria-expanded
        this.setAttribute('aria-expanded', !isExpanded);
        
        // Toggle menu class
        menu.classList.toggle('nav__menu--open');
        
        // Prevent body scroll when menu is open
        document.body.style.overflow = !isExpanded ? 'hidden' : '';
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        const isClickInsideMenu = menu.contains(e.target);
        const isClickOnToggle = toggle.contains(e.target);
        
        if (!isClickInsideMenu && !isClickOnToggle && menu.classList.contains('nav__menu--open')) {
            toggle.setAttribute('aria-expanded', 'false');
            menu.classList.remove('nav__menu--open');
            document.body.style.overflow = '';
        }
    });
    
    // Close menu when clicking on a link
    const menuLinks = menu.querySelectorAll('.nav__link');
    menuLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth < 769) {
                toggle.setAttribute('aria-expanded', 'false');
                menu.classList.remove('nav__menu--open');
                document.body.style.overflow = '';
            }
        });
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 769 && menu.classList.contains('nav__menu--open')) {
            toggle.setAttribute('aria-expanded', 'false');
            menu.classList.remove('nav__menu--open');
            document.body.style.overflow = '';
        }
    });
}

// Dropdown menus (if needed in future)
function initDropdowns() {
    const dropdowns = document.querySelectorAll('.nav__dropdown');
    
    dropdowns.forEach(dropdown => {
        const trigger = dropdown.querySelector('.nav__dropdown-trigger');
        const menu = dropdown.querySelector('.nav__dropdown-menu');
        
        if (!trigger || !menu) return;
        
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            // Close all other dropdowns
            dropdowns.forEach(d => {
                if (d !== dropdown) {
                    d.querySelector('.nav__dropdown-trigger').setAttribute('aria-expanded', 'false');
                    d.querySelector('.nav__dropdown-menu').classList.remove('nav__dropdown-menu--open');
                }
            });
            
            // Toggle current dropdown
            this.setAttribute('aria-expanded', !isExpanded);
            menu.classList.toggle('nav__dropdown-menu--open');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!dropdown.contains(e.target)) {
                trigger.setAttribute('aria-expanded', 'false');
                menu.classList.remove('nav__dropdown-menu--open');
            }
        });
    });
}

// Keyboard navigation for mobile menu
document.addEventListener('keydown', function(e) {
    const toggle = document.querySelector('.nav__toggle');
    const menu = document.querySelector('.nav__menu');
    
    if (!toggle || !menu) return;
    
    // Close menu on Escape key
    if (e.key === 'Escape' && menu.classList.contains('nav__menu--open')) {
        toggle.setAttribute('aria-expanded', 'false');
        menu.classList.remove('nav__menu--open');
        document.body.style.overflow = '';
        toggle.focus();
    }
});

// Add focus trap for mobile menu (accessibility)
function trapFocus(element) {
    const focusableElements = element.querySelectorAll(
        'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    
    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];
    
    element.addEventListener('keydown', function(e) {
        const isTabPressed = e.key === 'Tab' || e.keyCode === 9;
        
        if (!isTabPressed) return;
        
        if (e.shiftKey) {
            if (document.activeElement === firstFocusable) {
                lastFocusable.focus();
                e.preventDefault();
            }
        } else {
            if (document.activeElement === lastFocusable) {
                firstFocusable.focus();
                e.preventDefault();
            }
        }
    });
}

// Apply focus trap to mobile menu
const mobileMenu = document.querySelector('.nav__menu');
if (mobileMenu) {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.attributeName === 'class') {
                if (mobileMenu.classList.contains('nav__menu--open')) {
                    trapFocus(mobileMenu);
                }
            }
        });
    });
    
    observer.observe(mobileMenu, { attributes: true });
}
