// Scroll Animations Module

function initScrollAnimations() {
    // Elements to animate on scroll
    const animatedElements = document.querySelectorAll('.scroll-animate');
    
    // Create Intersection Observer
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('scroll-animate--visible');
                // Optional: stop observing once animated
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all animated elements
    animatedElements.forEach(element => {
        observer.observe(element);
    });

    // Animate stats counters
    animateCounters();
}

function animateCounters() {
    const counters = document.querySelectorAll('.stat__number[data-target]');
    
    if (counters.length === 0) return;

    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.5
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseFloat(counter.getAttribute('data-target'));
                const duration = 2000;
                const startTime = performance.now();
                
                const updateCounter = (currentTime) => {
                    const elapsed = currentTime - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    
                    // Easing function
                    const easeOutQuart = 1 - Math.pow(1 - progress, 4);
                    const current = target * easeOutQuart;
                    
                    if (target >= 1000) {
                        counter.textContent = Math.floor(current).toLocaleString();
                    } else if (target < 10) {
                        counter.textContent = current.toFixed(2);
                    } else {
                        counter.textContent = Math.floor(current);
                    }
                    
                    if (progress < 1) {
                        requestAnimationFrame(updateCounter);
                    } else {
                        // Ensure final value is exact
                        if (target >= 1000) {
                            counter.textContent = target.toLocaleString();
                        } else if (target < 10) {
                            counter.textContent = target.toFixed(2);
                        } else {
                            counter.textContent = target;
                        }
                    }
                };
                
                requestAnimationFrame(updateCounter);
                observer.unobserve(counter);
            }
        });
    }, observerOptions);

    counters.forEach(counter => {
        observer.observe(counter);
    });
}

// Parallax effect for hero sections
function initParallax() {
    const heroes = document.querySelectorAll('.hero');
    
    if (heroes.length === 0) return;

    window.addEventListener('scroll', () => {
        const scrolled = window.scrollY;
        
        heroes.forEach(hero => {
            if (scrolled < hero.offsetHeight) {
                const parallaxSpeed = 0.3;
                hero.style.transform = `translateY(${scrolled * parallaxSpeed}px)`;
            }
        });
    });
}

// Initialize parallax on larger screens only
if (window.innerWidth > 768) {
    initParallax();
}