-- ============================================================
--  STUDENT ATTENDANCE MANAGEMENT SYSTEM — DATABASE SCHEMA
-- ============================================================

CREATE DATABASE IF NOT EXISTS attendance_db;
USE attendance_db;

-- ──────────────────────────────────────────
--  TABLES
-- ──────────────────────────────────────────

CREATE TABLE IF NOT EXISTS student (
    student_id  INT          PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    department  VARCHAR(50),
    semester    INT
);

CREATE TABLE IF NOT EXISTS faculty (
    faculty_id  INT          PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    department  VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS course (
    course_id   INT          PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS subject (
    subject_id   INT          PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    course_id    INT,
    faculty_id   INT,
    FOREIGN KEY (course_id)  REFERENCES course(course_id),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
);

CREATE TABLE IF NOT EXISTS attendance (
    att_id     INT  PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    subject_id INT,
    date       DATE,
    status     ENUM('Present', 'Absent'),
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (subject_id) REFERENCES subject(subject_id)
);

-- ──────────────────────────────────────────
--  VIEW — Attendance Summary
-- ──────────────────────────────────────────

CREATE OR REPLACE VIEW attendance_summary AS
SELECT
    student_id,
    subject_id,
    SUM(status = 'Present') AS presents,
    SUM(status = 'Absent')  AS absents
FROM attendance
GROUP BY student_id, subject_id;

-- ──────────────────────────────────────────
--  TRIGGER — Prevent Duplicate Attendance
-- ──────────────────────────────────────────

DROP TRIGGER IF EXISTS prevent_duplicate_attendance;

DELIMITER //
CREATE TRIGGER prevent_duplicate_attendance
BEFORE INSERT ON attendance
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM attendance
        WHERE student_id = NEW.student_id
          AND subject_id = NEW.subject_id
          AND date       = NEW.date
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Attendance already recorded for this student on this date';
    END IF;
END;//
DELIMITER ;

-- ──────────────────────────────────────────
--  STORED PROCEDURE — Mark Whole Class
-- ──────────────────────────────────────────

DROP PROCEDURE IF EXISTS mark_attendance_class;

DELIMITER //
CREATE PROCEDURE mark_attendance_class(
    IN p_subject_id INT,
    IN p_date       DATE
)
BEGIN
    INSERT INTO attendance (student_id, subject_id, date, status)
    SELECT student_id, p_subject_id, p_date, 'Absent'
    FROM student;
END;//
DELIMITER ;

-- ──────────────────────────────────────────
--  SAMPLE DATA
-- ──────────────────────────────────────────

-- Faculty
INSERT IGNORE INTO faculty VALUES (1, 'Prof. Akhila',       'CSE');
INSERT IGNORE INTO faculty VALUES (2, 'Prof. Shivakumar',   'CSE');
INSERT IGNORE INTO faculty VALUES (3, 'Prof. Saju Shankar', 'CSE');
INSERT IGNORE INTO faculty VALUES (4, 'Prof. Saleema',      'CSE');
INSERT IGNORE INTO faculty VALUES (5, 'Prof. Deepa',        'CSE');
INSERT IGNORE INTO faculty VALUES (6, 'Prof. Lekshmi',      'CSE');
INSERT IGNORE INTO faculty VALUES (7, 'Prof. Lajitha',      'CSE');

-- Courses
INSERT IGNORE INTO course VALUES (1, 'B.Tech CSE');
INSERT IGNORE INTO course VALUES (2, 'B.Tech ECE');

-- Subjects
INSERT IGNORE INTO subject VALUES (1, 'Mathematics',                          1, 1);
INSERT IGNORE INTO subject VALUES (2, 'Operating Systems',                    1, 2);
INSERT IGNORE INTO subject VALUES (3, 'Software Engineering',                 1, 3);
INSERT IGNORE INTO subject VALUES (4, 'Computer Organization & Architecture', 1, 4);
INSERT IGNORE INTO subject VALUES (5, 'Database Management Systems',          1, 5);
INSERT IGNORE INTO subject VALUES (6, 'Professional Ethics',                  1, 6);
INSERT IGNORE INTO subject VALUES (7, 'Skill Development',                    1, 7);
INSERT IGNORE INTO subject VALUES (8, 'Operating Systems Lab',                1, 4);
INSERT IGNORE INTO subject VALUES (9, 'Database Management Systems Lab',      1, 5);

-- Students
INSERT IGNORE INTO student VALUES (101, 'Rahul Sharma',    'CSE', 4);
INSERT IGNORE INTO student VALUES (102, 'Priya Nair',      'CSE', 4);
INSERT IGNORE INTO student VALUES (103, 'Arun Menon',      'CSE', 4);
INSERT IGNORE INTO student VALUES (104, 'Sneha Pillai',    'ECE', 3);
INSERT IGNORE INTO student VALUES (105, 'Vishnu Das',      'ECE', 3);
INSERT IGNORE INTO student VALUES (106, 'Anjali Krishnan', 'CSE', 4);
INSERT IGNORE INTO student VALUES (107, 'Mohammed Rafi',   'CSE', 4);