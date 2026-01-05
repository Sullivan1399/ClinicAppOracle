CREATE USER HOSPITAL_ADMIN IDENTIFIED BY hospitaladmin
DEFAULT TABLESPACE USERS
TEMPORARY TABLESPACE TEMP
QUOTA UNLIMITED ON USERS;

GRANT CONNECT, RESOURCE TO HOSPITAL_ADMIN;
GRANT DBA TO HOSPITAL_ADMIN;

GRANT admin_role TO HOSPITAL_ADMIN;
-- Cấp quyền thực thi các gói bảo mật
GRANT EXECUTE ON DBMS_RLS TO hospital_admin;
GRANT EXECUTE ON DBMS_FGA TO hospital_admin;
GRANT EXECUTE ON DBMS_SESSION TO hospital_admin;

-- Cấp quyền tạo Context và Trigger
GRANT CREATE ANY CONTEXT TO hospital_admin;
GRANT CREATE TRIGGER TO hospital_admin;
GRANT ADMINISTER DATABASE TRIGGER TO hospital_admin;
-- Cấp quyền đọc thông tin session (để hàm sys_context hoạt động tốt nhất)
GRANT SELECT ON V_$SESSION TO hospital_admin;

----------
-- ODV
--  Tạo User (DV Owner)
CREATE USER sec_admin_dv IDENTIFIED BY "Dinh_Hoa_123";
GRANT CREATE SESSION TO sec_admin_dv;
GRANT DV_OWNER TO sec_admin_dv;
GRANT AUDIT_ADMIN TO sec_admin_dv; 

-- Tạo User (Account Manager)
CREATE USER acct_mngr_dv IDENTIFIED BY "Dinh_Hoa_123";
GRANT CREATE SESSION TO acct_mngr_dv;
-- Trao quyền quản lý user 
GRANT DV_ACCTMGR TO acct_mngr_dv;

-----------------------------
-- User audit_mgr
-----------------------------
CREATE USER audit_mgr IDENTIFIED BY audit_mgr;
GRANT CREATE SESSION TO audit_mgr;
GRANT UNLIMITED TABLESPACE TO audit_mgr;
GRANT AUDIT_ADMIN TO audit_mgr;
GRANT AUDIT_VIEWER TO audit_mgr;
GRANT SELECT ON AUDSYS.UNIFIED_AUDIT_TRAIL TO audit_mgr;
BEGIN
    DBMS_MACADM.authorize_audit_admin('audit_mgr');
END;
/
BEGIN
  DBMS_MACADM.AUTHORIZE_AUDIT_VIEWER('audit_mgr');
END;
GRANT EXECUTE ON DBMS_FGA TO audit_mgr; 
GRANT EXECUTE ON DBMS_FGA TO hospital_admin; 
-- 2. Cấp quyền quản trị Audit hệ thống (Nếu chưa có) 
GRANT AUDIT_ADMIN TO audit_mgr; 
-- 3. Cấp quyền thực thi Procedure (Để FGA có thể gọi được Handler Module) 
GRANT EXECUTE ANY PROCEDURE TO audit_mgr;

