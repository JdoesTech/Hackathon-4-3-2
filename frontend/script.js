// Global state
let currentUser = null;
let loadingSteps = ['Analyzing profile', 'Filtering scholarships', 'Calculating AI matches'];
let currentStep = 0;

// Page management
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(pageId).classList.add('active');
}

function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.add('active');
    
    // Animate loading steps
    currentStep = 0;
    updateLoadingStep();
    
    const stepInterval = setInterval(() => {
        currentStep++;
        if (currentStep < loadingSteps.length) {
            updateLoadingStep();
        } else {
            clearInterval(stepInterval);
        }
    }, 1000);
}

function updateLoadingStep() {
    const steps = document.querySelectorAll('.loading-step');
    steps.forEach((step, index) => {
        step.classList.toggle('active', index === currentStep);
    });
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.remove('active');
}

// Auth tab switching with smooth animation
function switchTab(tab) {
    const buttons = document.querySelectorAll('.tab-btn');
    const forms = document.querySelectorAll('.auth-form');
    
    // Remove active classes
    buttons.forEach(btn => btn.classList.remove('active'));
    forms.forEach(form => form.classList.remove('active'));
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Show corresponding form with delay for smooth transition
    setTimeout(() => {
        document.getElementById(`${tab}-form`).classList.add('active');
    }, 150);
}

// Enhanced authentication with better error handling
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    if (!email || !password) {
        showMessage('Please fill in all fields', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentUser = { id: data.userId, name: data.name };
            document.getElementById('user-name').textContent = `Welcome, ${data.name}!`;
            document.getElementById('user-name-results').textContent = `Welcome, ${data.name}!`;
            
            setTimeout(() => {
                hideLoading();
                showPage('profile-page');
                showMessage('Login successful! Please complete your profile.', 'success');
            }, 2000);
        } else {
            hideLoading();
            showMessage(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        hideLoading();
        showMessage('Network error. Please check your connection.', 'error');
    }
});

document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    
    if (!name || !email || !password) {
        showMessage('Please fill in all fields', 'error');
        return;
    }
    
    if (password.length < 6) {
        showMessage('Password must be at least 6 characters long', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentUser = { id: data.userId, name };
            document.getElementById('user-name').textContent = `Welcome, ${name}!`;
            document.getElementById('user-name-results').textContent = `Welcome, ${name}!`;
            
            setTimeout(() => {
                hideLoading();
                showPage('profile-page');
                showMessage('Account created successfully! Please complete your profile.', 'success');
            }, 2000);
        } else {
            hideLoading();
            showMessage(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        hideLoading();
        showMessage('Network error. Please check your connection.', 'error');
    }
});

// Enhanced profile form with validation
document.getElementById('profile-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const profileData = {
        age: parseInt(document.getElementById('age').value),
        country: document.getElementById('country').value,
        education_level: document.getElementById('education-level').value,
        gpa: parseFloat(document.getElementById('gpa').value),
        field_of_study: document.getElementById('field-of-study').value,
        financial_need: document.getElementById('financial-need').value,
    };
    
    // Validation
    if (profileData.age < 16 || profileData.age > 65) {
        showMessage('Please enter a valid age between 16 and 65', 'error');
        return;
    }
    
    if (profileData.gpa < 0 || profileData.gpa > 4) {
        showMessage('Please enter a valid GPA between 0.0 and 4.0', 'error');
        return;
    }
    
    showLoading();
    
    try {
        // Update profile
        const profileResponse = await fetch(`/api/profile/${currentUser.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(profileData),
        });
        
        if (profileResponse.ok) {
            // Simulate AI processing time
            await new Promise(resolve => setTimeout(resolve, 3000));
            
            // Get matches
            const matchesResponse = await fetch(`/api/matches/${currentUser.id}`);
            const matches = await matchesResponse.json();
            
            hideLoading();
            displayScholarships(matches);
            showPage('results-page');
        } else {
            hideLoading();
            showMessage('Profile update failed. Please try again.', 'error');
        }
    } catch (error) {
        hideLoading();
        showMessage('Network error. Please check your connection.', 'error');
    }
});

// Enhanced scholarship display with animations
function displayScholarships(scholarships) {
    const container = document.getElementById('scholarships-container');
    container.innerHTML = '';
    
    // Update stats
    const totalValue = scholarships.reduce((sum, s) => sum + s.amount, 0);
    document.getElementById('total-matches').textContent = scholarships.length;
    document.getElementById('total-value').textContent = `$${totalValue.toLocaleString()}`;
    
    scholarships.forEach((scholarship, index) => {
        const card = document.createElement('div');
        card.className = 'scholarship-card';
        card.style.animationDelay = `${index * 0.15}s`;
        
        const deadlineDate = new Date(scholarship.deadline);
        const formattedDeadline = deadlineDate.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
        // Calculate days until deadline
        const today = new Date();
        const timeDiff = deadlineDate.getTime() - today.getTime();
        const daysLeft = Math.ceil(timeDiff / (1000 * 3600 * 24));
        
        card.innerHTML = `
            <div class="scholarship-header">
                <h3 class="scholarship-name">${scholarship.name}</h3>
                <div class="scholarship-amount">$${scholarship.amount.toLocaleString()}</div>
            </div>
            
            <div class="confidence-section">
                <div class="confidence-label">
                    <span class="confidence-text">🎯 AI Match Score</span>
                    <span class="confidence-score">${scholarship.confidence}%</span>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" data-width="${scholarship.confidence}"></div>
                </div>
            </div>
            
            <p class="scholarship-description">${scholarship.description}</p>
            
            <div class="deadline-section">
                <div class="deadline-label">Application Deadline</div>
                <div class="deadline-date">${formattedDeadline}</div>
                ${daysLeft > 0 ? `<div style="font-size: 0.85rem; margin-top: 4px; opacity: 0.9;">${daysLeft} days remaining</div>` : ''}
            </div>
            
            <div class="scholarship-actions">
                <a href="${scholarship.apply_url}" target="_blank" class="apply-btn">
                    Apply Now
                </a>
                <div class="feedback-buttons">
                    <button class="feedback-btn like" onclick="submitFeedback(${scholarship.id}, 1, this)" title="This matches my interests">
                        👍
                    </button>
                    <button class="feedback-btn dislike" onclick="submitFeedback(${scholarship.id}, 0, this)" title="Not relevant for me">
                        👎
                    </button>
                </div>
            </div>
        `;
        
        container.appendChild(card);
        
        // Animate confidence bar after card is added
        setTimeout(() => {
            const fill = card.querySelector('.confidence-fill');
            const width = fill.getAttribute('data-width');
            fill.style.width = `${width}%`;
        }, 100 + (index * 150));
    });
    
    // Add floating elements for visual appeal
    addFloatingElements();
}

function addFloatingElements() {
    const container = document.querySelector('.results-header');
    const elements = ['🌟', '💎', '🚀', '⭐', '💫'];
    
    elements.forEach((emoji, index) => {
        const element = document.createElement('div');
        element.className = 'floating-element';
        element.textContent = emoji;
        element.style.left = `${20 + (index * 15)}%`;
        element.style.top = `${30 + (index * 10)}%`;
        element.style.animationDelay = `${index * 0.5}s`;
        element.style.fontSize = '2rem';
        container.appendChild(element);
    });
}

// Enhanced feedback system with visual feedback
async function submitFeedback(scholarshipId, rating, button) {
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userId: currentUser.id,
                scholarshipId,
                rating
            }),
        });
        
        if (response.ok) {
            // Update button states with animation
            const card = button.closest('.scholarship-card');
            const feedbackButtons = card.querySelectorAll('.feedback-btn');
            
            feedbackButtons.forEach(btn => {
                btn.classList.remove('active');
                btn.style.transform = 'scale(1)';
            });
            
            button.classList.add('active');
            button.style.transform = 'scale(1.2)';
            
            // Show success animation
            const successIcon = document.createElement('div');
            successIcon.textContent = '✨';
            successIcon.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 1.5rem;
                pointer-events: none;
                animation: successPop 0.6s ease-out;
            `;
            
            button.style.position = 'relative';
            button.appendChild(successIcon);
            
            setTimeout(() => {
                successIcon.remove();
                button.style.transform = 'scale(1)';
            }, 600);
            
            showMessage('Thank you for your feedback! This helps improve our AI matching.', 'success');
        }
    } catch (error) {
        showMessage('Feedback submission failed. Please try again.', 'error');
    }
}

// Add success animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes successPop {
        0% { opacity: 0; transform: translate(-50%, -50%) scale(0); }
        50% { opacity: 1; transform: translate(-50%, -50%) scale(1.2); }
        100% { opacity: 0; transform: translate(-50%, -50%) scale(0); }
    }
`;
document.head.appendChild(style);

// Utility functions
function showMessage(message, type) {
    // Remove existing messages
    document.querySelectorAll('.message').forEach(msg => msg.remove());
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px;">
            <span>${type === 'success' ? '✅' : '❌'}</span>
            <span>${message}</span>
        </div>
    `;
    
    const activeForm = document.querySelector('.auth-form.active') || 
                     document.querySelector('.profile-form') ||
                     document.querySelector('.container');
    
    if (activeForm) {
        activeForm.insertBefore(messageDiv, activeForm.firstChild);
        
        setTimeout(() => {
            messageDiv.style.animation = 'messageSlideOut 0.3s ease-out';
            setTimeout(() => messageDiv.remove(), 300);
        }, 4000);
    }
}

// Add message slide out animation
const messageStyle = document.createElement('style');
messageStyle.textContent = `
    @keyframes messageSlideOut {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-20px);
        }
    }
`;
document.head.appendChild(messageStyle);

function showProfile() {
    showPage('profile-page');
    
    // Update progress indicator
    const steps = document.querySelectorAll('.progress-step');
    steps[0].classList.add('active');
    steps[1].classList.remove('active');
    steps[2].classList.remove('active');
}

function logout() {
    currentUser = null;
    
    // Reset all forms
    document.getElementById('login-form').reset();
    document.getElementById('register-form').reset();
    document.getElementById('profile-form').reset();
    
    // Clear any messages
    document.querySelectorAll('.message').forEach(msg => msg.remove());
    
    // Show login page with animation
    showPage('login-page');
    showMessage('You have been logged out successfully', 'success');
}

// Form validation enhancements
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validateGPA(gpa) {
    return gpa >= 0 && gpa <= 4;
}

// Add real-time validation
document.addEventListener('DOMContentLoaded', () => {
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', () => {
            if (input.value && !validateEmail(input.value)) {
                input.style.borderColor = '#ef4444';
                showMessage('Please enter a valid email address', 'error');
            } else {
                input.style.borderColor = '#e5e7eb';
            }
        });
    });
    
    // GPA validation
    const gpaInput = document.getElementById('gpa');
    if (gpaInput) {
        gpaInput.addEventListener('blur', () => {
            const gpa = parseFloat(gpaInput.value);
            if (gpaInput.value && !validateGPA(gpa)) {
                gpaInput.style.borderColor = '#ef4444';
                showMessage('GPA must be between 0.0 and 4.0', 'error');
            } else {
                gpaInput.style.borderColor = '#e5e7eb';
            }
        });
    }
    
    // Initialize app
    showPage('login-page');
    
    // Add some visual flair
    setTimeout(() => {
        document.body.style.animation = 'none';
    }, 1000);
});

// Enhanced progress tracking
function updateProgressIndicator(step) {
    const steps = document.querySelectorAll('.progress-step');
    steps.forEach((stepEl, index) => {
        stepEl.classList.toggle('active', index <= step);
    });
}

// Keyboard navigation support
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const overlay = document.getElementById('loading-overlay');
        if (overlay.classList.contains('active')) {
            // Don't allow escape during loading
            e.preventDefault();
        }
    }
    
    if (e.key === 'Enter' && e.target.tagName === 'BUTTON') {
        e.target.click();
    }
});

// Add smooth scrolling for better UX
document.documentElement.style.scrollBehavior = 'smooth';

// Performance optimization: Lazy load animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animationPlayState = 'running';
        }
    });
}, observerOptions);

// Observe elements when they're created
function observeElement(element) {
    element.style.animationPlayState = 'paused';
    observer.observe(element);
}