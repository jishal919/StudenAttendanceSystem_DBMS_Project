# 🎓 Student Attendance Management System
### Flask + MySQL | Mini Project

---

## ⚙️ Setup Instructions (Step by Step)

### 1. Install Python packages
```bash
pip install flask mysql-connector-python
```

### 2. Set up MySQL database
Open MySQL Workbench / command line and run:
```sql
source schema.sql
```
Or paste the contents of `schema.sql` directly into MySQL Workbench.

### 3. Update database password in app.py
Open `app.py` and find this block near the top:
```python
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': '',   # ← PUT YOUR MySQL PASSWORD HERE
    'database': 'attendance_db'
}
```

### 4. Run the app
```bash
python app.py
```

### 5. Open in browser
```
http://127.0.0.1:5000
```

---

## 📁 Project Structure
```
attendance_system/
├── app.py                    ← Flask backend
├── schema.sql                ← Database schema + sample data
├── requirements.txt
├── README.md
└── templates/
    ├── base.html             ← Layout + CSS
    ├── index.html            ← Dashboard
    ├── students.html         ← Add / view students
    ├── mark_attendance.html  ← Mark attendance
    └── report.html           ← Attendance reports
```

---

## 🗂️ DB Concepts Used
| Concept            | Where Used                              |
|--------------------|-----------------------------------------|
| ER Diagram         | student, faculty, course, subject, att. |
| Normalization      | 3NF — no redundant data                 |
| Joins              | Report query (student + subject + att.) |
| Views              | `attendance_summary` view               |
| Triggers           | `prevent_duplicate_attendance`          |
| Stored Procedure   | `mark_attendance_class`                 |

---

## 🔗 Pages
| URL         | Description                 |
|-------------|-----------------------------|
| `/`         | Dashboard with stats        |
| `/students` | Add / view / delete students|
| `/mark`     | Mark attendance by subject  |
| `/report`   | Attendance % per student    |
