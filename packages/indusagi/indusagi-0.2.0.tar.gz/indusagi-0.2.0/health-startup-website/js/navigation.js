document.addEventListener('DOMContentLoaded', () => {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    const navLinks = document.querySelectorAll('.nav__link');
    const header = document.getElementById('header');
    const navIcon = navToggle?.querySelector('i');

    let isMenuOpen = false;

    function toggleMenu() {
        isMenuOpen = !isMenuOpen;
        
        if (navMenu) {
            navMenu.classList.toggle('active', isMenuOpen);
        }
        
        if (navIcon) {
            navIcon.classList.toggle('fa-bars', !isMenuOpen);
            navIcon.classList.toggle('fa-times', isMenuOpen);
        }
        
        document.body.style.overflow = isMenuOpen ? 'hidden' : '';
    }

    function closeMenu() {
        isMenuOpen = false;
        
        if (navMenu) {
            navMenu.classList.remove('active');
        }
        
        if (navIcon) {
            navIcon.classList.add('fa-bars');
            navIcon.classList.remove('fa-times');
        }
        
        document.body.style.overflow = '';
    }

    if (navToggle) {
        navToggle.addEventListener('click', toggleMenu);
    }

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            
            if (href && href.startsWith('#')) {
                e.preventDefault();
                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    closeMenu();
                    
                    const headerHeight = header?.offsetHeight || 0;
                    const targetPosition = targetElement.offsetTop - headerHeight;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            } else {
                closeMenu();
            }
        });
    });

    let lastScroll = 0;
    let scrollTimeout;

    function handleScroll() {
        const currentScroll = window.pageYOffset;
        
        if (header) {
            if (currentScroll > 50) {
                header.classList.add('header--scrolled');
            } else {
                header.classList.remove('header--scrolled');
            }
        }

        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            lastScroll = currentScroll;
        }, 100);
    }

    window.addEventListener('scroll', () => {
        window.requestAnimationFrame(handleScroll);
    }, { passive: true });

    handleScroll();

    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        
        if (href === currentPage || 
            (currentPage === '' && href === 'index.html') ||
            (href === 'index.html' && currentPage === '')) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isMenuOpen) {
            closeMenu();
        }
    });

    const navCta = document.querySelector('.nav__cta');
    
    if (navCta) {
        navCta.addEventListener('click', () => {
            closeMenu();
        });
    }

    if (navMenu) {
        navMenu.addEventListener('click', (e) => {
            if (e.target === navMenu) {
                closeMenu();
            }
        });
    }
});