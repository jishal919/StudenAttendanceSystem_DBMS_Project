# MySQL Commands Reference
## Student Attendance Management System

---

## 🔌 Connect to Database

```sql
-- Open MySQL
mysql -u root -p

-- Select the database
USE attendance_db;
```

---

## 📊 Dashboard — Stats

```sql
-- Total students
SELECT COUNT(*) AS total_students FROM student;

-- Total subjects
SELECT COUNT(*) AS total_subjects FROM subject;

-- Total classes recorded
SELECT COUNT(*) AS total_classes FROM attendance;

-- Overall attendance percentage
SELECT ROUND((SUM(status = 'Present') / COUNT(*)) * 100, 1) AS avg_percentage
FROM attendance;

-- Recent 5 attendance entries
SELECT s.name AS student_name, sub.subject_name, a.date, a.status
FROM attendance a
JOIN student s   ON a.student_id = s.student_id
JOIN subject sub ON a.subject_id = sub.subject_id
ORDER BY a.att_id DESC
LIMIT 5;
```

---

## 👥 Students Page

```sql
-- View all students
SELECT * FROM student ORDER BY department, semester, name;

-- Add a new student
INSERT INTO student VALUES (108, 'Student Name', 'CSE', 4);

-- Delete a student (removes their attendance records too)
DELETE FROM attendance WHERE student_id = 108;
DELETE FROM student WHERE student_id = 108;

-- Search student by name
SELECT * FROM student WHERE name LIKE '%Rahul%';

-- Students by department
SELECT * FROM student WHERE department = 'CSE';

-- Students by semester
SELECT * FROM student WHERE semester = 4;
```

---

## ✅ Mark Attendance Page

```sql
-- View all subjects with faculty name
SELECT s.*, f.name AS faculty_name
FROM subject s
JOIN faculty f ON s.faculty_id = f.faculty_id;

-- View all students (to display the list)
SELECT * FROM student ORDER BY name;

-- Mark a single student Present
INSERT INTO attendance (student_id, subject_id, date, status)
VALUES (101, 1, '2026-03-20', 'Present');

-- Mark a single student Absent
INSERT INTO attendance (student_id, subject_id, date, status)
VALUES (101, 1, '2026-03-20', 'Absent');

-- Mark entire class as Absent for a subject and date
CALL mark_attendance_class(1, '2026-03-20');

-- Check if attendance already exists for a student on a date
SELECT status FROM attendance
WHERE student_id = 101
  AND subject_id = 1
  AND date = '2026-03-20';

-- Update attendance if already marked
UPDATE attendance
SET status = 'Present'
WHERE student_id = 101
  AND subject_id = 1
  AND date = '2026-03-20';
```

---

## 📋 Reports Page

```sql
-- Full attendance report (all students, all subjects)
SELECT
    s.student_id,
    s.name        AS student_name,
    s.department,
    sub.subject_name,
    SUM(a.status = 'Present')                          AS presents,
    SUM(a.status = 'Absent')                           AS absents,
    COUNT(*)                                           AS total_classes,
    ROUND((SUM(a.status = 'Present') / COUNT(*)) * 100, 1) AS percentage
FROM attendance a
JOIN student s   ON a.student_id = s.student_id
JOIN subject sub ON a.subject_id = sub.subject_id
GROUP BY a.student_id, a.subject_id
ORDER BY s.name, sub.subject_name;

-- Filter by department
SELECT
    s.name, s.department, sub.subject_name,
    SUM(a.status = 'Present') AS presents,
    COUNT(*) AS total_classes,
    ROUND((SUM(a.status = 'Present') / COUNT(*)) * 100, 1) AS percentage
FROM attendance a
JOIN student s   ON a.student_id = s.student_id
JOIN subject sub ON a.subject_id = sub.subject_id
WHERE s.department = 'CSE'
GROUP BY a.student_id, a.subject_id;

-- Filter by subject
SELECT
    s.name, sub.subject_name,
    SUM(a.status = 'Present') AS presents,
    COUNT(*) AS total_classes,
    ROUND((SUM(a.status = 'Present') / COUNT(*)) * 100, 1) AS percentage
FROM attendance a
JOIN student s   ON a.student_id = s.student_id
JOIN subject sub ON a.subject_id = sub.subject_id
WHERE a.subject_id = 1
GROUP BY a.student_id;

-- Students below 75% attendance
SELECT
    s.name, sub.subject_name,
    ROUND((SUM(a.status = 'Present') / COUNT(*)) * 100, 1) AS percentage
FROM attendance a
JOIN student s   ON a.student_id = s.student_id
JOIN subject sub ON a.subject_id = sub.subject_id
GROUP BY a.student_id, a.subject_id
HAVING percentage < 75
ORDER BY percentage ASC;

-- Attendance summary using the view
SELECT * FROM attendance_summary;
```

---

## 🗂️ Manage Subjects / Faculty / Courses

```sql
-- View all
SELECT * FROM faculty;
SELECT * FROM course;
SELECT * FROM subject;

-- Add faculty
INSERT INTO faculty VALUES (8, 'Prof. New Name', 'CSE');

-- Add course
INSERT INTO course VALUES (3, 'B.Tech IT');

-- Add subject
INSERT INTO subject VALUES (10, 'Artificial Intelligence', 1, 1);

-- Update faculty name
UPDATE faculty SET name = 'Prof. Updated Name' WHERE faculty_id = 1;

-- Update subject name
UPDATE subject SET subject_name = 'Advanced DBMS' WHERE subject_id = 5;

-- Delete subject (remove attendance first)
DELETE FROM attendance WHERE subject_id = 10;
DELETE FROM subject WHERE subject_id = 10;

-- Delete faculty (remove their subjects first)
DELETE FROM attendance WHERE subject_id IN (SELECT subject_id FROM subject WHERE faculty_id = 8);
DELETE FROM subject WHERE faculty_id = 8;
DELETE FROM faculty WHERE faculty_id = 8;
```

---

## 🧹 Reset / Cleanup

```sql
-- Clear all attendance records only
DELETE FROM attendance;

-- Full reset (keeps table structure, removes all data)
DELETE FROM attendance;
DELETE FROM subject;
DELETE FROM faculty;
DELETE FROM student;
DELETE FROM course;

-- Reset auto-increment counter
ALTER TABLE attendance AUTO_INCREMENT = 1;
```

---

## 🔍 Useful Checks

```sql
-- All departments
SELECT DISTINCT department FROM student ORDER BY department;

-- Attendance for a specific date
SELECT s.name, sub.subject_name, a.status
FROM attendance a
JOIN student s   ON a.student_id = s.student_id
JOIN subject sub ON a.subject_id = sub.subject_id
WHERE a.date = '2026-03-20';

-- Attendance for a specific student
SELECT sub.subject_name, a.date, a.status
FROM attendance a
JOIN subject sub ON a.subject_id = sub.subject_id
WHERE a.student_id = 101
ORDER BY a.date DESC;

-- Show all tables
SHOW TABLES;

-- Show table structure
DESCRIBE student;
DESCRIBE attendance;
```

---

> 💡 **Tip:** Always delete from `attendance` before deleting from `student` or `subject`
> to avoid foreign key constraint errors.