// ========== GLOBAL CURRENCY SYSTEM ==========

const CURRENCY_SYMBOLS = { USD: '$', EUR: '€', GBP: '£', INR: '₹' };

function getStoredCurrency() {
    return getCookie('currency') || 'USD';
}

function setCurrencyPreference(cur) {
    document.cookie = `currency=${cur}; path=/; max-age=${365 * 86400}`;
    window.location.reload(); // reload to re-fetch all data with new currency
}

function getCurrencyFormatter() {
    const cur = getStoredCurrency();
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: cur });
}

function getCurrencySymbol() {
    return CURRENCY_SYMBOLS[getStoredCurrency()] || '$';
}

// ========== COOKIE HELPERS ==========

function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let c of cookies) {
        const [k, v] = c.trim().split('=');
        if (k === name) return v;
    }
    return null;
}

// ========== AUTH ==========

async function handleAuth(event, type) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    const alertContainer = document.getElementById('alert-container');
    alertContainer.style.display = 'none';

    try {
        const url = type === 'login' ? '/auth/login' : '/auth/register';
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            alertContainer.textContent = result.message || 'An error occurred';
            alertContainer.style.display = 'block';
            alertContainer.style.color = 'var(--loss-color)';
            return;
        }

        if (type === 'login') {
            if (result.token) {
                document.cookie = `token=${result.token}; path=/; max-age=86400`;
            }
            window.location.href = '/dashboard';
        } else {
            alertContainer.style.color = 'var(--gain-color)';
            alertContainer.textContent = 'Registration successful! Please login.';
            alertContainer.style.display = 'block';
            switchTab('login');
            setTimeout(() => { alertContainer.style.color = 'var(--loss-color)'; }, 3000);
        }

    } catch (err) {
        alertContainer.textContent = 'Failed to connect to server';
        alertContainer.style.display = 'block';
        alertContainer.style.color = 'var(--loss-color)';
    }
}

function handleLogout() {
    fetch('/auth/logout', { method: 'POST' }).then(() => {
        document.cookie = 'token=; Max-Age=0; path=/;';
        window.location.href = '/';
    });
}
