CREATE ROLE admin_role;
CREATE ROLE doctor_role;
CREATE ROLE nurse_role;

GRANT SELECT, INSERT, UPDATE ON staff TO admin_role;
GRANT SELECT, INSERT, UPDATE ON department TO admin_role;
GRANT SELECT ON visit TO admin_role;
GRANT SELECT ON staff TO doctor_role;
GRANT SELECT ON department TO doctor_role;
GRANT SELECT, UPDATE ON visit TO doctor_role;
GRANT SELECT ON staff TO nurse_role;
GRANT SELECT ON department TO nurse_role;
GRANT SELECT, INSERT, UPDATE ON visit TO nurse_role;

CREATE USER admin01 IDENTIFIED BY 123;
CREATE USER doctor_an IDENTIFIED BY 123;
CREATE USER nurse_tu IDENTIFIED BY 123;

GRANT admin_role TO admin01;
GRANT doctor_role TO doctor_an;
GRANT nurse_role TO nurse_tu;

GRANT CONNECT, RESOURCE TO admin01, doctor_an, nurse_tu;
ALTER USER admin01 QUOTA UNLIMITED ON users; 
ALTER USER doctor_an QUOTA UNLIMITED ON users; 
ALTER USER nurse_tu QUOTA UNLIMITED ON users;


