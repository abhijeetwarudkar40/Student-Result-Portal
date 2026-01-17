STUDENT RESULT MANAGEMENT APP (Flask + MySQL)

--------------------------------------------
SETUP INSTRUCTIONS
--------------------------------------------

1️⃣ Install Dependencies
-------------------------
pip install -r requirements.txt

2️⃣ Create Database in MySQL
-----------------------------
Run the SQL setup file in MySQL shell or phpMyAdmin:

mysql -u root -p
(source path/to/db_setup.sql)

3️⃣ Update MySQL Credentials (if needed)
----------------------------------------
Edit 'app.py' and modify:
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '404040',
    'db': 'student_results'
}

4️⃣ Run the Flask App
---------------------
python app.py

5️⃣ Open in Browser
-------------------
http://127.0.0.1:5000

Enjoy your Student Result Management System!
