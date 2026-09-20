// Login form handler
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    // Login form submission
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const errorMessage = document.getElementById('errorMessage');
            
            try {
                const response = await authAPI.login(email, password);
                
                // Save token to localStorage
                localStorage.setItem('access_token', response.access_token);
                
                // Redirect to dashboard
                window.location.href = '/dashboard.html';
            } catch (error) {
                errorMessage.textContent = error.message;
                errorMessage.style.display = 'block';
            }
        });
    }
    
    // Register form submission
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const full_name = document.getElementById('full_name').value;
            const password = document.getElementById('password').value;
            const confirm_password = document.getElementById('confirm_password').value;
            const errorMessage = document.getElementById('errorMessage');
            
            // Validate passwords match
            if (password !== confirm_password) {
                errorMessage.textContent = 'Passwords do not match';
                errorMessage.style.display = 'block';
                return;
            }
            
            try {
                await authAPI.register(email, password, full_name);
                
                // Registration successful, redirect to login
                window.location.href = '/login.html';
            } catch (error) {
                errorMessage.textContent = error.message;
                errorMessage.style.display = 'block';
            }
        });
    }
    
    // Logout function
    window.logout = function() {
        localStorage.clear();
        window.location.href = '/login.html';
    };
});
