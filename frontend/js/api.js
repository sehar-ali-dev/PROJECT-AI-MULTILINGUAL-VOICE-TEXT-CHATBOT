const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

/**
 * Central API wrapper function
 * Automatically injects Authorization header if token exists in localStorage
 * Handles 401 responses by clearing storage and redirecting to login
 */
async function fetchAPI(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        ...options,
        headers,
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        
        if (response.status === 401) {
            localStorage.clear();
            window.location.href = '/login.html';
            return null;
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API request failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Authentication API functions
 */
const authAPI = {
    async register(email, password, full_name, role = 'USER') {
        return fetchAPI('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, password, full_name, role }),
        });
    },
    
    async login(email, password) {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData,
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }
        
        return await response.json();
    },
    
    async getCurrentUser() {
        return fetchAPI('/auth/me');
    },
};

/**
 * Verify active session on page load
 */
async function verifySession() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login.html';
        return false;
    }
    
    try {
        const user = await authAPI.getCurrentUser();
        return user;
    } catch (error) {
        localStorage.clear();
        window.location.href = '/login.html';
        return false;
    }
}
