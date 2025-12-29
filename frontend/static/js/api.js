class ClinicAPI {
    constructor(baseUrl = "") {
        this.baseUrl = baseUrl;
    }

    _getToken() {
        return localStorage.getItem('access_token');
    }

    async request(endpoint, method = 'GET', body = null) {
        const headers = {
            'Content-Type': 'application/json'
        };

        const token = this._getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            method,
            headers,
        };

        if (body) {
            config.body = JSON.stringify(body);
        }

        try {
            const res = await fetch(`${this.baseUrl}${endpoint}`, config);
            const data = await res.json();
            
            if (!res.ok) {
                // Xử lý lỗi token hết hạn hoặc lỗi từ backend trả về
                if (res.status === 401) {
                    alert("Phiên đăng nhập hết hạn hoặc không hợp lệ.");
                    window.location.href = '/static/pages/login.html';
                }
                throw new Error(data.detail || JSON.stringify(data));
            }
            return data;
        } catch (error) {
            console.error("API Error:", error);
            throw error;
        }
    }

    // Login Function for form-data OAuth2PasswordRequestForm
    async login(username, password) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        // fetch sẽ tự động set 'multipart/form-data' hoặc 'x-www-form-urlencoded'
        const res = await fetch(`${this.baseUrl}/auth/login`, {
            method: 'POST',
            body: formData 
        });

        const data = await res.json();
        
        if (!res.ok) {
             throw new Error(data.detail || JSON.stringify(data));
        }
        return data;
    }

    // Login Function for JSON body
    // login(username, password) {
    //     return this.request('/auth/login', 'POST', { username, password });
    // }
    
    // Ví dụ hàm lấy danh sách bệnh nhân
    getPatients() {
        return this.request('/patient/patients', 'GET');
    }
}

// Export instance để dùng toàn cục
const api = new ClinicAPI('http://127.0.0.1:8000');