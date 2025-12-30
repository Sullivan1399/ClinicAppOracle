class ClinicAPI {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    // --- 1. Tiện ích Token ---

    _getToken() {
        return localStorage.getItem('access_token');
    }

    _setToken(token) {
        localStorage.setItem('access_token', token);
    }

    _removeToken() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
    }

    // Hàm giải mã JWT để lấy thông tin user (Role, Sub...)
    parseJwt(token) {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
            return JSON.parse(jsonPayload);
        } catch (e) {
            return null;
        }
    }

    // --- 2. Core Request ---

    async request(endpoint, method = 'GET', body = null) {
        const headers = {};
        const token = this._getToken();

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = { method, headers };

        if (body && !(body instanceof FormData) && !(body instanceof URLSearchParams)) {
            headers['Content-Type'] = 'application/json';
            config.body = JSON.stringify(body);
        } else if (body) {
            config.body = body;
        }

        try {
            const res = await fetch(`${this.baseUrl}${endpoint}`, config);

            if (res.status === 401) {
                alert("Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.");
                this.logout();
                return null;
            }

            if (!res.ok) {
                // Đọc lỗi trả về từ Backend
                const errorData = await res.json().catch(() => ({ detail: res.statusText }));
                
                // === PHẦN SỬA LỖI [object Object] ===
                let errorMessage = errorData.detail || "Lỗi không xác định";

                // Nếu là mảng lỗi (Validation Error của FastAPI)
                if (Array.isArray(errorMessage)) {
                    // Gom các lỗi lại thành 1 chuỗi dễ đọc
                    errorMessage = errorMessage.map(err => 
                        `- Trường '${err.loc[1] || err.loc[0]}': ${err.msg}`
                    ).join('\n');
                } 
                // Nếu là object lỗi khác
                else if (typeof errorMessage === 'object') {
                    errorMessage = JSON.stringify(errorMessage, null, 2);
                }
                // =====================================

                throw new Error(errorMessage);
            }

            return await res.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // --- 3. Authentication ---

    async login(username, password) {
        // 1. Tạo dữ liệu dạng Form (x-www-form-urlencoded) để khớp với OAuth2PasswordRequestForm của Backend
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        // 2. Gọi đúng đường dẫn /auth/login (Khớp với @router.post("/login") trong authRouter.py)
        const res = await fetch(`${this.baseUrl}/auth/login`, { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded', // Bắt buộc
            },
            body: formData
        });

        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.detail || "Tên đăng nhập hoặc mật khẩu không đúng");
        }
        
        const data = await res.json();
        
        // 3. Lưu token
        this._setToken(data.access_token);
        
        // 4. Giải mã JWT để lấy Role & User Info
        const userInfo = this.parseJwt(data.access_token);
        if (userInfo) {
            localStorage.setItem('user', JSON.stringify({
                username: userInfo.sub,
                role: userInfo.role, // Backend trả về key 'role' trong payload
                full_name: userInfo.full_name || userInfo.sub
            }));
        }
        
        return userInfo; 
    }

    logout() {
        this._removeToken();
        window.location.href = 'login.html';
    }

    // Hàm kiểm tra quyền dùng ở các trang con
    checkAuth(requiredRole = null) {
        const token = this._getToken();
        const userStr = localStorage.getItem('user');

        if (!token || !userStr) {
            window.location.href = 'login.html';
            return null;
        }

        const user = JSON.parse(userStr);
        
        if (requiredRole && user.role !== requiredRole) {
            alert(`Bạn không có quyền truy cập trang này.\nYêu cầu: ${requiredRole}\nQuyền của bạn: ${user.role}`);
            // Redirect về trang đúng với role của họ
            this.redirectByRole(user.role);
            return null;
        }
        return user;
    }

    redirectByRole(role) {
        switch (role) {
            case 'ADMIN': window.location.href = 'admin.html'; break;
            case 'DOCTOR': window.location.href = 'doctor.html'; break;
            case 'NURSE': window.location.href = 'nurse.html'; break; 
            default: window.location.href = 'login.html';
        }
    }
}

// Export instance
const api = new ClinicAPI('http://127.0.0.1:8000');