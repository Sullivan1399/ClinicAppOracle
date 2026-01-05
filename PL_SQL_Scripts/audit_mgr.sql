-- ===================================================================
-- UDIT_PATIENT_INTEGRITY: Ghi lại mọi hành động DELETE, UPDATE trên bảng PATIENT (Giám sát tính toàn vẹn).
-- AUDIT_STAFF_PRIVACY: Ghi lại hành động SELECT vào cột lương và mật khẩu của bảng STAFF (Giám sát quyền riêng tư).
-- ===================================================================
-- Policy Bảo vệ Bệnh nhân (Chống xóa/sửa)
CREATE AUDIT POLICY AUDIT_PATIENT_INTEGRITY
    ACTIONS DELETE ON HOSPITAL_ADMIN.PATIENT,
            UPDATE ON HOSPITAL_ADMIN.PATIENT;

-- Policy Bảo vệ Nhân viên (Chống soi lương/pass)
CREATE AUDIT POLICY AUDIT_STAFF_PRIVACY
    ACTIONS SELECT(salary, password_hash) ON HOSPITAL_ADMIN.STAFF;

--  KÍCH HOẠT 
AUDIT POLICY AUDIT_PATIENT_INTEGRITY;
AUDIT POLICY AUDIT_STAFF_PRIVACY;

-- ===================================================================
--  Giám sát sửa giá thuốc
--  Giám sát việc xóa thuốc
-- ===================================================================
-- giám sát sửa giá 
CREATE AUDIT POLICY AUDIT_MEDICINE_PRICE ACTIONS UPDATE(price) ON HOSPITAL_ADMIN.MEDICINE; 
-- Kích hoạt 
AUDIT POLICY AUDIT_MEDICINE_PRICE;

-- Tạo Giám sát lệnh 
DELETE CREATE AUDIT POLICY AUDIT_MEDICINE_DELETE_LOG ACTIONS DELETE ON HOSPITAL_ADMIN.MEDICINE; 
-- Kích hoạt 
AUDIT POLICY AUDIT_MEDICINE_DELETE_LOG;

-- ===================================================================
-- Giám sát mọi hành động thêm mới (INSERT) hoặc chỉnh sửa (UPDATE) thông tin trên bảng DEPARTMENT.
-- ===================================================================
CREATE AUDIT POLICY aud_insert_update_hospital_admin_department
ACTIONS INSERT, UPDATE ON hospital_admin.department;

AUDIT POLICY aud_insert_update_hospital_admin_department;

-- ===================================================================
-- ===================================================================
-- FGA
-- ===================================================================
-- ===================================================================
-- * Giám sát truy cập trái phép Số Bảo hiểm Y tế
BEGIN 
DBMS_FGA.ADD_POLICY
( object_schema => 'HOSPITAL_ADMIN', 
object_name => 'PATIENT', 
policy_name => 'FGA_PROTECT_INSURANCE_NO', 
audit_condition => 'SYS_CONTEXT(''USERENV'', ''SESSION_USER'') NOT LIKE ''NURSE%''', 
audit_column => 'INSURANCE_NUMBER',
statement_types => 'SELECT, UPDATE', 
enable => TRUE ); 
END;
-- * Giám sát khi kê đơn thuốc số lượng lớn
-- 1. TẠO PROCEDURE XỬ LÝ (HANDLER) 
-- Procedure này sẽ được gọi tự động khi có ai đó INSERT/UPDATE số lượng > 50
CREATE OR REPLACE PROCEDURE HOSPITAL_ADMIN.LOG_HIGH_QUANTITY (
    object_schema VARCHAR2,
    object_name   VARCHAR2,
    policy_name   VARCHAR2
) AS
BEGIN
    -- Bạn có thể chèn log vào bảng riêng hoặc gửi thông báo tại đây
    DBMS_OUTPUT.PUT_LINE('CANH BAO: Phat hien ke don so luong lon (>50) tai bang ' || object_name);
END;
/

-- 2. THIẾT LẬP FINE-GRAINED AUDIT (FGA)
BEGIN 
    -- Xóa policy FGA cũ nếu có để tránh lỗi trùng lặp
    BEGIN 
        DBMS_FGA.DROP_POLICY(
            object_schema => 'HOSPITAL_ADMIN', 
            object_name   => 'PRESCRIPTION_DETAIL', 
            policy_name   => 'FGA_HIGH_QTY_ALERT'
        ); 
    EXCEPTION 
        WHEN OTHERS THEN NULL; 
    END; 

    -- Tạo bẫy FGA cho số lượng lớn 
    DBMS_FGA.ADD_POLICY (
        object_schema   => 'HOSPITAL_ADMIN', 
        object_name     => 'PRESCRIPTION_DETAIL', 
        policy_name     => 'FGA_HIGH_QTY_ALERT', 
        audit_condition => 'QUANTITY > 50',         
        audit_column    => 'QUANTITY', 
        statement_types => 'INSERT, UPDATE', 
        handler_schema  => 'HOSPITAL_ADMIN', 
        handler_module  => 'LOG_HIGH_QUANTITY',    
        enable          => TRUE 
    ); 
END; 
/
-- * Giám sát các ca khám bệnh bị "thiếu" chẩn đoán.
BEGIN
    DBMS_FGA.ADD_POLICY(
        object_schema => 'HOSPITAL_ADMIN',
        object_name => 'VISIT',
        policy_name => 'FGA_VISIT_NO_DIAGNOSIS',
        audit_condition => 'diagnosis is null',
        statement_types => 'UPDATE',
        enable => TRUE
    );
END;








-- Kiểm tra log
SELECT 
    event_timestamp, 
    dbusername AS "KE_THUC_HIEN", 
    action_name AS "HANH_DONG", 
    object_name AS "DOI_TUONG", 
    sql_text    AS "LENH_CU_THE"
FROM UNIFIED_AUDIT_TRAIL
WHERE object_name IN ('PATIENT', 'STAFF')
  AND dbusername != 'SYS'
ORDER BY event_timestamp DESC;
