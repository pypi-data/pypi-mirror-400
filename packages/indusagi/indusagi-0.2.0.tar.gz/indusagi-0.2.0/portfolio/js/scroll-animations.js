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

    // Add scroll-animate class to elements
    addScrollAnimations();

    // Skill progress bar animation
    animateSkillBars();
}

function addScrollAnimations() {
    // Add animation classes to various elements
    const selectors = [
        '.about__content',
        '.skill-category',
        '.project-card',
        '.contact__info',
        '.contact__form'
    ];

    selectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach((element, index) => {
            element.classList.add('scroll-animate');
            element.classList.add(`scroll-animate--delay-${(index % 6) + 1}`);
        });
    });
}

function animateSkillBars() {
    const skillBars = document.querySelectorAll('.skill-item__progress');
    
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.5
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const width = entry.target.style.width;
                entry.target.style.width = '0';
                
                setTimeout(() => {
                    entry.target.style.width = width;
                }, 100);
                
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    skillBars.forEach(bar => {
        observer.observe(bar);
    });
}

// Parallax effect for hero section
function initParallax() {
    const hero = document.querySelector('.hero');
    
    if (!hero) return;

    window.addEventListener('scroll', () => {
        const scrolled = window.scrollY;
        const parallaxSpeed = 0.5;
        
        if (scrolled < hero.offsetHeight) {
            hero.style.transform = `translateY(${scrolled * parallaxSpeed}px)`;
        }
    });
}

// Initialize parallax on larger screens only
if (window.innerWidth > 768) {
    initParallax();
}