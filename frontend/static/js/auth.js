document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const errorMsg = document.getElementById('error-msg');

    if (loginForm) {
        loginForm.onsubmit = async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            errorMsg.innerText = "Đang xử lý...";
            
            try {
                // Gọi qua class api đã tạo
                const data = await api.login(username, password);
                
                // Lưu token
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('user_role', data.role);
                
                // Điều hướng dựa trên Role
                if (data.role === 'ADMIN') {
                    window.location.href = 'dashboard_admin.html';
                } else if (data.role === 'DOCTOR') {
                    window.location.href = 'dashboard_doctor.html';
                } else {
                     window.location.href = 'index.html';
                }
                
            } catch (err) {
                errorMsg.innerText = err.message;
            }
        };
    }
});