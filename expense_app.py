from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Connect Flask to MySQL.
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:1234@localhost/expense_splitter"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Group model.
class Group(db.Model):
    __tablename__ = "expense_group"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


# Member model.
class Member(db.Model):
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    group_id = db.Column(
        db.Integer,
        db.ForeignKey("expense_group.id"),
        nullable=False
    )


# Expense model.
class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(
        db.Integer,
        db.ForeignKey("expense_group.id"),
        nullable=False
    )
    paid_by = db.Column(
        db.Integer,
        db.ForeignKey("members.id"),
        nullable=False
    )
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)


# Home route.
@app.route("/")
def home():
    return "Expense Splitter API is running"


# Create a new group.
@app.route("/groups", methods=["POST"])
def create_group():
    data = request.get_json()

    if not data or not data.get("name"):
        return jsonify({
            "error": "Group name is required"
        }), 400

    group = Group(
        name=data["name"]
    )

    db.session.add(group)
    db.session.commit()

    return jsonify({
        "id": group.id,
        "name": group.name
    }), 201


# Get all groups.
@app.route("/groups", methods=["GET"])
def get_groups():
    groups = Group.query.all()

    result = []

    for group in groups:
        result.append({
            "id": group.id,
            "name": group.name
        })

    return jsonify(result)


# Add a member to a group.
@app.route("/groups/<int:group_id>/members", methods=["POST"])
def add_member(group_id):
    data = request.get_json()

    group = db.session.get(Group, group_id)

    if not group:
        return jsonify({
            "error": "Group not found"
        }), 404

    if not data or not data.get("name"):
        return jsonify({
            "error": "Member name is required"
        }), 400

    member = Member(
        name=data["name"],
        group_id=group_id
    )

    db.session.add(member)
    db.session.commit()

    return jsonify({
        "id": member.id,
        "name": member.name,
        "group_id": member.group_id
    }), 201


# Get all members in a group.
@app.route("/groups/<int:group_id>/members", methods=["GET"])
def get_members(group_id):
    group = db.session.get(Group, group_id)

    if not group:
        return jsonify({
            "error": "Group not found"
        }), 404

    members = Member.query.filter_by(group_id=group_id).all()

    result = []

    for member in members:
        result.append({
            "id": member.id,
            "name": member.name,
            "group_id": member.group_id
        })

    return jsonify(result)


# Add a new expense.
@app.route("/expenses", methods=["POST"])
def add_expense():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    group_id = data.get("group_id")
    paid_by = data.get("paid_by")
    amount = data.get("amount")
    description = data.get("description")

    if not group_id or not paid_by or amount is None or not description:
        return jsonify({
            "error": "group_id, paid_by, amount and description are required"
        }), 400

    group = db.session.get(Group, group_id)

    if not group:
        return jsonify({
            "error": "Group not found"
        }), 404

    member = db.session.get(Member, paid_by)

    if not member:
        return jsonify({
            "error": "Member not found"
        }), 404

    if member.group_id != group_id:
        return jsonify({
            "error": "Member does not belong to this group"
        }), 400

    if amount <= 0:
        return jsonify({
            "error": "Amount must be greater than 0"
        }), 400

    expense = Expense(
        group_id=group_id,
        paid_by=paid_by,
        amount=amount,
        description=description
    )

    db.session.add(expense)
    db.session.commit()

    return jsonify({
        "id": expense.id,
        "group_id": expense.group_id,
        "paid_by": expense.paid_by,
        "amount": expense.amount,
        "description": expense.description
    }), 201


# Get all expenses in a group.
@app.route("/groups/<int:group_id>/expenses", methods=["GET"])
def get_expenses(group_id):
    group = db.session.get(Group, group_id)

    if not group:
        return jsonify({
            "error": "Group not found"
        }), 404

    expenses = Expense.query.filter_by(group_id=group_id).all()

    result = []

    for expense in expenses:
        result.append({
            "id": expense.id,
            "group_id": expense.group_id,
            "paid_by": expense.paid_by,
            "amount": expense.amount,
            "description": expense.description
        })

    return jsonify(result)


# Calculate balances and who owes whom.
@app.route("/groups/<int:group_id>/balances", methods=["GET"])
def get_balances(group_id):
    group = db.session.get(Group, group_id)

    if not group:
        return jsonify({
            "error": "Group not found"
        }), 404

    members = Member.query.filter_by(group_id=group_id).all()

    if not members:
        return jsonify({
            "error": "No members found in this group"
        }), 404

    expenses = Expense.query.filter_by(group_id=group_id).all()

    total_expense = sum(expense.amount for expense in expenses)

    if total_expense == 0:
        return jsonify({
            "group_id": group_id,
            "total_expense": 0,
            "message": "No expenses found"
        })

    # Calculate equal share for each member.
    share = total_expense / len(members)

    balances = []

    for member in members:

        paid = sum(
            expense.amount
            for expense in expenses
            if expense.paid_by == member.id
        )

        balance = paid - share

        balances.append({
            "member_id": member.id,
            "name": member.name,
            "paid": round(paid, 2),
            "share": round(share, 2),
            "balance": round(balance, 2)
        })

    # Separate people who need to pay and receive money.
    payers = []
    receivers = []

    for balance in balances:

        if balance["balance"] < 0:
            payers.append({
                "name": balance["name"],
                "amount": abs(balance["balance"])
            })

        elif balance["balance"] > 0:
            receivers.append({
                "name": balance["name"],
                "amount": balance["balance"]
            })

    # Calculate who owes whom.
    settlements = []

    for payer in payers:

        for receiver in receivers:

            if payer["amount"] <= 0:
                break

            if receiver["amount"] <= 0:
                continue

            amount = min(
                payer["amount"],
                receiver["amount"]
            )

            settlements.append({
                "from": payer["name"],
                "to": receiver["name"],
                "amount": round(amount, 2)
            })

            payer["amount"] -= amount
            receiver["amount"] -= amount

    return jsonify({
        "group_id": group_id,
        "total_expense": round(total_expense, 2),
        "balances": balances,
        "settlements": settlements
    })


# Create database tables.
with app.app_context():
    db.create_all()


# Start the Flask server.
if __name__ == "__main__":
    app.run(debug=True)