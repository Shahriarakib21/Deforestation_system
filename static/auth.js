// Authentication JavaScript functionality

// Global variables
let currentForm = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupFormHandlers();
    setupPasswordStrength();
    setupFormValidation();
});

// Setup form handlers
function setupFormHandlers() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (loginForm) {
        currentForm = 'login';
        loginForm.addEventListener('submit', handleLogin);
    }
    
    if (registerForm) {
        currentForm = 'register';
        registerForm.addEventListener('submit', handleRegister);
    }
}

// Setup password strength checking
function setupPasswordStrength() {
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', checkPasswordStrength);
    }
}

// Setup form validation
function setupFormValidation() {
    const inputs = document.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearFieldError);
    });
}

// Handle login form submission
async function handleLogin(e) {
    e.preventDefault();
    
    if (!validateForm()) {
        return;
    }
    
    const formData = new FormData(e.target);
    const email = formData.get('email');
    const password = formData.get('password');
    const remember = formData.get('remember');
    
    // Show loading state
    const submitButton = e.target.querySelector('.auth-button');
    submitButton.classList.add('loading');
    
    try {
        // Simulate API call
        await simulateLogin(email, password, remember);
        
        // Redirect to dashboard
        window.location.href = '/';
        
    } catch (error) {
        showNotification(error.message, 'error');
        submitButton.classList.remove('loading');
    }
}

// Handle register form submission
async function handleRegister(e) {
    e.preventDefault();
    
    if (!validateForm()) {
        return;
    }
    
    const formData = new FormData(e.target);
    const firstName = formData.get('firstName');
    const lastName = formData.get('lastName');
    const email = formData.get('email');
    const organization = formData.get('organization');
    const role = formData.get('role');
    const password = formData.get('password');
    const confirmPassword = formData.get('confirmPassword');
    const terms = formData.get('terms');
    const newsletter = formData.get('newsletter');
    
    // Validate password confirmation
    if (password !== confirmPassword) {
        showFieldError('confirmPassword', 'Passwords do not match');
        return;
    }
    
    // Validate terms acceptance
    if (!terms) {
        showNotification('Please accept the Terms of Service and Privacy Policy', 'error');
        return;
    }
    
    // Show loading state
    const submitButton = e.target.querySelector('.auth-button');
    submitButton.classList.add('loading');
    
    try {
        // Simulate API call
        await simulateRegister({
            firstName,
            lastName,
            email,
            organization,
            role,
            password,
            newsletter
        });
        
        showNotification('Account created successfully! Redirecting to login...', 'success');
        
        // Redirect to login after a delay
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
        
    } catch (error) {
        showNotification(error.message, 'error');
        submitButton.classList.remove('loading');
    }
}

// Simulate login API call
function simulateLogin(email, password, remember) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            // Simple validation for demo
            if (email === 'admin@ecotrack.com' && password === 'admin123') {
                resolve({ success: true, user: { email, name: 'Admin User' } });
            } else if (email && password) {
                // For demo purposes, accept any valid email/password combination
                resolve({ success: true, user: { email, name: email.split('@')[0] } });
            } else {
                reject(new Error('Invalid email or password'));
            }
        }, 1500);
    });
}

// Simulate register API call
function simulateRegister(userData) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            // Check if email already exists (demo)
            if (userData.email === 'admin@ecotrack.com') {
                reject(new Error('Email already registered'));
            } else {
                resolve({ success: true, user: userData });
            }
        }, 1500);
    });
}

// Validate form
function validateForm() {
    const form = currentForm === 'login' ? document.getElementById('loginForm') : document.getElementById('registerForm');
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!validateField({ target: field })) {
            isValid = false;
        }
    });
    
    return isValid;
}

// Validate individual field
function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    const fieldName = field.name;
    
    // Clear previous errors
    clearFieldError({ target: field });
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, `${getFieldLabel(fieldName)} is required`);
        return false;
    }
    
    // Email validation
    if (fieldName === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'Please enter a valid email address');
            return false;
        }
    }
    
    // Password validation for register form
    if (fieldName === 'password' && currentForm === 'register' && value) {
        if (value.length < 8) {
            showFieldError(field, 'Password must be at least 8 characters long');
            return false;
        }
    }
    
    // Password confirmation validation
    if (fieldName === 'confirmPassword' && value) {
        const password = document.getElementById('password').value;
        if (value !== password) {
            showFieldError(field, 'Passwords do not match');
            return false;
        }
    }
    
    return true;
}

// Show field error
function showFieldError(field, message) {
    // Remove existing error
    clearFieldError({ target: field });
    
    // Create error element
    const errorElement = document.createElement('div');
    errorElement.className = 'field-error';
    errorElement.textContent = message;
    errorElement.style.cssText = `
        color: #ef4444;
        font-size: 0.8rem;
        margin-top: 0.25rem;
        animation: slideInDown 0.3s ease;
    `;
    
    // Insert error after field
    field.parentNode.insertBefore(errorElement, field.nextSibling);
    
    // Add error class to field
    field.style.borderColor = '#ef4444';
    field.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
}

// Clear field error
function clearFieldError(e) {
    const field = e.target;
    const errorElement = field.parentNode.querySelector('.field-error');
    
    if (errorElement) {
        errorElement.remove();
    }
    
    // Reset field styling
    field.style.borderColor = '';
    field.style.boxShadow = '';
}

// Get field label
function getFieldLabel(fieldName) {
    const labels = {
        'firstName': 'First Name',
        'lastName': 'Last Name',
        'email': 'Email Address',
        'organization': 'Organization',
        'role': 'Role',
        'password': 'Password',
        'confirmPassword': 'Confirm Password'
    };
    
    return labels[fieldName] || fieldName.charAt(0).toUpperCase() + fieldName.slice(1);
}

// Check password strength
function checkPasswordStrength(e) {
    const password = e.target.value;
    const strengthFill = document.getElementById('strengthFill');
    const strengthText = document.getElementById('strengthText');
    
    if (!strengthFill || !strengthText) return;
    
    let strength = 0;
    let strengthLabel = '';
    let strengthClass = '';
    
    // Length check
    if (password.length >= 8) strength += 25;
    if (password.length >= 12) strength += 25;
    
    // Character variety checks
    if (/[a-z]/.test(password)) strength += 25;
    if (/[A-Z]/.test(password)) strength += 25;
    if (/[0-9]/.test(password)) strength += 25;
    if (/[^A-Za-z0-9]/.test(password)) strength += 25;
    
    // Cap strength at 100
    strength = Math.min(strength, 100);
    
    // Determine strength level
    if (strength < 25) {
        strengthLabel = 'Very Weak';
        strengthClass = 'weak';
    } else if (strength < 50) {
        strengthLabel = 'Weak';
        strengthClass = 'weak';
    } else if (strength < 75) {
        strengthLabel = 'Fair';
        strengthClass = 'fair';
    } else if (strength < 100) {
        strengthLabel = 'Good';
        strengthClass = 'good';
    } else {
        strengthLabel = 'Strong';
        strengthClass = 'strong';
    }
    
    // Update UI
    strengthFill.style.width = strength + '%';
    strengthFill.className = 'strength-fill ' + strengthClass;
    strengthText.textContent = strengthLabel;
}

// Toggle password visibility
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleButton = document.querySelector('.password-toggle');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleButton.innerHTML = '<i class="fas fa-eye-slash"></i>';
    } else {
        passwordInput.type = 'password';
        toggleButton.innerHTML = '<i class="fas fa-eye"></i>';
    }
}

// Toggle confirm password visibility
function toggleConfirmPassword() {
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const toggleButton = confirmPasswordInput.parentNode.querySelector('.password-toggle');
    
    if (confirmPasswordInput.type === 'password') {
        confirmPasswordInput.type = 'text';
        toggleButton.innerHTML = '<i class="fas fa-eye-slash"></i>';
    } else {
        confirmPasswordInput.type = 'password';
        toggleButton.innerHTML = '<i class="fas fa-eye"></i>';
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">&times;</button>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        max-width: 400px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Close button functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    });
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (document.body.contains(notification)) {
            notification.style.transform = 'translateX(400px)';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }
    }, 5000);
}

// Get notification icon
function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Get notification color
function getNotificationColor(type) {
    const colors = {
        'success': '#10b981',
        'error': '#ef4444',
        'warning': '#f59e0b',
        'info': '#3b82f6'
    };
    return colors[type] || '#3b82f6';
}

// Add CSS animations
const additionalStyles = `
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .field-error {
        color: #ef4444;
        font-size: 0.8rem;
        margin-top: 0.25rem;
        animation: slideInDown 0.3s ease;
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// Social authentication handlers
document.addEventListener('DOMContentLoaded', function() {
    const googleButtons = document.querySelectorAll('.social-button.google');
    const microsoftButtons = document.querySelectorAll('.social-button.microsoft');
    
    googleButtons.forEach(button => {
        button.addEventListener('click', () => {
            showNotification('Google authentication coming soon!', 'info');
        });
    });
    
    microsoftButtons.forEach(button => {
        button.addEventListener('click', () => {
            showNotification('Microsoft authentication coming soon!', 'info');
        });
    });
});

// Forgot password handler
document.addEventListener('DOMContentLoaded', function() {
    const forgotPasswordLinks = document.querySelectorAll('.forgot-password');
    
    forgotPasswordLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            showNotification('Password reset functionality coming soon!', 'info');
        });
    });
});

// Terms and privacy policy handlers
document.addEventListener('DOMContentLoaded', function() {
    const termsLinks = document.querySelectorAll('.terms-link');
    
    termsLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            showNotification('Terms and Privacy Policy coming soon!', 'info');
        });
    });
});
