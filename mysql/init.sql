CREATE DATABASE IF NOT EXISTS lms_db;

CREATE USER IF NOT EXISTS 'lms_user'@'%' IDENTIFIED BY 'lms_password';

-- Normal DB access
GRANT ALL PRIVILEGES ON lms_db.* TO 'lms_user'@'%';

-- 🔥 VERY IMPORTANT (fixes your CI)
GRANT ALL PRIVILEGES ON *.* TO 'lms_user'@'%' WITH GRANT OPTION;

FLUSH PRIVILEGES;