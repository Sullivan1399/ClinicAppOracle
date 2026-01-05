-- ==========================================================================
-- Cài đặt ODV cho Patient
-- ==========================================================================

SET SERVEROUTPUT ON;

BEGIN
    -- ==========================================================
    -- TẠO LUẬT (RULE) VÀ BỘ LUẬT (RULE SET)
    -- ==========================================================
    
    -- Tạo Rule kiểm tra giờ hành chính (8h - 17h)
    DVSYS.DBMS_MACADM.CREATE_RULE(
        rule_name => 'Rule_Check_Time',
        rule_expr => 'TO_NUMBER(TO_CHAR(SYSDATE, ''HH24'')) BETWEEN 8 AND 17'
    );

    -- Tạo Rule Set
    DVSYS.DBMS_MACADM.CREATE_RULE_SET(
        rule_set_name => 'RS_Working_Hours', 
        description   => 'Gio han truy cap gio hanh chinh',
        enabled       => DBMS_MACUTL.G_YES,
        eval_options  => DBMS_MACUTL.G_RULESET_EVAL_ALL,
        fail_options  => DBMS_MACUTL.G_RULESET_FAILED_QUIET,
        fail_message  => 'Truy cap bi tu choi: Ngoai gio hanh chinh (8h-17h)',
        fail_code     => 20400
    );

    -- Gắn Rule vào Rule Set
    DVSYS.DBMS_MACADM.ADD_RULE_TO_RULE_SET(
        rule_set_name => 'RS_Working_Hours',
        rule_name     => 'Rule_Check_Time'
    );

    -- ==========================================================
    --  TẠO VÙNG BẢO MẬT (REALM)
    -- ==========================================================
    
    -- Tạo Realm bảo vệ bảng PATIENT
    DVSYS.DBMS_MACADM.CREATE_REALM(
        realm_name    => 'Realm_Patient_Security',
        description   => 'Bao ve nghiem ngat ho so benh nhan',
        enabled       => DBMS_MACUTL.G_YES, 
        audit_options => DBMS_MACUTL.G_REALM_AUDIT_OFF
    );

    -- Nâng cấp lên chế độ MANDATORY (Thiết quân luật)
    DVSYS.DBMS_MACADM.UPDATE_REALM(
        realm_name    => 'Realm_Patient_Security',
        realm_type    => 1 -- 1 = Mandatory Realm
    );

    -- ==========================================================
    --  ĐƯA ĐỐI TƯỢNG VÀO REALM
    -- ==========================================================
    
    DVSYS.DBMS_MACADM.ADD_OBJECT_TO_REALM(
        realm_name   => 'Realm_Patient_Security',
        object_owner => 'HOSPITAL_ADMIN', 
        object_name  => 'PATIENT',        
        object_type  => 'TABLE'
    );

    -- ==========================================================
    --  ỦY QUYỀN TRUY CẬP (AUTHORIZATION)
    -- ==========================================================

    -- A. Bác sĩ: Chỉ được vào trong giờ hành chính
    DVSYS.DBMS_MACADM.ADD_AUTH_TO_REALM(
        realm_name    => 'Realm_Patient_Security',
        grantee       => 'DOCTOR_ROLE',
        rule_set_name => 'RS_Working_Hours' 
    );
    
    -- B. Y tá: Chỉ được vào trong giờ hành chính
    DVSYS.DBMS_MACADM.ADD_AUTH_TO_REALM(
        realm_name    => 'Realm_Patient_Security',
        grantee       => 'NURSE_ROLE',
        rule_set_name => 'RS_Working_Hours'
    );

    -- C. HOSPITAL_ADMIN: Được vào tự do (Không gán Rule Set)
    DVSYS.DBMS_MACADM.ADD_AUTH_TO_REALM(
        realm_name    => 'Realm_Patient_Security',
        grantee       => 'HOSPITAL_ADMIN' 
    );

    COMMIT;
    DBMS_OUTPUT.PUT_LINE('--- Da thiet lap thanh cong Realm va Rule Set cho bang PATIENT ---');
END;
/
-- ==========================================================================
-- Cài đặt ODV cho MEDICINE, PRESCRIPTION, PRESCRIPTION_DETAIL
-- ==========================================================================
BEGIN
    DVSYS.DBMS_MACADM.CREATE_RULE(
        rule_name => 'Luat_Gio_Lam_Viec',
        rule_expr => 'TO_NUMBER(TO_CHAR(SYSDATE, ''HH24'')) BETWEEN 8 AND 17'
    );
END;
/

BEGIN
    DVSYS.DBMS_MACADM.CREATE_RULE_SET(
        rule_set_name => 'Bo_Luat_Gio_Gioi_Nghiem',
        description   => 'Chỉ cho phép truy cập trong giờ hành chính',
        enabled       => 'y',
        eval_options  => 1, 
        fail_options  => 1, 
        fail_message  => 'Loi: Truy cap bi TU CHOI vi ngoai gio lam viec (8h-17h)!',
        fail_code     => 20005
    );
END;
/


BEGIN
    DVSYS.DBMS_MACADM.ADD_RULE_TO_RULE_SET(
        rule_set_name => 'Bo_Luat_Gio_Gioi_Nghiem',
        rule_name     => 'Luat_Gio_Lam_Viec'
    );
END;
/



BEGIN
    DVSYS.DBMS_MACADM.CREATE_REALM(
        realm_name    => 'Realm_BaoVe_DuLieu_BenhVien',
        description   => 'Ngan SYS truy cap du lieu thuoc',
        enabled       => 'y',
        audit_options => 0
    );
END;
/


BEGIN
    DVSYS.DBMS_MACADM.ADD_OBJECT_TO_REALM(
        realm_name   => 'Realm_BaoVe_DuLieu_BenhVien', 
        object_owner => 'HOSPITAL_ADMIN', 
        object_name  => 'MEDICINE', 
        object_type  => 'TABLE'
    );
    
    DVSYS.DBMS_MACADM.ADD_OBJECT_TO_REALM(
        realm_name   => 'Realm_BaoVe_DuLieu_BenhVien', 
        object_owner => 'HOSPITAL_ADMIN', 
        object_name  => 'PRESCRIPTION', 
        object_type  => 'TABLE'
    );
    
    DVSYS.DBMS_MACADM.ADD_OBJECT_TO_REALM(
        realm_name   => 'Realm_BaoVe_DuLieu_BenhVien', 
        object_owner => 'HOSPITAL_ADMIN', 
        object_name  => 'PRESCRIPTION_DETAIL', 
        object_type  => 'TABLE'
    );
END;
/
BEGIN
    DVSYS.DBMS_MACADM.ADD_AUTH_TO_REALM(
        realm_name => 'Realm_BaoVe_DuLieu_BenhVien',
        grantee    => 'HOSPITAL_ADMIN'
    );
END;
/
BEGIN
    DVSYS.DBMS_MACADM.ENABLE_DV;
END;
/

SELECT command, object_owner, object_name, rule_set_name, enabled
FROM dba_dv_command_rule
WHERE object_name IN ('MEDICINE', 'PRESCRIPTION');

SELECT rule_set_name, rule_name 
FROM dba_dv_rule_set_rule
WHERE rule_set_name = 'Bo_Luat_Gio_Gioi_Nghiem';


-------------------------KiemTraIP--------------

BEGIN
    DVSYS.DBMS_MACADM.CREATE_RULE(
        rule_name => 'Luat_IP_Localhost',
        rule_expr => 'SYS_CONTEXT(''USERENV'', ''IP_ADDRESS'') IN (''127.0.0.1'', ''::1'')'
    );
END;
/


BEGIN
    DVSYS.DBMS_MACADM.CREATE_RULE_SET(
        rule_set_name => 'Bo_Luat_Bao_Mat_IP',
        description   => 'Chan truy cap tu may tinh la',
        enabled       => 'y',
        eval_options  => 1,
        fail_options  => 1,
        fail_message  => 'Truy cap bi TU CHOI! IP cua ban khong nam trong danh sach cho phep.',
        fail_code     => 20006
    );
END;
/

BEGIN
    DVSYS.DBMS_MACADM.ADD_RULE_TO_RULE_SET(
        rule_set_name => 'Bo_Luat_Bao_Mat_IP',
        rule_name     => 'Luat_IP_Localhost'
    );
END;
/

BEGIN
    -- 1. Bảng MEDICINE
    DVSYS.DBMS_MACADM.CREATE_COMMAND_RULE(command       => 'SELECT',
        object_owner  => 'HOSPITAL_ADMIN',
        object_name   => 'MEDICINE',
        rule_set_name => 'Bo_Luat_Bao_Mat_IP',
        enabled       => 'y'
    );

    -- 2. Bảng PRESCRIPTION
    DVSYS.DBMS_MACADM.CREATE_COMMAND_RULE(
        command       => 'SELECT',
        object_owner  => 'HOSPITAL_ADMIN',
        object_name   => 'PRESCRIPTION',
        rule_set_name => 'Bo_Luat_Bao_Mat_IP',
        enabled       => 'y'
    );

    -- 3. Bảng PRESCRIPTION_DETAIL
    DVSYS.DBMS_MACADM.CREATE_COMMAND_RULE(
        command       => 'SELECT',
        object_owner  => 'HOSPITAL_ADMIN',
        object_name   => 'PRESCRIPTION_DETAIL',
        rule_set_name => 'Bo_Luat_Bao_Mat_IP',
        enabled       => 'y'
    );
END;
/
BEGIN
    -- 1. Tạo Rule Set mới
    DVSYS.DBMS_MACADM.CREATE_RULE_SET(
        rule_set_name => 'Bo_Luat_Tong_Hop_IP_Time',
        description   => 'Bat buoc: Dung IP VA Dung Gio lam viec',
        enabled       => 'y',
        eval_options  => 1, -- AND (Phải thỏa mãn TẤT CẢ các luật)
        fail_options  => 1,
        fail_message  => 'Truy cap bi CHAN! Ban vi pham Gio lam viec hoac Sai dia chi IP.',
        fail_code     => 20007
    );

    DVSYS.DBMS_MACADM.ADD_RULE_TO_RULE_SET(
        rule_set_name => 'Bo_Luat_Tong_Hop_IP_Time',
        rule_name     => 'Luat_Gio_Lam_Viec' 
    );

    -- 3. Thêm luật IP 
    DVSYS.DBMS_MACADM.ADD_RULE_TO_RULE_SET(
        rule_set_name => 'Bo_Luat_Tong_Hop_IP_Time',
        rule_name     => 'Luat_IP_Localhost'  
    );
END;
/

BEGIN
    -- 1. Cập nhật cho bảng MEDICINE
    DVSYS.DBMS_MACADM.UPDATE_COMMAND_RULE(
        command       => 'SELECT',
        object_owner  => 'HOSPITAL_ADMIN',
        object_name   => 'MEDICINE',
        rule_set_name => 'Bo_Luat_Tong_Hop_IP_Time', -- Trỏ sang bộ luật mới
        enabled       => 'y'
    );

    -- 2. Cập nhật cho bảng PRESCRIPTION
    DVSYS.DBMS_MACADM.UPDATE_COMMAND_RULE(
        command       => 'SELECT',
        object_owner  => 'HOSPITAL_ADMIN',
        object_name   => 'PRESCRIPTION',
        rule_set_name => 'Bo_Luat_Tong_Hop_IP_Time',
        enabled       => 'y'
    );

    -- 3. Cập nhật cho bảng PRESCRIPTION_DETAIL
    DVSYS.DBMS_MACADM.UPDATE_COMMAND_RULE(
        command       => 'SELECT',
        object_owner  => 'HOSPITAL_ADMIN',
        object_name   => 'PRESCRIPTION_DETAIL',
        rule_set_name => 'Bo_Luat_Tong_Hop_IP_Time',
        enabled       => 'y'
    );
END;
/


BEGIN
    DVSYS.DBMS_MACADM.UPDATE_RULE(
        rule_name => 'Luat_IP_Localhost',
        rule_expr => 'SYS_CONTEXT(''USERENV'', ''IP_ADDRESS'') = ''1.2.3.4''' 
    );
END;
/
BEGIN
    DVSYS.DBMS_MACADM.UPDATE_RULE(
        rule_name => 'Luat_IP_Localhost',
        rule_expr => 'SYS_CONTEXT(''USERENV'', ''IP_ADDRESS'') = ''127.0.0.1''' 
    );
END;
