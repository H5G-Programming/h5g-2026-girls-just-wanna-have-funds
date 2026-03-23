from datetime import datetime, timedelta
import os
import json

from dotenv import load_dotenv
from pathlib import Path
import pandas as pd

from flask import Flask, jsonify, request
from flask_cors import CORS
from mistralai import Mistral
from tavily import TavilyClient
from pydantic import BaseModel
from pydantic import Field

load_dotenv()

app = Flask(__name__)
CORS(app)

ROOT_PATH = Path(__file__).parent.parent

# =================================== APP SETUP ===================================
# 1. User dict
# 2. Counters to goals and transactions
# 3. Initial app goals
# 4. Building initial transactions
# 5. Helper functions for finding a adding a new transaction and finding a goal, 
# =================================================================================

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
        "target_amount_reasoning": "Target estimate provided by user.",
        "saved_amount": 250,
        "emoji": "🎧",
        "image_url": "",
        "status": "closed"
    },
    {
        "id": 2,
        "title": "New sneakers",
        "target_amount": 175,
        "target_amount_reasoning": "Target estimate provided by user.",
        "saved_amount": 175,
        "emoji": "👟",
        "image_url": "",
        "status": "closed"
    },
    {
        "id": 3,
        "title": "Cinema trip",
        "target_amount": 140,
        "target_amount_reasoning": "Target estimate provided by user.",
        "saved_amount": 140,
        "emoji": "🍿",
        "image_url": "",
        "status": "closed"
    },
    {
        "id": 4,
        "title": "New sneakers",
        "target_amount": 200,
        "target_amount_reasoning": "Target estimate provided by user.",
        "saved_amount": 35,
        "emoji": "\ud83d\udc5f",
        "image_url": "",
        "status": "active",
    },
    {
        "id": 5,
        "title": "Art set",
        "target_amount": 80,
        "target_amount_reasoning": "Target estimate provided by user.",
        "saved_amount": 22,
        "emoji": "\ud83c\udfa8",
        "image_url": "",
        "status": "active",
    },
    {
        "id": 6,
        "title": "Concert ticket",
        "target_amount": 120,
        "target_amount_reasoning": "Target estimate provided by user.",
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


def _find_goal(goal_id):
    # next is a function used to return the first matching item. If none is found it returns None
    # First 'goal' is the value we return if there is a match
    # Second 'goal' is the current item in the iteration - essentially the same as the first one but they serve different purposes
    # goals is the list of goals we iterate over
    # 'if' is followed by a condition (always either true or false)
    return next((goal for goal in goals if goal["id"] == goal_id), None)

# =========================== FORECASTING FUNCTIONALITY ===========================
# 1. Find m
# 2. Find b
# 3. Run forecast
# =================================================================================

def find_m(
        days: list[float],
        savings: list[float],
        avg_day: float ,
        avg_savings: float
    ):
    """Find the m in y=m*x + b (slope) based on historical transactions."""
    # Calculate the numerator Σ_i(x_i-avg_x)*(y_i-avg_y)
    numerator = sum((days[i] - avg_day) * (savings[i] - avg_savings)
                for i in range(len(days)))

    # Calculate the denominator Σ_i(x_i-avg_x)**2
    denominator = sum((days[i] - avg_day) ** 2
                    for i in range(len(days)))

    m = numerator / denominator
    return m

def find_b(
        avg_day: float,
        avg_savings: float,
        m: float
    ):
    """Find the b in y=m*x+b (intercept) based on historical transactions."""
    # Calculate the intercept based on the function b=avg_y-m*avg_x
    return avg_savings - m * avg_day

def run_forecast(goal_amount: float):
    """Run forecast"""
    # Get the dates and deposits from all transactions
    df_transactions = pd.DataFrame(transactions)
    df_deposits = df_transactions.query("type == 'deposit'").copy()
    df_deposits["date"] = pd.to_datetime(df_deposits["date"], format="mixed")

    # Convert dates to "days since first deposit" (our x)
    df_deposits["day"] = (df_deposits["date"] - df_deposits["date"].min()).dt.days

    # Convert deposits to "total amount saved since first deposit" (our y)
    df_deposits["total_saved"] = df_deposits["amount"].cumsum()

    # Store x and y as lists
    days = df_deposits["day"].to_list()
    savings = df_deposits["total_saved"].to_list()

    # Calculate average date and average savings amount
    avg_day = sum(days) / len(days)
    avg_savings = sum(savings) / len(savings)

    # Calculate the slope
    m = find_m(days, savings, avg_day, avg_savings)

    # Calculate the intercept
    b = find_b(avg_day, avg_savings, m)

    # Use m and b to calculate the predicted days
    predicted_days = (goal_amount - b) / m

    # To not get any weird display
    predicted_days = max(0, predicted_days)

    return predicted_days

# ============================== GENAI FUNCTIONATILY ==============================
# 1. Tavily tool definition
# 2. Structured output model
# 3. System prompt
# 4. estimate_price function
# =================================================================================

# Search Tavily tool definition
def search_tavily(search_query: str) -> list:
    """Search for specific query on the internet."""
    client = TavilyClient(api_key=os.getenv("TAVILY_KEY"))
    result = client.search(query=search_query)
    return result.get("results", [])

# Tool definition for LLM
LLM_TOOLS = [{
    "type": "function",
    "function": {
        "name": "search_tavily",
        "description": "Search for specific query on the internet.",
        "parameters": {
            "type": "object",
            "properties": {
                "search_query": {
                    "type": "string",
                    "description": "The search query to search for online.",
                }
            },
            "required": ["search_query"],
        },
    },
}]

SYSTEM_PROMPT = (
    "You are an expert in finding and estimating the cost of an item or financial goal based on limited user input. "
    "You will receive a few words from the user on what they are setting as a new financial goal for themselves and "
    "your job will be to give them an estimate for how much it will cost them to achieve this goal / aquire the item.\n"
    "You are welcome to use the search tool before giving your answer, but focus on finding pricing information for the item.\n"
    "The users are 13-16 year old danish girls, so provide cost estimates in DKK and makes sure to adapt any web searches "
    "to fit with what a teenage girl would like to do (i.e. if the user says 'New clothes', search 'new clothes for teenage girls price').\n"   
    "Your response should ONLY be a number in DKK. No explanation or anything else."
)

# Structured output
class Output(BaseModel):
    estimated_price: float = Field(
        description="The estimated price for the item provided by the user."
    )
    reasoning: str = Field(
        description="A short reasoning, describing the evidence for this price."
    )

# Estimating price with LLM if not provided
def estimate_price(user_input: str, system_prompt:str, model: str = "mistral-medium-latest", temperature: float = 0, return_all_messages: bool = False) -> dict:
    """Use an LLM to search the internet and estimate an appropriate price for a goal."""
    # 2. Create chat client
    client = Mistral(api_key=os.getenv('MISTRAL_KEY'))

    # 3. Define messages
    messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_input},
    ]

    # 4. Call LLM to get search result
    chat_response = client.chat.complete(
        model=model,
        messages = messages,
        tools = LLM_TOOLS,
        temperature=temperature
    )
    messages.append(chat_response.choices[0].message)
    
    # 5. Execute tool calls
    if messages[-1].tool_calls:
        for tool_call in messages[-1].tool_calls:
            args = tool_call.function.arguments
            if tool_call.function.name == 'search_tavily':
                web_results = search_tavily(**json.loads(args))
                tool_result = "\n\n".join(f"{r['title']}\n{r['content']}" for r in web_results)
                messages.append({
                    "role":"tool",
                    "name":tool_call.function.name,
                    "content": tool_result,
                    "tool_call_id":tool_call.id
                })
    else:
        return {"estimated_price": messages[-1].content, "reasoning": "LLM estimated immediately."}
    
    # 6. Get structured response from LLM
    chat_response = client.chat.parse(
        model=model,
        messages = messages,
        tools = LLM_TOOLS,
        response_format=Output
    )

    messages.append(chat_response.choices[0].message)
    structured_output = json.loads(chat_response.choices[0].message.content)

    if return_all_messages:
        return structured_output, messages
    else:
        return structured_output

# =============================== BACKEND API SETUP ===============================
# 1. Get User, Goal, and all transactions
# 2. Create New Goal (create goal)
# 3. Add funds to Goal
# 4. Move funds from source Goal to target Goal
# 5. Close Goal
# 6. Complete Goal
# 7. Create Summary
# 8. Run forecast for closest goal
# =================================================================================

@app.get("/api/user")
def get_user():
    # Returns the demo user data as JSON to follow API convensions (basically enables communication between frontend and backend)
    return jsonify(user)


@app.get("/api/goals")
def get_goals():
    return jsonify(goals)


@app.get("/api/transactions")
def get_transactions():
    #sorted is a keyword that sorts a list based on a key provided, here we sort by date in descending order
    sorted_transactions = sorted(transactions, key=lambda item: item["date"], reverse=True)
    return jsonify(sorted_transactions)


@app.post("/api/goals")
def create_goal():
    global next_goal_id
    data = request.get_json(force=True)
    title = data.get("title", "").strip() # strip() removes whitespace from the beginning and end of the string
    target_amount = data.get("target_amount") #.get() gives default value 0 if target_amount is not found
    if target_amount is not None:
        target_amount = float(target_amount)
    emoji = data.get("emoji", "\ud83d\udc9c")
    image_url = data.get("image_url", "")
    target_amount_reasoning = "Target estimate provided by user."

    # If no target_amount is given, estimate with LLM
    if target_amount is None or target_amount <= 0:
        estimated_price = estimate_price(
            user_input=title,
            system_prompt=SYSTEM_PROMPT
        )
        target_amount = estimated_price.get("estimated_price")
        target_amount_reasoning = estimated_price.get("reasoning")

    # TODO: Lesson 2 Exercise - Create a new goal dictionary with the provided data
    new_goal = {
        "id": next_goal_id,
        "title": title,
        "target_amount": target_amount,
        "target_amount_reasoning": target_amount_reasoning,
        "saved_amount": 0,
        "emoji": emoji,
        "image_url": image_url,
        "status": "active",
    }
    next_goal_id = next_goal_id + 1
    
    # TODO: Lesson 2 Exercise - Add the new goal dictionary to the list of existing goals
    goals.append(new_goal)
    return jsonify(new_goal), 201

@app.post("/api/predict-goal")
def predict_goal():
    data = request.get_json(force=True)
    goal_title = data.get("title", "").strip()

    if not goal_title:
        return jsonify({"cost": None, "emoji": ""})

    # For now, you can return dummy values
    # Later we'll integrate an AI model here
    predicted_cost = 0  # placeholder
    predicted_emoji = "🧡"  # placeholder

    return jsonify({"cost": predicted_cost, "emoji": predicted_emoji})


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

@app.post("/api/summary/forecast")
def number_of_days_until_goal():
    # Get goal amount
    data = request.get_json(force=True)
    target_amount = float(data.get("target_amount", 0))
    saved_amount = float(data.get("saved_amount", 0))
    goal_amount = target_amount - saved_amount

    # Run forecast
    predicted_days = run_forecast(goal_amount=goal_amount)

    return jsonify({
        "predicted_days": predicted_days
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5001"))
    # Flask's debug=True automatically enables the auto-reloader — whenever a .py file is saved, Flask detects the change and restarts the server automatically. No need to stop and restart manually.   
    app.run(debug=True, port=port)
