EXEC sa_components.create_level('HOSPITAL_OLS', 1000, 'PUB',  'NEW_VISIT');
EXEC sa_components.create_level('HOSPITAL_OLS', 2000, 'CONF', 'IN_PROGRESS');
EXEC sa_components.create_level('HOSPITAL_OLS', 3000, 'SEC',  'DIAGNOSED');

EXEC sa_components.create_compartment('HOSPITAL_OLS', 10, 'INT', 'Internal Medicine');
EXEC sa_components.create_compartment('HOSPITAL_OLS', 20, 'SUR', 'Surgery');
EXEC sa_components.create_compartment('HOSPITAL_OLS', 30, 'PED', 'Pediatrics');
EXEC sa_components.create_compartment('HOSPITAL_OLS', 40, 'ER', 'Emergency');
EXEC sa_components.create_compartment('HOSPITAL_OLS', 50, 'ADM', 'Administration');

EXEC sa_components.create_group('HOSPITAL_OLS', 1, 'CLI', 'Clinical');

BEGIN
    sa_user_admin.set_user_labels (
        policy_name => 'HOSPITAL_OLS',
        user_name => 'NURSE_TU',
        max_read_label => 'PUB:INT,SUR,PED,ER,ADM:CLI',
        max_write_label => 'PUB:INT,SUR,PED,ER,ADM:CLI',
        def_label => 'PUB:INT,SUR,PED,ER,ADM:CLI',
        row_label => 'PUB:INT,SUR,PED,ER,ADM:CLI'
    );
END;

BEGIN
    sa_user_admin.set_user_labels (
        policy_name => 'HOSPITAL_OLS',
        user_name => 'DOCTOR_AN',
        max_read_label => 'SEC:INT:CLI',
        max_write_label => 'SEC:INT:CLI',
        def_label => 'SEC:INT:CLI',
        row_label => 'SEC:INT:CLI'
    );
END;

BEGIN
    sa_user_admin.set_user_labels (
        policy_name => 'HOSPITAL_OLS',
        user_name => 'ADMIN01',
        max_read_label => 'SEC:INT,SUR,PED,ER,ADM:CLI',
        max_write_label => 'SEC:INT,SUR,PED,ER,ADM:CLI',
        def_label => 'SEC:INT,SUR,PED,ER,ADM:CLI',
        row_label => 'SEC:INT,SUR,PED,ER,ADM:CLI'
    );
END;

BEGIN 
    sa_user_admin.set_user_privs (
        policy_name => 'HOSPITAL_OLS',
        user_name => 'HOSPITAL_ADMIN',
        PRIVILEGES => 'FULL'
    );
END;

CREATE OR REPLACE FUNCTION hospital_admin.gen_visit_label (
    p_department_id NUMBER,
    p_diagnosis CLOB,
    p_staffid NUMBER
) RETURN LBACSYS.LBAC_LABEL
AS
    v_label VARCHAR2(100);
BEGIN
    IF p_staffid IS NULL THEN
        v_label := 'PUB:';
    ELSIF p_diagnosis IS NULL THEN
        v_label := 'CONF:';
    ELSE
        v_label := 'SEC:';
    END IF;

    CASE p_department_id
        WHEN 1 THEN v_label := v_label || 'INT';
        WHEN 2 THEN v_label := v_label || 'SUR';
        WHEN 3 THEN v_label := v_label || 'PED';
        WHEN 4 THEN v_label := v_label || 'ER';
        ELSE v_label := v_label || 'ADM';
    END CASE;

    v_label := v_label || ':CLI';

    RETURN TO_LBAC_DATA_LABEL('HOSPITAL_OLS', v_label);
END;

GRANT execute ON hospital_admin.gen_visit_label TO lbacsys;

GRANT EXECUTE ON hospital_admin.gen_visit_label TO LBAC_TRIGGER;

BEGIN
    sa_policy_admin.apply_table_policy (
        policy_name => 'HOSPITAL_OLS',
        schema_name => 'HOSPITAL_ADMIN',
        table_name => 'VISIT',
        table_options => 'HIDE,NO_CONTROL'
    );
END;

-- Khoa Nội
UPDATE visit
SET ols_column = char_to_label('HOSPITAL_OLS', 'SEC:INT:CLI')
WHERE department_id = 1;

-- Khoa Ngoại
UPDATE visit
SET ols_column = char_to_label('HOSPITAL_OLS', 'SEC:SUR:CLI')
WHERE department_id = 2;

-- Khoa Nhi
UPDATE visit
SET ols_column = char_to_label('HOSPITAL_OLS', 'SEC:PED:CLI')
WHERE department_id = 3;

-- Khoa Cấp cứu
UPDATE visit
SET ols_column = char_to_label('HOSPITAL_OLS', 'SEC:ER:CLI')
WHERE department_id = 4;

-- Hành chính (nếu có)
UPDATE visit
SET ols_column = char_to_label('HOSPITAL_OLS', 'SEC:ADM:CLI')
WHERE department_id = 5;

COMMIT;

BEGIN 
    sa_policy_admin.remove_table_policy (
        policy_name => 'HOSPITAL_OLS',
        schema_name => 'HOSPITAL_ADMIN',
        table_name => 'VISIT'
    ); 
    
    sa_policy_admin.apply_table_policy (
        policy_name => 'HOSPITAL_OLS',
        schema_name => 'HOSPITAL_ADMIN',
        table_name => 'VISIT',
        table_options => 'HIDE,READ_CONTROL,WRITE_CONTROL,CHECK_CONTROL',
        label_function => 'hospital_admin.gen_visit_label(:new.department_id, :new.diagnosis, :new.staff_id)'
    ); 
END;

