BEGIN
    SA_SYSDBA.CREATE_POLICY (
        policy_name => 'HOSPITAL_OLS',
        column_name => 'OLS_COLUMN'
    );
END;
GRANT HOSPITAL_OLS_DBA TO hospital_admin;
GRANT execute ON sa_components TO hospital_admin; 
GRANT execute ON sa_label_admin TO hospital_admin; 
GRANT execute ON sa_policy_admin TO hospital_admin; 
GRANT execute ON sa_user_admin TO hospital_admin;
GRANT EXECUTE ON LBACSYS.TO_LBAC_DATA_LABEL TO hospital_admin;
