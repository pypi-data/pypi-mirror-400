// Form Validation JavaScript
// Handles contact form validation and submission

document.addEventListener('DOMContentLoaded', function() {
    initContactForm();
    initCategoryFilter();
    initFAQAccordion();
});

// Contact form validation
function initContactForm() {
    const form = document.getElementById('contactForm');
    
    if (!form) return;
    
    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const phoneInput = document.getElementById('phone');
    const subjectInput = document.getElementById('subject');
    const messageInput = document.getElementById('message');
    
    // Real-time validation
    nameInput.addEventListener('blur', () => validateName(nameInput));
    emailInput.addEventListener('blur', () => validateEmail(emailInput));
    phoneInput.addEventListener('blur', () => validatePhone(phoneInput));
    subjectInput.addEventListener('blur', () => validateSubject(subjectInput));
    messageInput.addEventListener('blur', () => validateMessage(messageInput));
    
    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate all fields
        const isNameValid = validateName(nameInput);
        const isEmailValid = validateEmail(emailInput);
        const isPhoneValid = validatePhone(phoneInput);
        const isSubjectValid = validateSubject(subjectInput);
        const isMessageValid = validateMessage(messageInput);
        
        if (isNameValid && isEmailValid && isPhoneValid && isSubjectValid && isMessageValid) {
            submitForm(form);
        }
    });
}

// Validate name
function validateName(input) {
    const errorElement = document.getElementById('nameError');
    const value = input.value.trim();
    
    if (value === '') {
        showError(input, errorElement, 'Name is required');
        return false;
    } else if (value.length < 2) {
        showError(input, errorElement, 'Name must be at least 2 characters');
        return false;
    } else {
        showSuccess(input, errorElement);
        return true;
    }
}

// Validate email
function validateEmail(input) {
    const errorElement = document.getElementById('emailError');
    const value = input.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (value === '') {
        showError(input, errorElement, 'Email is required');
        return false;
    } else if (!emailRegex.test(value)) {
        showError(input, errorElement, 'Please enter a valid email address');
        return false;
    } else {
        showSuccess(input, errorElement);
        return true;
    }
}

// Validate phone (optional)
function validatePhone(input) {
    const errorElement = document.getElementById('phoneError');
    const value = input.value.trim();
    
    if (value === '') {
        showSuccess(input, errorElement);
        return true;
    }
    
    const phoneRegex = /^[\d\s\-+()]+$/;
    if (!phoneRegex.test(value)) {
        showError(input, errorElement, 'Please enter a valid phone number');
        return false;
    } else {
        showSuccess(input, errorElement);
        return true;
    }
}

// Validate subject
function validateSubject(input) {
    const errorElement = document.getElementById('subjectError');
    const value = input.value;
    
    if (value === '') {
        showError(input, errorElement, 'Please select a subject');
        return false;
    } else {
        showSuccess(input, errorElement);
        return true;
    }
}

// Validate message
function validateMessage(input) {
    const errorElement = document.getElementById('messageError');
    const value = input.value.trim();
    
    if (value === '') {
        showError(input, errorElement, 'Message is required');
        return false;
    } else if (value.length < 10) {
        showError(input, errorElement, 'Message must be at least 10 characters');
        return false;
    } else {
        showSuccess(input, errorElement);
        return true;
    }
}

// Show error
function showError(input, errorElement, message) {
    input.style.borderColor = 'var(--error)';
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
}

// Show success
function showSuccess(input, errorElement) {
    input.style.borderColor = 'var(--success)';
    if (errorElement) {
        errorElement.textContent = '';
        errorElement.style.display = 'none';
    }
}

// Submit form
function submitForm(form) {
    const submitBtn = form.querySelector('.contact-form__submit');
    const submitText = submitBtn.querySelector('.contact-form__submit-text');
    const submitLoading = submitBtn.querySelector('.contact-form__submit-loading');
    
    // Show loading state
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;
    
    // Simulate API call
    setTimeout(() => {
        // Hide form
        form.style.display = 'none';
        
        // Show success message
        const successMessage = document.getElementById('formSuccess');
        if (successMessage) {
            successMessage.style.display = 'block';
            successMessage.classList.add('fade-in');
        }
        
        // Reset form
        form.reset();
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
        
        // Reset input styles
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.style.borderColor = '';
        });
    }, 2000);
}

// Category filter for products page
function initCategoryFilter() {
    const filterButtons = document.querySelectorAll('.category-filter__button');
    const productCards = document.querySelectorAll('.product-card--full');
    
    if (filterButtons.length === 0) return;
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('category-filter__button--active'));
            this.classList.add('category-filter__button--active');
            
            // Filter products
            productCards.forEach(card => {
                const cardCategory = card.getAttribute('data-category');
                
                if (category === 'all' || cardCategory === category) {
                    card.style.display = '';
                    card.style.animation = 'fadeIn 0.5s ease';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

// FAQ accordion
function initFAQAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    if (faqItems.length === 0) return;
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-item__question');
        const answer = item.querySelector('.faq-item__answer');
        
        question.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            // Close all other items
            faqItems.forEach(otherItem => {
                const otherQuestion = otherItem.querySelector('.faq-item__question');
                const otherAnswer = otherItem.querySelector('.faq-item__answer');
                
                otherQuestion.setAttribute('aria-expanded', 'false');
                otherAnswer.setAttribute('aria-hidden', 'true');
            });
            
            // Toggle current item
            this.setAttribute('aria-expanded', !isExpanded);
            answer.setAttribute('aria-hidden', isExpanded);
        });
    });
}

// Newsletter form validation
function initNewsletterForms() {
    const newsletterForms = document.querySelectorAll('.footer__newsletter-form, .newsletter-form');
    
    newsletterForms.forEach(form => {
        const input = form.querySelector('input[type="email"]');
        
        if (!input) return;
        
        input.addEventListener('blur', function() {
            const value = this.value.trim();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (value !== '' && !emailRegex.test(value)) {
                this.style.borderColor = 'var(--error)';
            } else {
                this.style.borderColor = '';
            }
        });
        
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const value = input.value.trim();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (value === '') {
                alert('Please enter your email address.');
                input.focus();
            } else if (!emailRegex.test(value)) {
                alert('Please enter a valid email address.');
                input.focus();
            } else {
                // Success
                alert('Thank you for subscribing!');
                input.value = '';
            }
        });
    });
}

// Utility: Get form data as object
function getFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    return data;
}

// Utility: Clear form errors
function clearFormErrors(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    const errors = form.querySelectorAll('.form-error');
    
    inputs.forEach(input => {
        input.style.borderColor = '';
    });
    
    errors.forEach(error => {
        error.textContent = '';
        error.style.display = 'none';
    });
}

// Export functions
window.FormValidation = {
    validateName,
    validateEmail,
    validatePhone,
    validateSubject,
    validateMessage,
    getFormData,
    clearFormErrors
};
