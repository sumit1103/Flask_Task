from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.json.sort_keys = False

# Connect Flask to MySQL.
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:1234@localhost/employee_leave_tracker"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Employee model.
class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(100), nullable=False)


# Leave model.
class Leave(db.Model):
    __tablename__ = "leaves"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(255))
    status = db.Column(db.String(20), default="PENDING")


# Home route.
@app.route("/")
def home():
    return "Employee Leave Tracker API is running"


# Create employee.
@app.route("/employees", methods=["POST"])
def create_employee():
    data = request.get_json()

    employee = Employee(
        name=data["name"],
        email=data["email"],
        department=data["department"]
    )

    db.session.add(employee)
    db.session.commit()

    return jsonify({
        "id": employee.id,
        "name": employee.name,
        "email": employee.email,
        "department": employee.department
    }), 201


# Get all employees.
@app.route("/employees", methods=["GET"])
def get_employees():
    employees = Employee.query.all()

    result = []

    for employee in employees:
        result.append({
            "id": employee.id,
            "name": employee.name,
            "email": employee.email,
            "department": employee.department
        })

    return jsonify(result)


# Apply for leave.
@app.route("/leaves", methods=["POST"])
def apply_leave():
    data = request.get_json()

    employee = Employee.query.get(data["employee_id"])

    if not employee:
        return jsonify({
            "error": "Employee not found"
        }), 404

    leave = Leave(
        employee_id=data["employee_id"],
        leave_type=data["leave_type"],
        start_date=datetime.strptime(
            data["start_date"], "%Y-%m-%d"
        ).date(),
        end_date=datetime.strptime(
            data["end_date"], "%Y-%m-%d"
        ).date(),
        reason=data.get("reason"),
        status="PENDING"
    )

    db.session.add(leave)
    db.session.commit()

    return jsonify({
        "id": leave.id,
        "employee_id": leave.employee_id,
        "leave_type": leave.leave_type,
        "start_date": str(leave.start_date),
        "end_date": str(leave.end_date),
        "reason": leave.reason,
        "status": leave.status
    }), 201


# Get all leaves.
@app.route("/leaves", methods=["GET"])
def get_leaves():
    leaves = Leave.query.all()

    result = []

    for leave in leaves:
        result.append({
            "id": leave.id,
            "employee_id": leave.employee_id,
            "leave_type": leave.leave_type,
            "start_date": str(leave.start_date),
            "end_date": str(leave.end_date),
            "reason": leave.reason,
            "status": leave.status
        })

    return jsonify(result)


# Approve leave.
@app.route("/leaves/<int:leave_id>/approve", methods=["PUT"])
def approve_leave(leave_id):
    leave = Leave.query.get(leave_id)

    if not leave:
        return jsonify({
            "error": "Leave not found"
        }), 404

    leave.status = "APPROVED"

    db.session.commit()

    return jsonify({
        "message": "Leave approved successfully",
        "leave_id": leave.id,
        "status": leave.status
    })


# Reject leave.
@app.route("/leaves/<int:leave_id>/reject", methods=["PUT"])
def reject_leave(leave_id):
    leave = Leave.query.get(leave_id)

    if not leave:
        return jsonify({
            "error": "Leave not found"
        }), 404

    leave.status = "REJECTED"

    db.session.commit()

    return jsonify({
        "message": "Leave rejected successfully",
        "leave_id": leave.id,
        "status": leave.status
    })


# Start the Flask server.
if __name__ == "__main__":
    app.run(debug=True)