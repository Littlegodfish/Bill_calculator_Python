# Stage 3A: SQLite

# Imports 
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, JSON
from datetime import datetime
from bill_calculator import subtotal_checker, tax_tip_calculation

# My app setup
app = Flask(__name__) 
Scss(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


def ensure_receipt_schema():
    """Add missing columns for older SQLite schemas without full migration tooling."""
    try:
        columns = db.session.execute(text("PRAGMA table_info(receipt)")).fetchall()
        column_names = {column[1] for column in columns}

        if "grand_total" not in column_names:
            db.session.execute(
                text("ALTER TABLE receipt ADD COLUMN grand_total FLOAT NOT NULL DEFAULT 0.0")
            )
            print("✓ Added grand_total column to receipt")

        if "user_id" not in column_names:
            db.session.execute(
                text("ALTER TABLE receipt ADD COLUMN user_id INTEGER DEFAULT 1")
            )
            print("✓ Added user_id column to receipt")

        if "people" not in column_names:
            db.session.execute(
                text("ALTER TABLE receipt ADD COLUMN people TEXT DEFAULT '[]'")
            )
            print("✓ Added people column to receipt")

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Schema check note: {e}")

#Data Class: Row of Data
class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    completed = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"Task {self.id}"
# Data Class: Receipt: Contains ID, Title, Subtotal, Tax, Tip, Grand Total, Split Tip Evenly (Boolean), People, Created Date
class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    tax = db.Column(db.Float, nullable=False)
    tip = db.Column(db.Float, nullable=False)
    grand_total = db.Column(db.Float, nullable=False)
    split_tip_evenly = db.Column(db.Boolean, default=False)
    
    # Store people data as JSON: [{"name": str, "base_cost": float, "final_amount": float}, ...]
    people = db.Column(JSON, default=list)
    
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"Receipt {self.id}: {self.title}"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    receipts = db.relationship("Receipt", backref="user", lazy=True)

with app.app_context():
    db.create_all()
    ensure_receipt_schema()

#Routes to webpages
#Home page
@app.route("/", methods=["POST", "GET"])
def index():
    #Add a new task to the database
    if request.method == "POST":
        current_task = request.form['content']
        current_amount = float(request.form['amount'])
        new_task = MyTask(content=current_task, amount=current_amount)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"Error: {e}")
            return(f"Error: {e}")
    #See all tasks in the database
    else:
        tasks = MyTask.query.order_by(MyTask.created).all()
        return render_template("index.html", tasks=tasks)
@app.route("/split", methods=["POST", "GET"])
#Split the bill and show each person's cost
def split():
    if request.method == "POST":
        people_list = request.form['names'].split()
        money_list = [float(request.form[f'cost_{name}']) for name in people_list]
        subtotal = float(request.form['subtotal'])
        tax = float(request.form['tax'])
        tip = float(request.form['tip'])
        evenly_split_tip = request.form.get('evenly_split_tip') == 'y'

        subtotal_checker(subtotal, money_list)
        results, _ = tax_tip_calculation(
            tax,
            tip,
            subtotal,
            money_list,
            people_list,
            evenly_split_tip,
            len(people_list)
        )
        breakdown = dict(zip(people_list, [round(r, 2) for r in results]))
        return render_template("split.html", breakdown=breakdown)
    return render_template("split.html", breakdown=None)
#Delete a task
@app.route("/delete/<int:id>")
def delete(id:int):
    delete_task = MyTask.query.get_or_404(id)
    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        return(f"Error: {e}")
#Edit a task
@app.route("/edit/<int:id>", methods=["POST", "GET"])
def edit(id:int):
    edit_task = MyTask.query.get_or_404(id)
    if request.method == "POST":
        edit_task.content = request.form['content']
        edit_task.amount = float(request.form['amount']) 
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return(f"Error: {e}")
    else:
        return render_template("edit.html", task=edit_task)

# Bill Calculator API endpoint
@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    people_list = data['people']        # list of names
    money_list = data['costs']          # list of floats matching people
    subtotal = float(data['subtotal'])
    tax = float(data['tax'])
    tip = float(data['tip'])
    evenly_split_tip = bool(data.get('evenly_split_tip', False))

    subtotal_checker(subtotal, money_list)
    results, _ = tax_tip_calculation(
        tax,
        tip,
        subtotal,
        money_list,
        people_list,
        evenly_split_tip,
        len(people_list)
    )
    breakdown = {name: round(amount, 2) for name, amount in zip(people_list, results)}
    return jsonify(breakdown)

@app.route("/save_receipt", methods=["POST"])
def save_receipt():
    data = request.get_json(silent=True) or {}

    people = data.get("people", [])
    costs = data.get("costs", [])
    breakdown = data.get("breakdown", {})

    if not isinstance(people, list) or not isinstance(costs, list):
        return jsonify({"message": "Invalid receipt payload."}), 400

    if len(people) == 0 or len(people) != len(costs):
        return jsonify({"message": "People and costs must be non-empty and match."}), 400

    try:
        title = str(data.get("title", "Untitled Receipt")).strip() or "Untitled Receipt"
        subtotal = float(data.get("subtotal", 0) or 0)
        tax = float(data.get("tax", 0) or 0)
        tip = float(data.get("tip", 0) or 0)
        split_tip_evenly = bool(data.get("evenly_split_tip", False))

        receipt = Receipt(
            title=title,
            subtotal=subtotal,
            tax=tax,
            tip=tip,
            grand_total=0.0,
            split_tip_evenly=split_tip_evenly,
            # user_id will be set when authentication is implemented
        )

        grand_total = 0.0
        people_data = []
        
        for name, base_cost in zip(people, costs):
            clean_name = str(name).strip()
            if clean_name == "":
                continue

            base_cost_value = float(base_cost or 0)
            final_amount_value = float(breakdown.get(clean_name, base_cost_value))
            grand_total += final_amount_value

            people_data.append({
                "name": clean_name,
                "base_cost": round(base_cost_value, 2),
                "final_amount": round(final_amount_value, 2),
            })

        if len(people_data) == 0:
            return jsonify({"message": "No valid people to save."}), 400

        receipt.people = people_data
        receipt.grand_total = round(grand_total, 2)

        db.session.add(receipt)
        db.session.commit()

        return jsonify({"message": "Receipt saved successfully.", "receipt_id": receipt.id}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.exception("Failed to save receipt: %s", e)
        return jsonify({"message": "Failed to save receipt on the server."}), 500

#Runner & Debugger
if __name__ == "__main__":
    app.run(debug= True)