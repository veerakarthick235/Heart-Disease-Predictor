document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.prediction-form');
    
    if (form) {
        // Form validation and submission
        form.addEventListener('submit', function(event) {
            let isValid = true;
            
            // Get all required inputs
            const requiredInputs = form.querySelectorAll('[required]');
            
            requiredInputs.forEach(input => {
                if (!input.value) {
                    isValid = false;
                    input.style.borderColor = 'var(--danger-red)';
                } else {
                    input.style.borderColor = 'var(--medium-gray)';
                }
            });
            
            if (!isValid) {
                event.preventDefault();
                showNotification('Please fill in all required fields', 'error');
                return;
            }
            
            // Add loading state to submit button
            const submitButton = form.querySelector('.btn-primary');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.classList.add('loading');
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing Patient Data...';
            }
        });
        
        // Reset button functionality
        const resetButton = form.querySelector('.btn-secondary');
        if (resetButton) {
            resetButton.addEventListener('click', function() {
                setTimeout(() => {
                    const inputs = form.querySelectorAll('input, select');
                    inputs.forEach(input => {
                        input.style.borderColor = 'var(--medium-gray)';
                    });
                }, 100);
            });
        }
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                validateInput(this);
            });
            
            input.addEventListener('blur', function() {
                validateInput(this);
            });
        });
    }
    
    // Smooth scroll to result
    const resultBox = document.querySelector('.result-box');
    if (resultBox) {
        resultBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
});

// Input validation function
function validateInput(input) {
    const value = input.value;
    const name = input.name;
    let isValid = true;
    let message = '';
    
    // Age validation
    if (name === 'age' && value) {
        if (value < 1 || value > 120) {
            isValid = false;
            message = 'Age must be between 1 and 120';
        }
    }
    
    // Blood pressure validation
    if (name === 'trestbps' && value) {
        if (value < 80 || value > 200) {
            isValid = false;
            message = 'Blood pressure seems unusual (80-200 mm Hg)';
        }
    }
    
    // Cholesterol validation
    if (name === 'chol' && value) {
        if (value < 100 || value > 600) {
            isValid = false;
            message = 'Cholesterol value seems unusual (100-600 mg/dl)';
        }
    }
    
    // Heart rate validation
    if (name === 'thalach' && value) {
        if (value < 70 || value > 220) {
            isValid = false;
            message = 'Heart rate seems unusual (70-220 bpm)';
        }
    }
    
    // Update UI based on validation
    if (isValid) {
        input.style.borderColor = 'var(--success-green)';
        removeError(input);
    } else {
        input.style.borderColor = 'var(--danger-red)';
        showError(input, message);
    }
}

// Show error message
function showError(input, message) {
    removeError(input);
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.color = 'var(--danger-red)';
    errorDiv.style.fontSize = '0.85rem';
    errorDiv.style.marginTop = '5px';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    input.parentElement.appendChild(errorDiv);
}

// Remove error message
function removeError(input) {
    const existingError = input.parentElement.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
}

// Show notification
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'error' ? 'var(--danger-red)' : 'var(--success-green)'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    notification.innerHTML = `<i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'check-circle'}"></i> ${message}`;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);