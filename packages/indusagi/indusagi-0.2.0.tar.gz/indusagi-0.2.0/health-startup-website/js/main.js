document.addEventListener('DOMContentLoaded', () => {
    
    function animateCounter(element, target, duration = 2000) {
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            
            if (current >= target) {
                element.textContent = target.toLocaleString();
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current).toLocaleString();
            }
        }, 16);
    }

    function initStatsCounter() {
        const statsSection = document.querySelector('.stats');
        const statNumbers = document.querySelectorAll('.stat-item__number');
        
        if (!statsSection || statNumbers.length === 0) return;
        
        let animated = false;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !animated) {
                    animated = true;
                    
                    statNumbers.forEach(stat => {
                        const target = parseInt(stat.getAttribute('data-target'));
                        if (target) {
                            animateCounter(stat, target);
                        }
                    });
                }
            });
        }, { threshold: 0.5 });
        
        observer.observe(statsSection);
    }

    function initTestimonialCarousel() {
        const testimonials = document.querySelectorAll('.testimonial-card');
        const prevBtn = document.getElementById('testimonial-prev');
        const nextBtn = document.getElementById('testimonial-next');
        
        if (testimonials.length === 0) return;
        
        let currentIndex = 0;
        let autoPlayInterval;
        
        function showTestimonial(index) {
            testimonials.forEach((testimonial, i) => {
                testimonial.classList.toggle('active', i === index);
            });
        }
        
        function nextTestimonial() {
            currentIndex = (currentIndex + 1) % testimonials.length;
            showTestimonial(currentIndex);
        }
        
        function prevTestimonial() {
            currentIndex = (currentIndex - 1 + testimonials.length) % testimonials.length;
            showTestimonial(currentIndex);
        }
        
        function startAutoPlay() {
            autoPlayInterval = setInterval(nextTestimonial, 5000);
        }
        
        function stopAutoPlay() {
            clearInterval(autoPlayInterval);
        }
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                stopAutoPlay();
                prevTestimonial();
                startAutoPlay();
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                stopAutoPlay();
                nextTestimonial();
                startAutoPlay();
            });
        }
        
        startAutoPlay();
    }

    function initFAQAccordion() {
        const faqQuestions = document.querySelectorAll('.faq-item__question');
        
        faqQuestions.forEach(question => {
            question.addEventListener('click', () => {
                const isExpanded = question.getAttribute('aria-expanded') === 'true';
                const parentItem = question.closest('.faq-item');
                const answer = parentItem?.querySelector('.faq-item__answer');
                
                faqQuestions.forEach(q => {
                    if (q !== question) {
                        q.setAttribute('aria-expanded', 'false');
                    }
                });
                
                question.setAttribute('aria-expanded', !isExpanded);
            });
        });
    }

    function initScrollAnimations() {
        const animatedElements = document.querySelectorAll(
            '.feature-card, .stat-item, .team-card, .service-card, .pricing-card, .value-card, .timeline__item, .partner-logo, .contact-info-card'
        );
        
        if (animatedElements.length === 0) return;
        
        const observerOptions = {
            root: null,
            rootMargin: '0px',
            threshold: 0.1
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);
        
        animatedElements.forEach(element => {
            observer.observe(element);
        });
    }

    function initNewsletterForms() {
        const newsletterForms = document.querySelectorAll('.footer__newsletter');
        
        newsletterForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                
                const emailInput = form.querySelector('input[type="email"]');
                const email = emailInput?.value;
                
                if (email) {
                    alert(`Thank you for subscribing with: ${email}`);
                    emailInput.value = '';
                }
            });
        });
    }

    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                
                if (href === '#' || href === '#main-content') return;
                
                const targetElement = document.querySelector(href);
                
                if (targetElement) {
                    e.preventDefault();
                    
                    const header = document.querySelector('.header');
                    const headerHeight = header?.offsetHeight || 0;
                    const targetPosition = targetElement.offsetTop - headerHeight;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    function initLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        if (images.length === 0) return;
        
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.getAttribute('data-src');
                    
                    if (src) {
                        img.src = src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    }

    function addHoverEffects() {
        const cards = document.querySelectorAll('.feature-card, .service-card, .team-card, .pricing-card');
        
        cards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-8px)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = '';
            });
        });
    }

    function initBackToTop() {
        const backToTopBtn = document.createElement('button');
        backToTopBtn.className = 'back-to-top';
        backToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        backToTopBtn.setAttribute('aria-label', 'Back to top');
        backToTopBtn.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            background: var(--color-primary);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: none;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
            z-index: 999;
        `;
        
        document.body.appendChild(backToTopBtn);
        
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                backToTopBtn.style.display = 'flex';
            } else {
                backToTopBtn.style.display = 'none';
            }
        });
        
        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
        
        backToTopBtn.addEventListener('mouseenter', () => {
            backToTopBtn.style.transform = 'scale(1.1)';
            backToTopBtn.style.background = 'var(--color-primary-dark)';
        });
        
        backToTopBtn.addEventListener('mouseleave', () => {
            backToTopBtn.style.transform = 'scale(1)';
            backToTopBtn.style.background = 'var(--color-primary)';
        });
    }

    function handleResize() {
        let resizeTimeout;
        
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                const navMenu = document.getElementById('nav-menu');
                const navToggle = document.getElementById('nav-toggle');
                
                if (window.innerWidth > 768 && navMenu?.classList.contains('active')) {
                    navMenu.classList.remove('active');
                    const navIcon = navToggle?.querySelector('i');
                    if (navIcon) {
                        navIcon.classList.add('fa-bars');
                        navIcon.classList.remove('fa-times');
                    }
                    document.body.style.overflow = '';
                }
            }, 250);
        });
    }

    initStatsCounter();
    initTestimonialCarousel();
    initFAQAccordion();
    initScrollAnimations();
    initNewsletterForms();
    initSmoothScroll();
    initLazyLoading();
    addHoverEffects();
    initBackToTop();
    handleResize();
});