-- Create Stored Procedure (Wrapper Procedure) for automatically creating user and labeling user OLS

-- 1. Hàm trợ giúp: Map Department ID sang OLS Compartment
CREATE OR REPLACE FUNCTION get_ols_compartment(p_dept_id NUMBER) 
RETURN VARCHAR2 IS
BEGIN
    CASE p_dept_id
        WHEN 1 THEN RETURN 'INT'; -- Nội
        WHEN 2 THEN RETURN 'SUR'; -- Ngoại
        WHEN 3 THEN RETURN 'PED'; -- Nhi
        WHEN 4 THEN RETURN 'ER';  -- Cấp cứu
        WHEN 5 THEN RETURN 'ADM'; -- Hành chính
        ELSE RETURN NULL;
    END CASE;
END;
/

-- 2. Procedure chính: Tạo User, Gán Role, Gán OLS Label, Insert bảng Staff
CREATE OR REPLACE PROCEDURE create_hospital_staff_user (
    p_full_name     IN VARCHAR2,
    p_username      IN VARCHAR2,
    p_password      IN VARCHAR2, -- Mật khẩu thô để tạo DB User
    p_role          IN VARCHAR2, -- 'DOCTOR', 'NURSE', 'ADMIN'
    p_phone         IN VARCHAR2,
    p_email         IN VARCHAR2,
    p_dept_id       IN NUMBER,
    p_salary        IN NUMBER,
    p_hashed_pass   IN VARCHAR2  -- Mật khẩu hash để lưu vào bảng STAFF (cho app login)
) AUTHID CURRENT_USER AS
    v_sql           VARCHAR2(1000);
    v_ols_label     VARCHAR2(200);
    v_compartment   VARCHAR2(10);
    v_db_role       VARCHAR2(50);
BEGIN
    -- A. Insert vào bảng STAFF (để lưu hồ sơ nhân sự)
    INSERT INTO STAFF (full_name, username, password_hash, role, phone, email, department_id, salary)
    VALUES (p_full_name, p_username, p_hashed_pass, p_role, p_phone, p_email, p_dept_id, p_salary);

    -- B. Tạo Oracle User (Dynamic SQL vì DDL không chạy trực tiếp trong PL/SQL)
    v_sql := 'CREATE USER ' || p_username || ' IDENTIFIED BY "' || p_password || '" DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS';
    EXECUTE IMMEDIATE v_sql;

    v_sql := 'GRANT CONNECT, RESOURCE TO ' || p_username;
    EXECUTE IMMEDIATE v_sql;

    -- C. Gán Role tương ứng
    IF p_role = 'ADMIN' THEN
        v_db_role := 'admin_role';
    ELSIF p_role = 'DOCTOR' THEN
        v_db_role := 'doctor_role';
    ELSIF p_role = 'NURSE' THEN
        v_db_role := 'nurse_role';
    END IF;
    
    IF v_db_role IS NOT NULL THEN
        v_sql := 'GRANT ' || v_db_role || ' TO ' || p_username;
        EXECUTE IMMEDIATE v_sql;
    END IF;

    -- D. Gán nhãn OLS (Logic phức tạp nhất)
    -- Lấy mã khoa (Compartment)
    v_compartment := get_ols_compartment(p_dept_id);
    
    IF v_compartment IS NOT NULL THEN
        -- Logic tạo label string dựa trên Role
        IF p_role = 'NURSE' THEN
            v_ols_label := 'PUB:INT,SUR,PED,ER,ADM:CLI';
            
        ELSIF p_role = 'DOCTOR' THEN
            v_ols_label := 'SEC:' || v_compartment || ':CLI';
            
        ELSIF p_role = 'ADMIN' THEN
            v_ols_label := 'SEC:INT,SUR,PED,ER,ADM:CLI';
        END IF;

        -- Gọi hàm OLS policy (Cần quyền LBAC_DBA hoặc quyền execute trên package này)
        sa_user_admin.set_user_labels (
            policy_name     => 'HOSPITAL_OLS',
            user_name       => UPPER(p_username),
            max_read_label  => v_ols_label,
            max_write_label => v_ols_label,
            def_label       => v_ols_label,
            row_label       => v_ols_label
        );
    END IF;

    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;
/