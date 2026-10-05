from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Connect Flask to MySQL.
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:1234@localhost/task_priority_manager"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Task model.
class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500))
    priority = db.Column(db.String(20), default="MEDIUM")
    deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="PENDING")
    assigned_to = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Home route.
@app.route("/")
def home():
    return "Task Priority Manager API is running"


# Create task.
@app.route("/tasks", methods=["POST"])
def create_task():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    title = data.get("title")
    description = data.get("description")
    priority = data.get("priority", "MEDIUM").upper()
    deadline = data.get("deadline")
    assigned_to = data.get("assigned_to")

    if not title or not deadline or not assigned_to:
        return jsonify({
            "error": "title, deadline and assigned_to are required"
        }), 400

    if priority not in ["LOW", "MEDIUM", "HIGH"]:
        return jsonify({
            "error": "Priority must be LOW, MEDIUM or HIGH"
        }), 400

    try:
        task_deadline = datetime.strptime(
            deadline,
            "%Y-%m-%d"
        ).date()
    except ValueError:
        return jsonify({
            "error": "Deadline must be in YYYY-MM-DD format"
        }), 400

    task = Task(
        title=title,
        description=description,
        priority=priority,
        deadline=task_deadline,
        assigned_to=assigned_to
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "deadline": str(task.deadline),
        "status": task.status,
        "assigned_to": task.assigned_to
    }), 201


# Get all tasks.
@app.route("/tasks", methods=["GET"])
def get_tasks():

    tasks = Task.query.all()

    result = []

    for task in tasks:
        result.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "deadline": str(task.deadline),
            "status": task.status,
            "assigned_to": task.assigned_to
        })

    return jsonify(result)


# Get one task.
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):

    task = db.session.get(Task, task_id)

    if not task:
        return jsonify({
            "error": "Task not found"
        }), 404

    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "deadline": str(task.deadline),
        "status": task.status,
        "assigned_to": task.assigned_to
    })


# Update task status.
@app.route("/tasks/<int:task_id>/status", methods=["PUT"])
def update_status(task_id):

    task = db.session.get(Task, task_id)

    if not task:
        return jsonify({
            "error": "Task not found"
        }), 404

    data = request.get_json()

    if not data or not data.get("status"):
        return jsonify({
            "error": "Status is required"
        }), 400

    status = data["status"].upper()

    if status not in ["PENDING", "IN_PROGRESS", "COMPLETED"]:
        return jsonify({
            "error": "Invalid status"
        }), 400

    task.status = status

    db.session.commit()

    return jsonify({
        "message": "Task status updated",
        "id": task.id,
        "status": task.status
    })


# Update task priority.
@app.route("/tasks/<int:task_id>/priority", methods=["PUT"])
def update_priority(task_id):

    task = db.session.get(Task, task_id)

    if not task:
        return jsonify({
            "error": "Task not found"
        }), 404

    data = request.get_json()

    if not data or not data.get("priority"):
        return jsonify({
            "error": "Priority is required"
        }), 400

    priority = data["priority"].upper()

    if priority not in ["LOW", "MEDIUM", "HIGH"]:
        return jsonify({
            "error": "Priority must be LOW, MEDIUM or HIGH"
        }), 400

    task.priority = priority

    db.session.commit()

    return jsonify({
        "message": "Task priority updated",
        "id": task.id,
        "priority": task.priority
    })


# Get tasks by priority.
@app.route("/tasks/priority/<priority>", methods=["GET"])
def get_tasks_by_priority(priority):

    tasks = Task.query.filter_by(
        priority=priority.upper()
    ).all()

    result = []

    for task in tasks:
        result.append({
            "id": task.id,
            "title": task.title,
            "priority": task.priority,
            "deadline": str(task.deadline),
            "status": task.status,
            "assigned_to": task.assigned_to
        })

    return jsonify(result)


# Get tasks assigned to a user.
@app.route("/tasks/assigned/<user>", methods=["GET"])
def get_tasks_by_user(user):

    tasks = Task.query.filter_by(
        assigned_to=user
    ).all()

    result = []

    for task in tasks:
        result.append({
            "id": task.id,
            "title": task.title,
            "priority": task.priority,
            "deadline": str(task.deadline),
            "status": task.status,
            "assigned_to": task.assigned_to
        })

    return jsonify(result)


# Create database tables.
with app.app_context():
    db.create_all()


# Start Flask server.
if __name__ == "__main__":
    app.run(debug=True)