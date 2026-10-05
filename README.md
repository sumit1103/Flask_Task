python -m venv venv
venv\Scripts\activate
pip install flask flask-sqlalchemy pymysql
pip list
http://127.0.0.1:5000
GET http://127.0.0.1:5000/employees
GET http://127.0.0.1:5000/leaves
PUT http://127.0.0.1:5000/leaves/1/approve
PUT http://127.0.0.1:5000/leaves/2/reject
GET http://127.0.0.1:5000/groups
GET http://127.0.0.1:5000/groups/1/members
GET http://127.0.0.1:5000/groups/1/expenses
GET http://127.0.0.1:5000/groups/1/balances
GET http://127.0.0.1:5000/feedback
PUT http://127.0.0.1:5000/feedback/1/category
{
    "category": "GENERAL"
}
GET http://127.0.0.1:5000/feedback/category/GENERAL
PUT http://127.0.0.1:5000/feedback/1/status
{
    "status": "REVIEWED"
}
GET http://127.0.0.1:5000/tasks
{
    "status": "IN_PROGRESS"
}
PUT http://127.0.0.1:5000/tasks/1/priority
{
    "priority": "HIGH"
}
GET http://127.0.0.1:5000/tasks/priority/HIGH
GET http://127.0.0.1:5000/tasks/assigned/Rahul
app.py
   ↓
Ctrl + C
   ↓
expense_app.py
   ↓
Ctrl + C
   ↓
feedback_app.py
   ↓
Ctrl + C
   ↓
task_app.py
