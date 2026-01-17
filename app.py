# app.py
import pymysql
from pymysql.cursors import DictCursor
from flask import Flask, request, redirect, url_for, render_template, flash
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Load secret key from environment
app.secret_key = os.environ.get('FLASK_SECRET', 'a-default-fallback-key')

# DB config loaded from environment variables
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASS'),
    'db': os.environ.get('DB_NAME', 'student_results'),
    'cursorclass': DictCursor,
    'autocommit': False  # IMPORTANT: We will manage transactions manually
}

# ---------------------- DB HELPER FUNCTIONS ----------------------
# These functions manage connections and separate DB logic from routes

def get_conn():
    """Establishes a new database connection."""
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        # In a real app, you'd log this error
        print(f"Error connecting to database: {e}")
        return None

def db_query(sql, args=None, fetchone=False):
    """Runs a SELECT query and returns data."""
    conn = get_conn()
    if not conn:
        return None if fetchone else []
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            if fetchone:
                result = cur.fetchone()
            else:
                result = cur.fetchall()
            return result
    except Exception as e:
        flash(f"Database query error: {e}", "danger")
        return None if fetchone else []
    finally:
        if conn:
            conn.close()

def db_execute(sql, args=None):
    """Runs an INSERT, UPDATE, or DELETE query."""
    conn = get_conn()
    if not conn:
        flash("Database connection failed.", "danger")
        return False
        
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
        conn.commit()  # Manually commit the transaction
        return True
    except pymysql.err.IntegrityError as e:
        conn.rollback()  # Roll back on integrity error (e.g., duplicate key)
        flash(f"Error: {e}", "warning")
        return False
    except Exception as e:
        conn.rollback()  # Roll back on any other error
        flash(f"Database execution error: {e}", "danger")
        return False
    finally:
        if conn:
            conn.close()

# ---------------------- ROUTES ----------------------

@app.route('/')
def index():
    # This route now just renders the index.html template
    return render_template("index.html")


@app.route('/students', methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        roll_no = request.form['roll_no'].strip()
        name = request.form['name'].strip()
        cls = request.form.get('class', '').strip()
        
        sql = "INSERT INTO student (roll_no, name, class) VALUES (%s,%s,%s)"
        if db_execute(sql, (roll_no, name, cls)):
            flash('Student added.', 'success')
        
        return redirect(url_for('students'))

    # GET Request
    students_list = db_query("SELECT * FROM student ORDER BY student_id")
    return render_template("students.html", students_list=students_list)


@app.route('/subjects', methods=['GET', 'POST'])
def subjects():
    if request.method == 'POST':
        name = request.form['name'].strip()
        try:
            max_marks = int(request.form.get('max_marks', 100))
        except ValueError:
            flash("Invalid max marks. Must be a number.", "danger")
            return redirect(url_for('subjects'))

        sql = "INSERT INTO subject (name, max_marks) VALUES (%s,%s)"
        if db_execute(sql, (name, max_marks)):
            flash('Subject added.', 'success')

        return redirect(url_for('subjects'))

    # GET Request
    subjects_list = db_query("SELECT * FROM subject ORDER BY subject_id")
    return render_template("subjects.html", subjects_list=subjects_list)


@app.route('/enter_marks', methods=['GET', 'POST'])
def enter_marks():
    if request.method == 'POST':
        try:
            student_id = int(request.form['student_id'])
            subject_id = int(request.form['subject_id'])
            marks = int(request.form['marks'])
        except ValueError:
            flash("Invalid input. Please enter numbers.", "danger")
            return redirect(url_for('enter_marks'))

        sql = """
        INSERT INTO result (student_id, subject_id, marks) VALUES (%s,%s,%s)
        ON DUPLICATE KEY UPDATE marks = VALUES(marks)
        """
        if db_execute(sql, (student_id, subject_id, marks)):
            flash('Marks saved.', 'success')
        
        return redirect(url_for('enter_marks'))
    
    # GET Request
    students_list = db_query("SELECT * FROM student")
    subjects_list = db_query("SELECT * FROM subject")
    return render_template("enter_marks.html", students_list=students_list, subjects_list=subjects_list)


@app.route('/results/<int:student_id>')
def view_results(student_id):
    student = db_query("SELECT * FROM student WHERE student_id=%s", (student_id,), fetchone=True)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for('students'))

    sql = """
      SELECT r.result_id, s.name AS subject_name, r.marks, s.max_marks
      FROM result r
      JOIN subject s ON r.subject_id = s.subject_id
      WHERE r.student_id=%s
      ORDER BY s.subject_id
    """
    rows_list = db_query(sql, (student_id,))
    
    total_marks = sum([r['marks'] for r in rows_list]) if rows_list else 0
    total_max = sum([r['max_marks'] for r in rows_list]) if rows_list else 0
    
    # Call the (improved) grade function
    grade_result = db_query("SELECT compute_grade(%s, %s) AS grade", (total_marks, total_max), fetchone=True)
    grade = grade_result.get('grade', 'N/A') if grade_result else 'Error'

    return render_template("view_results.html", 
                           student=student, 
                           rows_list=rows_list, 
                           total_marks=total_marks, 
                           total_max=total_max, 
                           grade=grade)


if __name__ == '__main__':
    # Set debug=False for production
    app.run(debug=True, port=5000)