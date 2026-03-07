from datetime import datetime, timedelta
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

from pathlib import Path

import pandas as pd

app = Flask(__name__)
CORS(app)

ROOT_PATH = Path(__file__).parent.parent

# In-memory data for a single demo user
user = {"id": 1, "name": "Maya"}

# Simple counters to keep IDs readable
next_goal_id = 7
next_transaction_id = 1

# List of savings goals each contained in {} to have more attributes and split by ,
goals = [
    {
        "id": 1,
        "title": "Wireless headphones",
        "target_amount": 250,
        "saved_amount": 250,
        "emoji": "🎧",
        "image_url": "",
        "status": "closed"
    },
    {
        "id": 2,
        "title": "New sneakers",
        "target_amount": 175,
        "saved_amount": 175,
        "emoji": "👟",
        "image_url": "",
        "status": "closed"
    },
    {
        "id": 3,
        "title": "Cinema trip",
        "target_amount": 140,
        "saved_amount": 140,
        "emoji": "🍿",
        "image_url": "",
        "status": "closed"
    },
    {
        "id": 4,
        "title": "New sneakers",
        "target_amount": 200,
        "saved_amount": 35,
        "emoji": "\ud83d\udc5f",
        "image_url": "",
        "status": "active",
    },
    {
        "id": 5,
        "title": "Art set",
        "target_amount": 80,
        "saved_amount": 22,
        "emoji": "\ud83c\udfa8",
        "image_url": "",
        "status": "active",
    },
    {
        "id": 6,
        "title": "Concert ticket",
        "target_amount": 120,
        "saved_amount": 40,
        "emoji": "\ud83c\udfb6",
        "image_url": "",
        "status": "active",
    },
]

# Empty list of transactions
transactions = []

# to decalre a function you have to use keyword 'def' followed by name and parentheses
def _new_transaction_id():
    global next_transaction_id # Refers to the globale variable and enables us to change it instead of creating a new local one and changing that instead
    transaction_id = next_transaction_id
    next_transaction_id = next_transaction_id + 1
    return transaction_id

# function with arguments, because to add transaction you have to inform the computer of certain details
def _add_transaction(goal_id, transaction_type, amount, note="", date_override=None): #note and date_override provides default values if not provided
    created_at = date_override or datetime.now().isoformat() + "Z"
    transaction = {
        "id": _new_transaction_id(),
        "goal_id": goal_id,
        "type": transaction_type,
        "amount": amount,
        "date": created_at,
        "note": note,
    }
    transactions.append(transaction) # append is a function that adds an item to the end of a list
    return transaction


def _find_goal(goal_id):
    # next is a function used to return the first matching item. If none is found it returns None
    # First 'goal' is the value we return if there is a match
    # Second 'goal' is the current item in the iteration - essentially the same as the first one but they serve different purposes
    # goals is the list of goals we iterate over
    # 'if' is followed by a condition (always either true or false)
    return next((goal for goal in goals if goal["id"] == goal_id), None)

# Seed some initial transactions for demo purposes
def _seed_transactions():
    sample_transactions = pd.read_csv(ROOT_PATH / "transactions.csv")
    sample_transactions['date'] = pd.to_datetime(sample_transactions.date, format='%Y-%m-%d')

    # Loop through the sample transactions and add them to the transactions list
    for _, (goal_id, tx_type, amount, note, date_value) in sample_transactions.iterrows():
        _add_transaction(
            goal_id,
            tx_type,
            amount,
            note=note,
            date_override=date_value.isoformat() + "Z",
        )


_seed_transactions()


@app.get("/api/user")
def get_user():
    # Returns the demo user data as JSON to follow API convensions (basically enables communication between frontend and backend)
    return jsonify(user)


@app.get("/api/goals")
def get_goals():
    return jsonify(goals)


@app.post("/api/goals")
def create_goal():
    global next_goal_id
    data = request.get_json(force=True)
    title = data.get("title", "").strip() # strip() removes whitespace from the beginning and end of the string
    target_amount = float(data.get("target_amount", 0)) #.get() gives default value 0 if target_amount is not found
    emoji = data.get("emoji", "\ud83d\udc9c")
    image_url = data.get("image_url", "")

    # TODO: Lesson 2 Exercise - Create a new goal dictionary with the provided data
    new_goal = {
        "id": next_goal_id,
        "title": title,
        "target_amount": target_amount,
        "saved_amount": 0,
        "emoji": emoji,
        "image_url": image_url,
        "status": "active",
    }
    next_goal_id = next_goal_id + 1
    
    # TODO: Lesson 2 Exercise - Add the new goal dictionary to the list of existing goals
    goals.append(new_goal)
    return jsonify(new_goal), 201


@app.post("/api/goals/<int:goal_id>/add-funds")
def add_funds(goal_id):
    data = request.get_json(force=True)
    amount = float(data.get("amount", 0))
    note = data.get("note", "")

    goal = _find_goal(goal_id)

    # Add the funds to the goal's saved amount. [] is used to access the specific key in the dictionary
    # TODO: Lesson 2 Exercise - Complete the line below to add the amount to the saved_amount
    goal["saved_amount"] = goal["saved_amount"] + amount

    _add_transaction(goal_id, "deposit", amount, note=note)
    return jsonify(goal)


@app.post("/api/goals/<int:goal_id>/move-funds")
def move_funds(goal_id):
    data = request.get_json(force=True)
    amount = float(data.get("amount", 0))
    target_goal_id = int(data.get("target_goal_id", 0))

    source_goal = _find_goal(goal_id) #the goal we are moving funds from
    target_goal = _find_goal(target_goal_id) #the goal we are moving funds to

    # TODO: Lesson 2 - Move the funds between the two goals
    source_goal["saved_amount"] = source_goal["saved_amount"] - amount
    target_goal["saved_amount"] = target_goal["saved_amount"] + amount

    # Record the transactions for both goals (adds to the transactions list)
    _add_transaction(source_goal["id"], "transfer_out", amount, note="Moved to another goal")
    _add_transaction(target_goal["id"], "transfer_in", amount, note="Received from another goal")

    return jsonify({"source": source_goal, "target": target_goal})


@app.post("/api/goals/<int:goal_id>/close")
def close_goal(goal_id):
    data = request.get_json(force=True)
    target_goal_id = int(data.get("target_goal_id", 0))

    goal_to_be_closed = _find_goal(goal_id) 
    target_goal = _find_goal(target_goal_id) #the goal we are moving the remaining funds to

    # TODO - Lesson 2 - Get the saved amount from the goal to be closed
    amount = goal_to_be_closed["saved_amount"]

    # TODO - Lesson 2 - If the amount is > 0,
    # add the amount to the saved amount of the target goal
    # and set the saved amount of the goal to be closed to 0
    if amount > 0:
        goal_to_be_closed["saved_amount"] = 0
        target_goal["saved_amount"] = target_goal["saved_amount"] + amount

    _add_transaction(goal_to_be_closed["id"], "transfer_out", amount, note="Closed goal")
    _add_transaction(target_goal["id"], "transfer_in", amount, note="From closed goal")


    # TODO - Lesson 2 - set the status of the goal to 'closed'
    goal_to_be_closed["status"] = "closed"

    return jsonify({"source": goal_to_be_closed, "target": target_goal})


@app.post("/api/goals/<int:goal_id>/complete")
def complete_goal(goal_id):
    goal = _find_goal(goal_id)
    if not goal:
        return jsonify({"error": "Goal not found."}), 404

    goal["status"] = "archived"
    _add_transaction(goal_id, "complete", goal['target_amount'], note=f"Goal {goal['title']} completed")
    return jsonify(goal)


@app.get("/api/transactions")
def get_transactions():
    #sorted is a keyword that sorts a list based on a key provided, here we sort by date in descending order
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
        month = transaction["date"][0:7] # There are 7 characters because the format is:'YYYY-MM'
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5001"))
    # Flask's debug=True automatically enables the auto-reloader — whenever a .py file is saved, Flask detects the change and restarts the server automatically. No need to stop and restart manually.   
    app.run(debug=True, port=port)
