# Imports 
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from bill_calculator import subtotal_checker, tax_tip_calculation

# My app setup
app = Flask(__name__) 
Scss(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

#Data Class: Row of Data
class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    completed = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"Task {self.id}"

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
        results = tax_tip_calculation(tax, tip, subtotal, money_list, evenly_split_tip, len(people_list))
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
    results = tax_tip_calculation(tax, tip, subtotal, money_list, evenly_split_tip, len(people_list))
    breakdown = {name: round(amount, 2) for name, amount in zip(people_list, results)}
    return jsonify(breakdown)

#Runner & Debugger
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug= True)