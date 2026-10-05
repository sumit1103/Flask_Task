import mysql.connector

# Connect to MySQL.
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="employee_leave_tracker"
)

print("MySQL connected successfully")