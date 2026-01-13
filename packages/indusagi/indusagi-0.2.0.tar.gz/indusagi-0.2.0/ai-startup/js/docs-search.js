// Documentation Search Module

function initDocsSearch() {
    const searchInput = document.getElementById('docs-search');
    const docsSections = document.querySelectorAll('.docs__section');
    const docsNavLinks = document.querySelectorAll('.docs__nav-link');
    
    if (!searchInput || docsSections.length === 0) return;

    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase().trim();
        
        if (searchTerm === '') {
            // Show all sections
            docsSections.forEach(section => {
                section.style.display = 'block';
            });
            return;
        }

        // Search through sections
        docsSections.forEach(section => {
            const title = section.querySelector('h2, h3')?.textContent.toLowerCase() || '';
            const content = section.textContent.toLowerCase();
            
            if (title.includes(searchTerm) || content.includes(searchTerm)) {
                section.style.display = 'block';
                
                // Highlight matching terms
                highlightSearchTerms(section, searchTerm);
            } else {
                section.style.display = 'none';
            }
        });
    });

    // Keyboard navigation
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            searchInput.value = '';
            docsSections.forEach(section => {
                section.style.display = 'block';
                removeHighlights(section);
            });
        }
    });

    // Active section highlighting in sidebar
    const observerOptions = {
        root: null,
        rootMargin: '-20% 0px -70% 0px',
        threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                
                docsNavLinks.forEach(link => {
                    link.classList.remove('docs__nav-link--active');
                    if (link.getAttribute('href') === `#${id}`) {
                        link.classList.add('docs__nav-link--active');
                    }
                });
            }
        });
    }, observerOptions);

    docsSections.forEach(section => {
        observer.observe(section);
    });
}

function highlightSearchTerms(section, term) {
    // Remove existing highlights
    removeHighlights(section);
    
    if (term === '') return;

    // Create regex for highlighting
    const regex = new RegExp(`(${escapeRegex(term)})`, 'gi');
    
    // Highlight in headings
    const headings = section.querySelectorAll('h2, h3, h4');
    headings.forEach(heading => {
        const originalHTML = heading.getAttribute('data-original-html') || heading.innerHTML;
        heading.setAttribute('data-original-html', originalHTML);
        
        if (!heading.getAttribute('data-original-html')) {
            heading.setAttribute('data-original-html', heading.innerHTML);
        }
        
        const highlighted = originalHTML.replace(regex, '<mark style="background: var(--color-accent); color: white; padding: 0 0.25rem;">$1</mark>');
        heading.innerHTML = highlighted;
    });
}

function removeHighlights(section) {
    const headings = section.querySelectorAll('h2, h3, h4');
    headings.forEach(heading => {
        const originalHTML = heading.getAttribute('data-original-html');
        if (originalHTML) {
            heading.innerHTML = originalHTML;
        }
    });
}

function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}