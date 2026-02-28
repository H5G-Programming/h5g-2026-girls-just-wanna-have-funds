from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ---- Data ----

# =============================================
# EXERCISE 1: Change the user to have your own name
# =============================================
# Hint: Think back to exercise 5 from last week (lesson 1)
user = {"id": 1, "name": "Maya"}

next_goal_id = 4

goals = [
    {
        "id": 1,
        "title": "New sneakers",
        "target_amount": 200,
        "saved_amount": 124,
        "emoji": "👟",
        "image_url": "",
        "status": "active",
    },
    {
        "id": 2,
        "title": "Art set",
        "target_amount": 80,
        "saved_amount": 32,
        "emoji": "🎨",
        "image_url": "",
        "status": "active",
    },
    {
        "id": 3,
        "title": "Concert ticket",
        "target_amount": 120,
        "saved_amount": 95,
        "emoji": "🎶",
        "image_url": "",
        "status": "active",
    },
]

transactions = []


# ---- Helper ----

def find_goal(goal_id):
    for goal in goals:
        if goal["id"] == goal_id:
            return goal
    return None


# ---- Endpoints ----

@app.get("/api/user")
def get_user():
    return jsonify(user)


@app.get("/api/goals")
def get_goals():
    return jsonify(goals)


@app.post("/api/goals")
def create_goal():
    global next_goal_id
    data = request.get_json(force=True)
    title = data["title"]
    target_amount = data["target_amount"]
    emoji = data["emoji"]
    image_url = data["image_url"]

    # =============================================
    # EXERCISE 3: Create a new goal
    # =============================================
    new_goal = {
        "id": next_goal_id,
        "title": title,
        # Add the remaining keys yourself:
        # target_amount, saved_amount, emoji, image_url, status
        # Hint: saved_amount starts at 0, status should be "active"
    }

    next_goal_id = next_goal_id + 1

    # Add new_goal to the goals list below:

    return jsonify(new_goal), 201


@app.post("/api/goals/<int:goal_id>/add-funds")
def add_funds(goal_id):
    data = request.get_json(force=True)
    amount = data["amount"]

    goal = find_goal(goal_id)

    # =============================================
    # EXERCISE 2: Add funds to a goal
    # =============================================
    # Add the funds to the goal's saved amount. [] is used to access a key in the dictionary.
    goal["saved_amount"] = _____ + amount

    return jsonify(goal)


@app.post("/api/goals/<int:goal_id>/move-funds")
def move_funds(goal_id):
    data = request.get_json(force=True)
    amount = data["amount"]
    target_goal_id = data["target_goal_id"]

    source_goal = find_goal(goal_id)
    target_goal = find_goal(target_goal_id)

    # =============================================
    # EXERCISE 4: Move funds between goals
    # =============================================
    # Hint: You need TWO lines here.
    #   1. Subtract amount from source_goal's saved_amount.
    #   2. Add amount to target_goal's saved_amount.
    # (Think back to Exercise 2 — same idea, two goals this time.)
    # Pattern: something["saved"] = something["saved"] - amount
    # Now do it with source_goal and target_goal using "saved_amount":

    return jsonify({"source": source_goal, "target": target_goal})


@app.post("/api/goals/<int:goal_id>/close")
def close_goal(goal_id):
    data = request.get_json(force=True)
    target_goal_id = data["target_goal_id"]

    goal_to_be_closed = find_goal(goal_id)
    target_goal = find_goal(target_goal_id)

    # =============================================
    # EXERCISE 5: Close a goal
    # =============================================

    # YOUR CODE HERE  (1 of 3)
    # Hint: Get the saved_amount from goal_to_be_closed and store it in a variable called amount.

    # YOUR CODE HERE  (2 of 3)
    # Hint: Only move funds if there IS money to move.
    #       Use an if statement: if amount > 0, move it to target_goal and set goal_to_be_closed to 0.

    # YOUR CODE HERE  (3 of 3)
    # Hint: Set the status of goal_to_be_closed to "closed".

    return jsonify({"source": goal_to_be_closed, "target": target_goal})


@app.post("/api/goals/<int:goal_id>/complete")
def complete_goal(goal_id):
    goal = find_goal(goal_id)
    goal["status"] = "archived"
    return jsonify(goal)

##### The rest can be ignored. It just adds some activities to the log to make the website look nice.
@app.get("/api/transactions")
def get_transactions():
    sorted_transactions = sorted(transactions, key=lambda item: item["date"], reverse=True)
    return jsonify(sorted_transactions)


@app.get("/api/summary")
def get_summary():
    active_goals = [goal for goal in goals if goal["status"] == "active"]
    total_saved = sum(goal["saved_amount"] for goal in active_goals)

    closest_goal = None
    if active_goals:
        closest_goal = max(
            active_goals,
            key=lambda goal: goal["saved_amount"] / goal["target_amount"],
        )

    month_totals = {}
    for transaction in transactions:
        month = transaction["date"][0:7]
        if month not in month_totals:
            month_totals[month] = {"month": month, "in": 0, "out": 0}

        if transaction["type"] in ("deposit", "transfer_in"):
            month_totals[month]["in"] = month_totals[month]["in"] + transaction["amount"]
        elif transaction["type"] in ("transfer_out", "complete"):
            month_totals[month]["out"] = month_totals[month]["out"] + transaction["amount"]

    sorted_months = sorted(month_totals.values(), key=lambda item: item["month"])

    return jsonify(
        {
            "total_saved": total_saved,
            "closest_goal": closest_goal,
            "monthly_activity": sorted_months,
        }
    )

next_transaction_id = 1

def _new_transaction_id():
    global next_transaction_id
    transaction_id = next_transaction_id
    next_transaction_id = next_transaction_id + 1
    return transaction_id

def _add_transaction(goal_id, transaction_type, amount, note="", date_override=None): #note and date_override provides default values if not provided
    created_at = date_override or "2026-02-28T00:00:00Z"
    transaction = {
        "id": _new_transaction_id(),
        "goal_id": goal_id,
        "type": transaction_type,
        "amount": amount,
        "date": created_at,
        "note": note,
    }
    transactions.append(transaction)
    return transaction

def _seed_transactions():
    sample_transactions = [
        (1, "deposit", 20, "Babysitting", "2026-02-20T00:00:00Z"),
        (1, "deposit", 15, "Allowance", "2026-02-03T00:00:00Z"),
        (2, "deposit", 10, "Gift", "2026-01-19T00:00:00Z"),
        (2, "deposit", 12, "Snack savings", "2025-12-25T00:00:00Z"),
        (3, "deposit", 18, "Chores", "2026-02-16T00:00:00Z"),
        (3, "deposit", 22, "Weekly save", "2025-12-18T00:00:00Z"),
    ]
    
    for goal_id, tx_type, amount, note, date_value in sample_transactions:
        _add_transaction(
            goal_id,
            tx_type,
            amount,
            note=note,
            date_override=date_value,
        )


_seed_transactions()

app.run(debug=True, port=5001)
