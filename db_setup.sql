-- 1. Create DB
CREATE DATABASE IF NOT EXISTS student_results;
USE student_results;

-- 2. Students table
CREATE TABLE IF NOT EXISTS student (
  student_id INT AUTO_INCREMENT PRIMARY KEY,
  roll_no VARCHAR(30) NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  class VARCHAR(50)
);

-- 3. Subjects table
CREATE TABLE IF NOT EXISTS subject (
  subject_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  max_marks INT NOT NULL DEFAULT 100
);

-- 4. Results table
CREATE TABLE IF NOT EXISTS result (
  result_id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  subject_id INT NOT NULL,
  marks INT NOT NULL,
  CONSTRAINT fk_student FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
  CONSTRAINT fk_subject FOREIGN KEY (subject_id) REFERENCES subject(subject_id) ON DELETE CASCADE,
  UNIQUE KEY uq_student_subject (student_id, subject_id)
);

-- 5. Results audit table
CREATE TABLE IF NOT EXISTS results_audit (
  audit_id INT AUTO_INCREMENT PRIMARY KEY,
  result_id INT,
  action VARCHAR(20), -- 'UPDATE' or 'DELETE' or 'INSERT'
  old_marks INT,
  new_marks INT,
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  changed_by VARCHAR(50)
);

-- 6. Stored function to compute grade (IMPROVED)
-- Drops the old one if it exists, and creates a new one
-- that uses percentage, making it much more flexible.
DROP FUNCTION IF EXISTS compute_grade;
DELIMITER //
CREATE FUNCTION compute_grade(total_marks INT, max_total_marks INT) 
RETURNS VARCHAR(50)
DETERMINISTIC
BEGIN
  DECLARE g VARCHAR(50);
  DECLARE perc DECIMAL(5, 2); -- e.g., 95.50

  IF max_total_marks IS NULL OR max_total_marks = 0 THEN
    RETURN 'N/A';
  END IF;

  SET perc = (total_marks / max_total_marks) * 100;

  IF perc >= 90 THEN
    SET g = 'Distinction';
  ELSEIF perc >= 80 THEN
    SET g = 'First Class';
  ELSEIF perc >= 70 THEN
    SET g = 'Higher Second Class';
  ELSEIF perc >= 60 THEN
    SET g = 'Second Class';
  ELSEIF perc >= 40 THEN
    SET g = 'Pass';
  ELSE
    SET g = 'Fail';
  END IF;
  RETURN g;
END;
//
DELIMITTER ;

-- 7. Triggers (IMPROVED - Added INSERT trigger)
DROP TRIGGER IF EXISTS trg_result_insert;
DROP TRIGGER IF EXISTS trg_result_update;
DROP TRIGGER IF EXISTS trg_result_delete;

DELIMITER //
CREATE TRIGGER trg_result_insert
AFTER INSERT ON result
FOR EACH ROW
BEGIN
  INSERT INTO results_audit(result_id, action, old_marks, new_marks, changed_by)
  VALUES (NEW.result_id, 'INSERT', NULL, NEW.marks, USER());
END;
//
CREATE TRIGGER trg_result_update
BEFORE UPDATE ON result
FOR EACH ROW
BEGIN
  INSERT INTO results_audit(result_id, action, old_marks, new_marks, changed_by)
  VALUES (OLD.result_id, 'UPDATE', OLD.marks, NEW.marks, USER());
END;
//
CREATE TRIGGER trg_result_delete
BEFORE DELETE ON result
FOR EACH ROW
BEGIN
  INSERT INTO results_audit(result_id, action, old_marks, new_marks, changed_by)
  VALUES (OLD.result_id, 'DELETE', OLD.marks, NULL, USER());
END;
//
DELIMITER ;

-- 8. Insert sample subjects
-- Clear existing data to avoid conflicts if script is re-run
TRUNCATE TABLE subject;
INSERT INTO subject (name, max_marks) VALUES ('Mathematics',100),('Physics',100),('Chemistry',100),('Electronics',100),('Data Structures',100);

-- 9. Insert sample student and sample marks
-- Clear existing data to avoid conflicts if script is re-run
TRUNCATE TABLE student;
INSERT INTO student (roll_no, name, class) VALUES ('CE2019001','Sai Patel','SE-A'),('CE2019002','Asha Kumar','SE-A');

-- sample marks for Sai: 98,92,90,88,93
-- We clear results first, which also clears the audit log
TRUNCATE TABLE result;
TRUNCATE TABLE results_audit;
INSERT INTO result (student_id, subject_id, marks) VALUES (1,1,98),(1,2,92),(1,3,90),(1,4,88),(1,5,93);
INSERT INTO result (student_id, subject_id, marks) VALUES (2,1,78),(2,2,82),(2,3,80),(2,4,75),(2,5,85);