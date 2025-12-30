document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const errorMsg = document.getElementById('error-msg');

    if (loginForm) {
        loginForm.onsubmit = async (e) => {
            e.preventDefault();
            
            const usernameInput = document.getElementById('username');
            const passwordInput = document.getElementById('password');
            const btn = loginForm.querySelector('button');

            // Reset trạng thái
            errorMsg.innerText = "";
            btn.disabled = true;
            btn.innerText = "Đang xử lý...";

            try {
                // Gọi hàm login đã sửa ở bước 1
                const user = await api.login(usernameInput.value, passwordInput.value);
                
                // Điều hướng dựa trên Role
                if (user && user.role) {
                    api.redirectByRole(user.role);
                } else {
                    throw new Error("Lỗi: Token không chứa thông tin quyền hạn (Role)");
                }

            } catch (err) {
                console.error(err);
                errorMsg.innerText = err.message;
                btn.disabled = false;
                btn.innerText = "Đăng nhập";
            }
        };
    }
});