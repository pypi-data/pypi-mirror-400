document.addEventListener('DOMContentLoaded', () => {
    const contactForm = document.getElementById('contact-form');
    
    if (!contactForm) return;
    
    const formFields = {
        name: {
            input: document.getElementById('name'),
            error: document.getElementById('name-error'),
            validate: (value) => {
                if (!value.trim()) {
                    return 'Please enter your name';
                }
                if (value.trim().length < 2) {
                    return 'Name must be at least 2 characters';
                }
                return '';
            }
        },
        email: {
            input: document.getElementById('email'),
            error: document.getElementById('email-error'),
            validate: (value) => {
                if (!value.trim()) {
                    return 'Please enter your email';
                }
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    return 'Please enter a valid email address';
                }
                return '';
            }
        },
        phone: {
            input: document.getElementById('phone'),
            error: document.getElementById('phone-error'),
            validate: (value) => {
                if (value.trim()) {
                    const phoneRegex = /^[\d\s\-\+\(\)]+$/;
                    if (!phoneRegex.test(value)) {
                        return 'Please enter a valid phone number';
                    }
                }
                return '';
            }
        },
        subject: {
            input: document.getElementById('subject'),
            error: document.getElementById('subject-error'),
            validate: (value) => {
                if (!value) {
                    return 'Please select a subject';
                }
                return '';
            }
        },
        message: {
            input: document.getElementById('message'),
            error: document.getElementById('message-error'),
            validate: (value) => {
                if (!value.trim()) {
                    return 'Please enter your message';
                }
                if (value.trim().length < 10) {
                    return 'Message must be at least 10 characters';
                }
                return '';
            }
        },
        consent: {
            input: document.querySelector('input[name="consent"]'),
            error: document.getElementById('consent-error'),
            validate: (input) => {
                if (!input.checked) {
                    return 'You must agree to the Privacy Policy';
                }
                return '';
            }
        }
    };
    
    function showError(fieldName, errorMessage) {
        const field = formFields[fieldName];
        if (!field) return;
        
        if (field.input) {
            field.input.classList.add('error');
        }
        
        if (field.error) {
            field.error.textContent = errorMessage;
        }
    }
    
    function clearError(fieldName) {
        const field = formFields[fieldName];
        if (!field) return;
        
        if (field.input) {
            field.input.classList.remove('error');
        }
        
        if (field.error) {
            field.error.textContent = '';
        }
    }
    
    function clearAllErrors() {
        Object.keys(formFields).forEach(fieldName => {
            clearError(fieldName);
        });
    }
    
    function validateField(fieldName) {
        const field = formFields[fieldName];
        if (!field) return true;
        
        const value = field.input?.value || '';
        const error = field.validate(fieldName === 'consent' ? field.input : value);
        
        if (error) {
            showError(fieldName, error);
            return false;
        } else {
            clearError(fieldName);
            return true;
        }
    }
    
    function validateForm() {
        let isValid = true;
        
        Object.keys(formFields).forEach(fieldName => {
            if (!validateField(fieldName)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    Object.keys(formFields).forEach(fieldName => {
        const field = formFields[fieldName];
        
        if (field.input && fieldName !== 'consent') {
            field.input.addEventListener('blur', () => {
                if (field.input.value.trim()) {
                    validateField(fieldName);
                }
            });
            
            field.input.addEventListener('input', () => {
                if (field.input.classList.contains('error')) {
                    clearError(fieldName);
                }
            });
        }
        
        if (fieldName === 'consent' && field.input) {
            field.input.addEventListener('change', () => {
                if (field.input.checked) {
                    clearError(fieldName);
                }
            });
        }
    });
    
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        clearAllErrors();
        
        if (!validateForm()) {
            const firstError = document.querySelector('.form-input.error, .form-select.error, .form-textarea.error');
            if (firstError) {
                firstError.focus();
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            return;
        }
        
        const submitBtn = document.getElementById('submit-btn');
        const btnText = submitBtn?.querySelector('.btn__text');
        const btnIcon = submitBtn?.querySelector('.btn__icon');
        
        if (submitBtn) {
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
        }
        
        if (btnText) {
            btnText.textContent = 'Sending...';
        }
        
        if (btnIcon) {
            btnIcon.style.display = 'none';
        }
        
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        if (submitBtn) {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
        
        contactForm.style.display = 'none';
        
        const successMessage = document.getElementById('form-success');
        if (successMessage) {
            successMessage.style.display = 'block';
            successMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        
        const formData = {
            name: formFields.name.input?.value,
            email: formFields.email.input?.value,
            phone: formFields.phone.input?.value,
            subject: formFields.subject.input?.value,
            message: formFields.message.input?.value
        };
        
        console.log('Form submitted successfully:', formData);
    });
    
    const formInputs = contactForm.querySelectorAll('input, select, textarea');
    
    formInputs.forEach(input => {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
            }
        });
    });
});