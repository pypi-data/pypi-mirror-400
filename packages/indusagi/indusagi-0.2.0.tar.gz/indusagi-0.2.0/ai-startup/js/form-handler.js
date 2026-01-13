// Form Handler Module

function initFormHandler() {
    const form = document.getElementById('contact-form');
    
    if (!form) return;

    form.addEventListener('submit', handleFormSubmit);
    
    // Real-time validation
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('input', () => {
            if (input.classList.contains('form-input--error')) {
                validateField(input);
            }
        });
    });
}

function handleFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Validate all fields
    let isValid = true;
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    if (!isValid) {
        showFormMessage(form, 'Please fix the errors and try again.', 'error');
        return;
    }
    
    // Show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.innerHTML;
    submitButton.innerHTML = '<span class="spinner"></span> Sending...';
    submitButton.disabled = true;
    
    // Simulate form submission (replace with actual API call)
    setTimeout(() => {
        console.log('Form submitted:', data);
        
        // Show success message
        showFormMessage(form, 'Message sent successfully! We\'ll get back to you within 24 hours.', 'success');
        
        // Reset form
        form.reset();
        
        // Reset button
        submitButton.innerHTML = originalButtonText;
        submitButton.disabled = false;
        
        // Remove message after 5 seconds
        setTimeout(() => {
            removeFormMessage(form);
        }, 5000);
    }, 1500);
}

function validateField(input) {
    const value = input.value.trim();
    const fieldName = input.name || input.id;
    let isValid = true;
    let errorMessage = '';
    
    // Remove previous error state
    input.classList.remove('form-input--error');
    removeFieldError(input);
    
    // Required validation
    if (input.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = `${capitalize(fieldName)} is required`;
    }
    
    // Email validation
    if (isValid && input.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }
    }
    
    // Select validation
    if (isValid && input.tagName === 'SELECT' && input.hasAttribute('required')) {
        if (input.value === '') {
            isValid = false;
            errorMessage = 'Please select an option';
        }
    }
    
    // Min length validation for message
    if (isValid && fieldName === 'message' && value.length < 10) {
        isValid = false;
        errorMessage = 'Message must be at least 10 characters long';
    }
    
    // Show error if invalid
    if (!isValid) {
        input.classList.add('form-input--error');
        showFieldError(input, errorMessage);
        input.classList.add('error-shake');
        setTimeout(() => input.classList.remove('error-shake'), 500);
    }
    
    return isValid;
}

function showFieldError(input, message) {
    const errorElement = document.createElement('span');
    errorElement.className = 'form-error';
    errorElement.textContent = message;
    errorElement.style.cssText = `
        color: var(--color-error);
        font-size: var(--font-size-sm);
        margin-top: var(--space-xs);
        display: block;
    `;
    
    input.parentNode.appendChild(errorElement);
}

function removeFieldError(input) {
    const errorElement = input.parentNode.querySelector('.form-error');
    if (errorElement) {
        errorElement.remove();
    }
}

function showFormMessage(form, message, type) {
    removeFormMessage(form);
    
    const messageElement = document.createElement('div');
    messageElement.className = `form-message form-message--${type}`;
    messageElement.textContent = message;
    messageElement.style.cssText = `
        padding: var(--space-md);
        margin-top: var(--space-md);
        border-radius: var(--border-radius-md);
        font-size: var(--font-size-sm);
        animation: fadeIn 0.3s ease-out;
    `;
    
    if (type === 'success') {
        messageElement.style.backgroundColor = 'rgba(16, 185, 129, 0.1)';
        messageElement.style.color = 'var(--color-success)';
        messageElement.style.border = '1px solid var(--color-success)';
    } else {
        messageElement.style.backgroundColor = 'rgba(239, 68, 68, 0.1)';
        messageElement.style.color = 'var(--color-error)';
        messageElement.style.border = '1px solid var(--color-error)';
    }
    
    form.appendChild(messageElement);
}

function removeFormMessage(form) {
    const existingMessage = form.querySelector('.form-message');
    if (existingMessage) {
        existingMessage.remove();
    }
}

function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).replace(/_/g, ' ');
}