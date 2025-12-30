-- Fine-grained Auditing
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

SELECT
    dbusername, 
    sql_text, 
    fga_policy_name, 
    object_name 
FROM UNIFIED_AUDIT_TRAIL 
WHERE fga_policy_name = 'FGA_VISIT_NO_DIAGNOSIS' 
ORDER BY event_timestamp DESC;

-- Unified Auditing
CREATE AUDIT POLICY aud_insert_update_hospital_admin_department
ACTIONS INSERT, UPDATE ON hospital_admin.department;

AUDIT POLICY aud_insert_update_hospital_admin_department;

SELECT
    dbusername, 
    sql_text, 
    fga_policy_name, 
    object_name 
FROM UNIFIED_AUDIT_TRAIL
ORDER BY event_timestamp DESC;
