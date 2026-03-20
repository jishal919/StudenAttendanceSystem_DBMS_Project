from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import date

app = Flask(__name__)
app.secret_key = 'attendance_sys_secret_2025'

# ──────────────────────────────────────────
#  DATABASE CONFIG  ← change password here
# ──────────────────────────────────────────
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': '',          
    'database': 'attendance_db'
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# ──────────────────────────────────────────
#  DASHBOARD
# ──────────────────────────────────────────
@app.route('/')
def dashboard():
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) AS c FROM student")
    total_students = cur.fetchone()['c']

    cur.execute("SELECT COUNT(*) AS c FROM subject")
    total_subjects = cur.fetchone()['c']

    cur.execute("SELECT COUNT(*) AS c FROM attendance")
    total_classes = cur.fetchone()['c']

    cur.execute("SELECT COUNT(*) AS c FROM attendance WHERE status='Present'")
    total_present = cur.fetchone()['c']

    avg_pct = round((total_present / total_classes * 100), 1) if total_classes > 0 else 0

    # Latest 5 attendance records
    cur.execute("""
        SELECT s.name AS student_name, sub.subject_name, a.date, a.status
        FROM attendance a
        JOIN student s  ON a.student_id = s.student_id
        JOIN subject sub ON a.subject_id = sub.subject_id
        ORDER BY a.att_id DESC
        LIMIT 5
    """)
    recent = cur.fetchall()

    cur.close(); db.close()
    return render_template('index.html',
        total_students=total_students,
        total_subjects=total_subjects,
        total_classes=total_classes,
        avg_pct=avg_pct,
        recent=recent
    )


# ──────────────────────────────────────────
#  STUDENTS — List & Add
# ──────────────────────────────────────────
@app.route('/students', methods=['GET', 'POST'])
def students():
    db = get_db()
    cur = db.cursor(dictionary=True)

    if request.method == 'POST':
        sid  = request.form['student_id'].strip()
        name = request.form['name'].strip()
        dept = request.form['department'].strip()
        sem  = request.form['semester'].strip()
        try:
            cur.execute(
                "INSERT INTO student VALUES (%s, %s, %s, %s)",
                (sid, name, dept, sem)
            )
            db.commit()
            flash(f'✅ Student "{name}" added successfully!', 'success')
        except mysql.connector.IntegrityError:
            flash('❌ Student ID already exists.', 'error')
        except Exception as e:
            flash(f'❌ Error: {e}', 'error')
        return redirect(url_for('students'))

    cur.execute("SELECT * FROM student ORDER BY department, semester, name")
    student_list = cur.fetchall()
    cur.close(); db.close()
    return render_template('students.html', students=student_list)


# ──────────────────────────────────────────
#  DELETE STUDENT
# ──────────────────────────────────────────
@app.route('/students/delete/<int:sid>', methods=['POST'])
def delete_student(sid):
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute("DELETE FROM attendance WHERE student_id=%s", (sid,))
        cur.execute("DELETE FROM student WHERE student_id=%s", (sid,))
        db.commit()
        flash('🗑️ Student deleted.', 'success')
    except Exception as e:
        flash(f'❌ Error: {e}', 'error')
    cur.close(); db.close()
    return redirect(url_for('students'))


# ──────────────────────────────────────────
#  MARK ATTENDANCE
# ──────────────────────────────────────────
@app.route('/mark', methods=['GET', 'POST'])
def mark_attendance():
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT s.*, f.name AS faculty_name FROM subject s JOIN faculty f ON s.faculty_id=f.faculty_id")
    subjects = cur.fetchall()

    if request.method == 'POST':
        subject_id = request.form['subject_id']
        att_date   = request.form['date']

        cur.execute("SELECT * FROM student ORDER BY name")
        student_list = cur.fetchall()

        errors = 0
        for s in student_list:
            status = request.form.get(f'status_{s["student_id"]}', 'Absent')
            try:
                cur.execute(
                    "INSERT INTO attendance (student_id, subject_id, date, status) VALUES (%s,%s,%s,%s)",
                    (s['student_id'], subject_id, att_date, status)
                )
            except Exception:
                errors += 1

        db.commit()
        if errors == 0:
            flash(f'✅ Attendance marked for {len(student_list)} students on {att_date}!', 'success')
        else:
            flash(f'⚠️ Done with {errors} duplicate(s) skipped.', 'warning')
        cur.close(); db.close()
        return redirect(url_for('mark_attendance'))

    # GET — load students if subject+date chosen
    subject_id   = request.args.get('subject_id')
    att_date     = request.args.get('date', str(date.today()))
    student_list = []

    if subject_id:
        cur.execute("SELECT * FROM student ORDER BY name")
        student_list = cur.fetchall()
        for s in student_list:
            cur.execute(
                "SELECT status FROM attendance WHERE student_id=%s AND subject_id=%s AND date=%s",
                (s['student_id'], subject_id, att_date)
            )
            row = cur.fetchone()
            s['existing'] = row['status'] if row else None

    cur.close(); db.close()
    return render_template('mark_attendance.html',
        subjects=subjects,
        student_list=student_list,
        selected_subject=subject_id,
        selected_date=att_date
    )


# ──────────────────────────────────────────
#  ATTENDANCE REPORT
# ──────────────────────────────────────────
@app.route('/report')
def report():
    db = get_db()
    cur = db.cursor(dictionary=True)

    dept_filter = request.args.get('dept', '')
    sub_filter  = request.args.get('subject_id', '')

    query = """
        SELECT
            s.student_id,
            s.name        AS student_name,
            s.department,
            sub.subject_name,
            SUM(a.status = 'Present')   AS presents,
            SUM(a.status = 'Absent')    AS absents,
            COUNT(*)                    AS total_classes,
            ROUND((SUM(a.status='Present') / COUNT(*)) * 100, 1) AS percentage
        FROM attendance a
        JOIN student s   ON a.student_id = s.student_id
        JOIN subject sub ON a.subject_id = sub.subject_id
        WHERE 1=1
    """
    params = []
    if dept_filter:
        query += " AND s.department = %s"; params.append(dept_filter)
    if sub_filter:
        query += " AND a.subject_id = %s"; params.append(sub_filter)
    query += " GROUP BY a.student_id, a.subject_id ORDER BY s.name, sub.subject_name"

    cur.execute(query, params)
    report_data = cur.fetchall()

    cur.execute("SELECT DISTINCT department FROM student ORDER BY department")
    departments = [r['department'] for r in cur.fetchall()]

    cur.execute("SELECT * FROM subject ORDER BY subject_name")
    subjects = cur.fetchall()

    cur.close(); db.close()
    return render_template('report.html',
        report=report_data,
        departments=departments,
        subjects=subjects,
        dept_filter=dept_filter,
        sub_filter=sub_filter
    )


if __name__ == '__main__':
    app.run(debug=True)
