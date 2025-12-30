--sys--
ALTER SYSTEM SET RESOURCE_LIMIT = TRUE;


CREATE PROFILE PF_HOSPITAL_ADMIN LIMIT
    -- 1. Quản lý Mật khẩu
    FAILED_LOGIN_ATTEMPTS 3         -- Nhập sai 3 lần sẽ bị khóa
    PASSWORD_LIFE_TIME 60           -- Mật khẩu hết hạn sau 60 ngày
    PASSWORD_REUSE_TIME 365         -- Không được dùng lại mật khẩu cũ trong 1 năm
    PASSWORD_REUSE_MAX 5            -- Không trùng với 5 mật khẩu gần nhất
    PASSWORD_LOCK_TIME 1            -- Khóa tài khoản trong 1 ngày nếu vi phạm
    PASSWORD_GRACE_TIME 7           -- Cảnh báo đổi mật khẩu trước 7 ngày
    SESSIONS_PER_USER 1             -- Mỗi Admin chỉ được mở 1 phiên làm việc (tránh share acc)
    IDLE_TIME 30                    -- Treo máy 30 phút tự động ngắt kết nối
    CONNECT_TIME UNLIMITED;         -- Không giới hạn tổng thời gian kết nối (để làm việc lâu dài)


CREATE PROFILE PF_MEDICAL_STAFF LIMIT
    -- 1. Quản lý Mật khẩu
    FAILED_LOGIN_ATTEMPTS 5         -- Cho phép sai 5 lần (đỡ bị khóa nhầm lúc vội)
    PASSWORD_LIFE_TIME 90           -- Mật khẩu hết hạn sau 90 ngày
    PASSWORD_REUSE_TIME 180         -- Không dùng lại trong 6 tháng
    PASSWORD_LOCK_TIME 1/24         -- Chỉ khóa 1 tiếng (để còn quay lại làm việc sớm)
    PASSWORD_GRACE_TIME 7
    SESSIONS_PER_USER 2             -- Cho phép đăng nhập trên 2 thiết bị (ví dụ: PC và Máy tính bảng)
    IDLE_TIME 60                    -- Treo máy 60 phút mới ngắt (dài hơn Admin)
    CONNECT_TIME 600;               -- Giới hạn 1 ca làm việc (10 tiếng), tránh treo nick qua đêm

-- 1. Gán cho nhóm ADMIN (admin01, admin02)
ALTER USER admin01 PROFILE PF_HOSPITAL_ADMIN;
ALTER USER admin02 PROFILE PF_HOSPITAL_ADMIN;

-- 2. Gán cho nhóm DOCTOR (Bác sĩ)
ALTER USER doctor_an PROFILE PF_MEDICAL_STAFF;
ALTER USER doctor_tam PROFILE PF_MEDICAL_STAFF;
ALTER USER doctor_quoc PROFILE PF_MEDICAL_STAFF;
ALTER USER doctor_nhi PROFILE PF_MEDICAL_STAFF;
ALTER USER doctor_hung PROFILE PF_MEDICAL_STAFF;
ALTER USER doctor_thao PROFILE PF_MEDICAL_STAFF;

-- 3. Gán cho nhóm NURSE (Y tá)
ALTER USER nurse_phuong PROFILE PF_MEDICAL_STAFF;
ALTER USER nurse_thu PROFILE PF_MEDICAL_STAFF;
ALTER USER nurse_tu PROFILE PF_MEDICAL_STAFF;
ALTER USER nurse_hoa PROFILE PF_MEDICAL_STAFF;
