# 📘 Student Result Portal(Flask + MySQL)

A **web-based Student Result Management System** built using **Flask** and **MySQL** that allows users to store, manage, and retrieve student records, subjects, and exam results efficiently through a simple web interface.

---

## ✨ Features

- Add and manage students
- Add subjects
- Enter and update marks
- Automatically calculate total marks and grades
- View individual student results
- MySQL database backend
- Flask-based web interface

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask  
- **Database:** MySQL  
- **Frontend:** HTML, CSS, Jinja Templates  

---

## ▶️ Setup Instructions

### 1️⃣ Install Dependencies

Run the following command to install required Python packages:

```bash
pip install -r requirements.txt
```
### 2️⃣ Create Database in MySQL
```bash
mysql -u root -p
source path/to/db_setup.sql
```
### 3️⃣ Update MySQL Credentials (if needed)
```bash
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '404040',
    'db': 'student_results'
}
```
### 4️⃣ Run the Flask App
```bash
python app.py
```
### 5️⃣ Open in Browser
```bash
http://127.0.0.1:5000
```
