// Main JavaScript - Entry Point

document.addEventListener('DOMContentLoaded', () => {
    // Set current year in footer
    const yearElements = document.querySelectorAll('#year');
    yearElements.forEach(element => {
        element.textContent = new Date().getFullYear();
    });

    // Initialize all modules
    initNavigation();
    initScrollAnimations();
    initPricingToggle();
    initDocsSearch();
    initFormHandler();
});

// Global error handling
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});