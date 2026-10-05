from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Connect Flask to MySQL.
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:1234@localhost/feedback_management"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Feedback model.
class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False)
    feedback_text = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), default="GENERAL")
    status = db.Column(db.String(20), default="PENDING")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Home route.
@app.route("/")
def home():
    return "Feedback Management API is running"


# Submit feedback.
@app.route("/feedback", methods=["POST"])
def submit_feedback():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    employee_name = data.get("employee_name")
    feedback_text = data.get("feedback_text")

    if not employee_name or not feedback_text:
        return jsonify({
            "error": "employee_name and feedback_text are required"
        }), 400

    feedback = Feedback(
        employee_name=employee_name,
        feedback_text=feedback_text
    )

    db.session.add(feedback)
    db.session.commit()

    return jsonify({
        "id": feedback.id,
        "employee_name": feedback.employee_name,
        "feedback_text": feedback.feedback_text,
        "category": feedback.category,
        "status": feedback.status
    }), 201


# Get all feedback.
@app.route("/feedback", methods=["GET"])
def get_feedback():

    feedbacks = Feedback.query.all()

    result = []

    for feedback in feedbacks:
        result.append({
            "id": feedback.id,
            "employee_name": feedback.employee_name,
            "feedback_text": feedback.feedback_text,
            "category": feedback.category,
            "status": feedback.status,
            "created_at": feedback.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify(result)


# Categorize feedback.
@app.route("/feedback/<int:feedback_id>/category", methods=["PUT"])
def categorize_feedback(feedback_id):

    feedback = db.session.get(Feedback, feedback_id)

    if not feedback:
        return jsonify({
            "error": "Feedback not found"
        }), 404

    data = request.get_json()

    if not data or not data.get("category"):
        return jsonify({
            "error": "Category is required"
        }), 400

    feedback.category = data["category"].upper()

    db.session.commit()

    return jsonify({
        "message": "Feedback category updated",
        "id": feedback.id,
        "category": feedback.category
    })


# Get feedback by category.
@app.route("/feedback/category/<category>", methods=["GET"])
def get_feedback_by_category(category):

    feedbacks = Feedback.query.filter_by(
        category=category.upper()
    ).all()

    result = []

    for feedback in feedbacks:
        result.append({
            "id": feedback.id,
            "employee_name": feedback.employee_name,
            "feedback_text": feedback.feedback_text,
            "category": feedback.category,
            "status": feedback.status
        })

    return jsonify(result)


# Update feedback status.
@app.route("/feedback/<int:feedback_id>/status", methods=["PUT"])
def update_feedback_status(feedback_id):

    feedback = db.session.get(Feedback, feedback_id)

    if not feedback:
        return jsonify({
            "error": "Feedback not found"
        }), 404

    data = request.get_json()

    if not data or not data.get("status"):
        return jsonify({
            "error": "Status is required"
        }), 400

    status = data["status"].upper()

    if status not in ["PENDING", "REVIEWED"]:
        return jsonify({
            "error": "Status must be PENDING or REVIEWED"
        }), 400

    feedback.status = status

    db.session.commit()

    return jsonify({
        "message": "Feedback status updated",
        "id": feedback.id,
        "status": feedback.status
    })


# Create database tables.
with app.app_context():
    db.create_all()


# Start Flask server.
if __name__ == "__main__":
    app.run(debug=True)