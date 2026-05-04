-- ============================================================
--  Library Management System — Full Migration Script v2
--  Compatible with MySQL 5.7+ and MySQL 8.0+
--  Run once in MySQL Workbench against library_db.
--  Safe to re-run — uses IGNORE and conditional logic.
-- ============================================================

USE library_db;

-- ─────────────────────────────────────────────────────────────
-- PROCEDURE: add a column only if it doesn't already exist
-- ─────────────────────────────────────────────────────────────
DROP PROCEDURE IF EXISTS add_column_if_missing;
DELIMITER $$
CREATE PROCEDURE add_column_if_missing(
    IN tbl   VARCHAR(64),
    IN col   VARCHAR(64),
    IN def   TEXT
)
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME   = tbl
          AND COLUMN_NAME  = col
    ) THEN
        SET @sql = CONCAT('ALTER TABLE `', tbl, '` ADD COLUMN `', col, '` ', def);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$
DELIMITER ;

-- ─────────────────────────────────────────────────────────────
--  TABLE: users
-- ─────────────────────────────────────────────────────────────
CALL add_column_if_missing('users', 'username',      'VARCHAR(80) DEFAULT NULL');
CALL add_column_if_missing('users', 'name',          'VARCHAR(100) NOT NULL DEFAULT ""');
CALL add_column_if_missing('users', 'password_hash', 'VARCHAR(512) DEFAULT NULL');
CALL add_column_if_missing('users', 'role',          'VARCHAR(20) NOT NULL DEFAULT "student"');
CALL add_column_if_missing('users', 'is_active',     'TINYINT(1) NOT NULL DEFAULT 1');
CALL add_column_if_missing('users', 'created_at',    'DATETIME DEFAULT CURRENT_TIMESTAMP');
CALL add_column_if_missing('users', 'updated_at',    'DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP');

-- Expand password_hash if it exists but is too short (VARCHAR(256) → VARCHAR(512))
ALTER TABLE users MODIFY COLUMN password_hash VARCHAR(512) DEFAULT NULL;

-- ─────────────────────────────────────────────────────────────
--  TABLE: notifications
-- ─────────────────────────────────────────────────────────────
CALL add_column_if_missing('notifications', 'user_id',    'INT NOT NULL DEFAULT 0');
CALL add_column_if_missing('notifications', 'title',      'VARCHAR(200) NOT NULL DEFAULT ""');
CALL add_column_if_missing('notifications', 'message',    'TEXT');
CALL add_column_if_missing('notifications', 'read',       'TINYINT(1) NOT NULL DEFAULT 0');
CALL add_column_if_missing('notifications', 'created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP');

-- ─────────────────────────────────────────────────────────────
--  TABLE: students
-- ─────────────────────────────────────────────────────────────
CALL add_column_if_missing('students', 'phone',         'VARCHAR(20) DEFAULT NULL');
CALL add_column_if_missing('students', 'address',       'TEXT');
CALL add_column_if_missing('students', 'department',    'VARCHAR(100) DEFAULT NULL');
CALL add_column_if_missing('students', 'photo',         'VARCHAR(255) DEFAULT NULL');
CALL add_column_if_missing('students', 'date_of_birth', 'DATE DEFAULT NULL');
CALL add_column_if_missing('students', 'gender',        'VARCHAR(10) DEFAULT NULL');
CALL add_column_if_missing('students', 'created_at',    'DATETIME DEFAULT CURRENT_TIMESTAMP');
CALL add_column_if_missing('students', 'updated_at',    'DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP');

-- ─────────────────────────────────────────────────────────────
--  TABLE: books
-- ─────────────────────────────────────────────────────────────
CALL add_column_if_missing('books', 'isbn',             'VARCHAR(20) DEFAULT NULL');
CALL add_column_if_missing('books', 'edition',          'VARCHAR(50) DEFAULT NULL');
CALL add_column_if_missing('books', 'description',      'TEXT');
CALL add_column_if_missing('books', 'cover_image',      'VARCHAR(255) DEFAULT NULL');
CALL add_column_if_missing('books', 'ebook',            'VARCHAR(255) DEFAULT NULL');
CALL add_column_if_missing('books', 'qr_code',          'VARCHAR(255) DEFAULT NULL');
CALL add_column_if_missing('books', 'barcode',          'VARCHAR(50) DEFAULT NULL');
CALL add_column_if_missing('books', 'price',            'FLOAT DEFAULT 0.0');
CALL add_column_if_missing('books', 'rack_number',      'VARCHAR(20) DEFAULT NULL');
CALL add_column_if_missing('books', 'total_copies',     'INT DEFAULT 1');
CALL add_column_if_missing('books', 'available_copies', 'INT DEFAULT 1');
CALL add_column_if_missing('books', 'created_at',       'DATETIME DEFAULT CURRENT_TIMESTAMP');
CALL add_column_if_missing('books', 'updated_at',       'DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP');

-- ─────────────────────────────────────────────────────────────
--  TABLE: issued_books
-- ─────────────────────────────────────────────────────────────
CALL add_column_if_missing('issued_books', 'notes',      'TEXT');
CALL add_column_if_missing('issued_books', 'issued_by',  'INT DEFAULT NULL');
CALL add_column_if_missing('issued_books', 'created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP');
CALL add_column_if_missing('issued_books', 'updated_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP');

-- ─────────────────────────────────────────────────────────────
--  TABLE: fines
-- ─────────────────────────────────────────────────────────────
CALL add_column_if_missing('fines', 'reason',     'TEXT');
CALL add_column_if_missing('fines', 'paid',       'TINYINT(1) NOT NULL DEFAULT 0');
CALL add_column_if_missing('fines', 'created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP');

-- ─────────────────────────────────────────────────────────────
--  TABLE: reservations
-- ─────────────────────────────────────────────────────────────
CALL add_column_if_missing('reservations', 'reservation_date',  'DATETIME DEFAULT CURRENT_TIMESTAMP');
CALL add_column_if_missing('reservations', 'expiry_date',       'DATE DEFAULT NULL');
CALL add_column_if_missing('reservations', 'status',            'VARCHAR(20) DEFAULT "pending"');
CALL add_column_if_missing('reservations', 'notification_sent', 'TINYINT(1) NOT NULL DEFAULT 0');

-- ─────────────────────────────────────────────────────────────
--  TABLE: reading_history
-- ─────────────────────────────────────────────────────────────
CALL add_column_if_missing('reading_history', 'issue_date',  'DATE DEFAULT NULL');
CALL add_column_if_missing('reading_history', 'return_date', 'DATE DEFAULT NULL');
CALL add_column_if_missing('reading_history', 'borrowed_at', 'DATETIME DEFAULT NULL');
CALL add_column_if_missing('reading_history', 'returned_at', 'DATETIME DEFAULT NULL');

-- ─────────────────────────────────────────────────────────────
--  TABLE: authors
-- ─────────────────────────────────────────────────────────────
CALL add_column_if_missing('authors', 'biography',  'TEXT');
CALL add_column_if_missing('authors', 'country',    'VARCHAR(50) DEFAULT NULL');
CALL add_column_if_missing('authors', 'created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP');
CALL add_column_if_missing('authors', 'updated_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP');

-- ─────────────────────────────────────────────────────────────
--  TABLE: categories
-- ─────────────────────────────────────────────────────────────
CALL add_column_if_missing('categories', 'description', 'TEXT');
CALL add_column_if_missing('categories', 'created_at',  'DATETIME DEFAULT CURRENT_TIMESTAMP');
CALL add_column_if_missing('categories', 'updated_at',  'DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP');

-- ─────────────────────────────────────────────────────────────
--  TABLE: settings
-- ─────────────────────────────────────────────────────────────
CALL add_column_if_missing('settings', 'setting_key', 'VARCHAR(50) DEFAULT NULL');
CALL add_column_if_missing('settings', 'value',       'TEXT');
CALL add_column_if_missing('settings', 'created_at',  'DATETIME DEFAULT CURRENT_TIMESTAMP');
CALL add_column_if_missing('settings', 'updated_at',  'DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP');

-- ─────────────────────────────────────────────────────────────
--  Seed default settings (ignored if already exist)
-- ─────────────────────────────────────────────────────────────
INSERT IGNORE INTO settings (setting_key, value) VALUES
    ('library_name',            'BiblioSystem'),
    ('loan_period_days',        '14'),
    ('max_books_per_student',   '3'),
    ('fine_per_day',            '0.50'),
    ('reservation_expiry_days', '3'),
    ('currency',                'USD');

-- Seed default authors for admin book form choices
INSERT IGNORE INTO authors (name, biography, country) VALUES
    ('Stuart Russell', 'Computer scientist and co-author of Artificial Intelligence: A Modern Approach.', 'United Kingdom'),
    ('Peter Norvig', 'Computer scientist and co-author of Artificial Intelligence: A Modern Approach.', 'United States');

-- Seed default categories for admin book form choices
INSERT IGNORE INTO categories (name, description) VALUES
    ('Artificial Intelligence', 'Books about AI, machine learning, and intelligent systems.'),
    ('Computer Science', 'Core computer science topics including algorithms, programming, and systems.'),
    ('Software Engineering', 'Books about software design, development practices, and project architecture.'),
    ('Data Science', 'Books covering data analysis, statistics, and data-driven applications.'),
    ('Information Technology', 'General IT infrastructure, networking, systems, and administration topics.');

-- ─────────────────────────────────────────────────────────────
--  Clean up the helper procedure
-- ─────────────────────────────────────────────────────────────
DROP PROCEDURE IF EXISTS add_column_if_missing;

-- ─────────────────────────────────────────────────────────────
--  Confirm: show all tables with their column count
-- ─────────────────────────────────────────────────────────────
SELECT
    TABLE_NAME         AS `Table`,
    COUNT(COLUMN_NAME) AS `Columns`
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
GROUP BY TABLE_NAME
ORDER BY TABLE_NAME;

SELECT 'Migration complete. All columns verified.' AS Result;
