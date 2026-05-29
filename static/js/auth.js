/**
 * auth.js — Auth Page Logic + Shared UI Behaviors
 * CardioPredict AI
 */

'use strict';

// ─────────────────────────────────────────────
// Navbar: scroll shadow + mobile hamburger
// ─────────────────────────────────────────────

(function initNavbar() {
    const navbar = document.getElementById('navbar');
    const hamburger = document.getElementById('navHamburger');
    const navLinks = document.getElementById('navLinks');

    if (navbar) {
        window.addEventListener('scroll', () => {
            navbar.classList.toggle('scrolled', window.scrollY > 10);
        }, { passive: true });
    }

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('open');
            const spans = hamburger.querySelectorAll('span');
            spans.forEach(s => s.classList.toggle('open'));
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
                navLinks.classList.remove('open');
            }
        });
    }
})();


// ─────────────────────────────────────────────
// Auto-dismiss flash messages
// ─────────────────────────────────────────────

(function initFlashMessages() {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach((flash, i) => {
        setTimeout(() => {
            flash.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            flash.style.opacity = '0';
            flash.style.transform = 'translateX(20px)';
            setTimeout(() => flash.remove(), 400);
        }, 5000 + i * 500);
    });
})();


// ─────────────────────────────────────────────
// Toggle Password Visibility
// ─────────────────────────────────────────────

function togglePassword(inputId, btn) {
    const input = document.getElementById(inputId);
    const icon = btn.querySelector('i');
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
}


// ─────────────────────────────────────────────
// Password Strength Meter (Register page)
// ─────────────────────────────────────────────

(function initPasswordStrength() {
    const passwordInput = document.getElementById('reg_password');
    const strengthFill = document.getElementById('strengthFill');
    const strengthLabel = document.getElementById('strengthLabel');

    if (!passwordInput || !strengthFill) return;

    const levels = [
        { label: 'Very weak', class: 's1', color: '#ef4444' },
        { label: 'Weak', class: 's2', color: '#f59e0b' },
        { label: 'Good', class: 's3', color: '#3b82f6' },
        { label: 'Strong', class: 's4', color: '#22c55e' },
    ];

    function getStrength(pwd) {
        let score = 0;
        if (pwd.length >= 8) score++;
        if (pwd.length >= 12) score++;
        if (/[A-Z]/.test(pwd)) score++;
        if (/[0-9]/.test(pwd)) score++;
        if (/[^A-Za-z0-9]/.test(pwd)) score++;
        return Math.min(Math.ceil(score / 5 * 4), 4); // 1–4
    }

    passwordInput.addEventListener('input', () => {
        const pwd = passwordInput.value;
        if (!pwd) {
            strengthFill.className = 'strength-fill';
            strengthFill.style.width = '0';
            strengthLabel.textContent = 'Password strength';
            strengthLabel.style.color = '';
            return;
        }
        const strength = getStrength(pwd);
        const level = levels[strength - 1];
        strengthFill.className = `strength-fill ${level.class}`;
        strengthLabel.textContent = level.label;
        strengthLabel.style.color = level.color;
    });
})();


// ─────────────────────────────────────────────
// Register Form: Real-time Validation
// ─────────────────────────────────────────────

(function initRegisterValidation() {
    const form = document.getElementById('registerForm');
    if (!form) return;

    const fullNameInput = document.getElementById('reg_full_name');
    const emailInput = document.getElementById('reg_email');
    const passwordInput = document.getElementById('reg_password');
    const confirmInput = document.getElementById('reg_confirm_password');

    function validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function setFieldState(input, statusIconEl, errorEl, isValid, errorMsg) {
        if (!input) return;
        const icon = input.parentElement.querySelector('.field-status-icon');
        if (isValid) {
            input.classList.remove('invalid');
            input.classList.add('valid');
            if (icon) { icon.innerHTML = '<i class="fas fa-check-circle" style="color:#4ade80"></i>'; }
            if (errorEl) errorEl.textContent = '';
        } else {
            input.classList.remove('valid');
            input.classList.add('invalid');
            if (icon) { icon.innerHTML = '<i class="fas fa-circle-xmark" style="color:#f87171"></i>'; }
            if (errorEl) errorEl.textContent = errorMsg;
        }
    }

    function clearField(input) {
        if (!input) return;
        input.classList.remove('valid', 'invalid');
        const icon = input.parentElement.querySelector('.field-status-icon');
        if (icon) icon.innerHTML = '';
    }

    // Full Name
    if (fullNameInput) {
        fullNameInput.addEventListener('blur', () => {
            const v = fullNameInput.value.trim();
            if (!v) { clearField(fullNameInput); return; }
            setFieldState(fullNameInput, null, document.getElementById('fullNameError'),
                v.length >= 2, 'Name must be at least 2 characters.');
        });
    }

    // Email
    if (emailInput) {
        emailInput.addEventListener('blur', () => {
            const v = emailInput.value.trim();
            if (!v) { clearField(emailInput); return; }
            setFieldState(emailInput, null, document.getElementById('regEmailError'),
                validateEmail(v), 'Please enter a valid email address.');
        });
    }

    // Password
    if (passwordInput) {
        passwordInput.addEventListener('blur', () => {
            const v = passwordInput.value;
            if (!v) { clearField(passwordInput); return; }
            const ok = v.length >= 8 && /[A-Z]/.test(v) && /\d/.test(v);
            setFieldState(passwordInput, null, document.getElementById('regPasswordError'),
                ok, 'Min 8 chars, 1 uppercase letter, 1 number.');
        });
    }

    // Confirm Password
    if (confirmInput) {
        confirmInput.addEventListener('input', () => {
            const v = confirmInput.value;
            if (!v) { clearField(confirmInput); return; }
            const ok = v === passwordInput.value;
            setFieldState(confirmInput, null, document.getElementById('confirmPasswordError'),
                ok, 'Passwords do not match.');
        });
    }

    // Prevent submit if client-side errors
    form.addEventListener('submit', (e) => {
        const submitBtn = document.getElementById('registerSubmit');
        if (submitBtn) {
            submitBtn.querySelector('.btn-text').classList.add('hidden');
            submitBtn.querySelector('.btn-loader').classList.remove('hidden');
            submitBtn.disabled = true;
        }
    });
})();


// ─────────────────────────────────────────────
// Login Form: Loading State
// ─────────────────────────────────────────────

(function initLoginForm() {
    const form = document.getElementById('loginForm');
    if (!form) return;

    form.addEventListener('submit', () => {
        const submitBtn = document.getElementById('loginSubmit');
        if (submitBtn) {
            submitBtn.querySelector('.btn-text').classList.add('hidden');
            submitBtn.querySelector('.btn-loader').classList.remove('hidden');
            submitBtn.disabled = true;
        }
    });

    // Email field live feedback
    const emailInput = document.getElementById('login_email');
    if (emailInput) {
        emailInput.addEventListener('blur', () => {
            const v = emailInput.value.trim();
            const icon = emailInput.parentElement.querySelector('.field-status-icon');
            if (!v) { if (icon) icon.innerHTML = ''; return; }
            const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
            if (icon) {
                icon.innerHTML = ok
                    ? '<i class="fas fa-check-circle" style="color:#4ade80"></i>'
                    : '<i class="fas fa-circle-xmark" style="color:#f87171"></i>';
            }
        });
    }
})();


// ─────────────────────────────────────────────
// Prediction Form: Submit Loading State
// ─────────────────────────────────────────────

(function initPredictionForm() {
    const form = document.getElementById('predictionForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (!form || !analyzeBtn) return;

    form.addEventListener('submit', () => {
        analyzeBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Analyzing...';
        analyzeBtn.disabled = true;
    });

    // Scroll to result if present
    const result = document.getElementById('predictionResult') || document.getElementById('predictionError');
    if (result) {
        setTimeout(() => {
            result.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
})();


// ─────────────────────────────────────────────
// Landing Page: Intersection Observer Animations
// ─────────────────────────────────────────────

(function initLandingAnimations() {
    const cards = document.querySelectorAll('.feature-card, .step-card, .stat-card');
    if (!cards.length || !('IntersectionObserver' in window)) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });

    cards.forEach((card, i) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(24px)';
        card.style.transition = `opacity 0.5s ease ${i * 0.06}s, transform 0.5s ease ${i * 0.06}s`;
        observer.observe(card);
    });
})();
