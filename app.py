from flask import Flask, render_template, request, redirect, url_for
import math
from datetime import datetime
import random

app = Flask(__name__)

class Transaction:
    def __init__(self, amount, description, date=None):
        self.amount = amount
        self.description = description
        self.date = date if date else datetime.now().date()

    def display(self):
        return f"{self.date} {self.amount} {self.description}"

class Income(Transaction):
    def display(self):
        return f"{self.date} Income {self.amount} {self.description}"

class Expenditure(Transaction):
    def display(self):
        return f"{self.date} Expenditure {self.amount} {self.description}"

class Investment:
    def __init__(self, amount, duration, start_date=None):
        self.amount = amount
        self.duration = duration
        self.start_date = start_date if start_date else datetime.now().date()


    def maturity_amount(self):
        return self.amount

class SIP(Investment):
    def __init__(self, amount, duration, monthly, start_date=None):
        super().__init__(amount, duration, start_date)
        self.monthly = monthly

    def display(self):
        return f"{self.start_date} SIP {self.amount} {self.duration} {self.monthly}                               {self.maturity_amount()}"


    def maturity_amount(self):
        final = self.amount * math.pow(1 + (0.096 / 12), self.duration * 12)
        return final + (self.monthly * 12 * self.duration)

class FD(Investment):
    def display(self):
        return f"{self.start_date} FD {self.amount} {self.duration} {self.maturity_amount()}"

    def maturity_amount(self):
        return self.amount * math.pow((1 + 0.071), self.duration)

class FinanceManager:
    def __init__(self):
        self.transactions = []
        self.investments = []
        self.alerts = []

    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        self.check_alerts(transaction)

    def add_investment(self, investment):
        self.investments.append(investment)

    
    def calculate_income(self):
        return sum(t.amount for t in self.transactions if isinstance(t, Income))

    def calculate_expenditure(self):
        return sum(t.amount for t in self.transactions if isinstance(t, Expenditure))

    def display_summary(self):
        income = self.calculate_income()
        expenditure = self.calculate_expenditure()
        balance = income - expenditure

        print("Summary:")
        print(f"Total Income: {income}")
        print(f"Total Expenditure: {expenditure}")
        print(f"Net Balance: {balance}")
        

    def display_record(self, balance):
        records = {
            "balance": balance,
            "transactions": [t.display() for t in self.transactions],
            "investments": [i.display() for i in self.investments]  # Now includes maturity amount
        }
        return records
        

    def display_alerts(self):
        return self.alerts

    def trend_analysis(self):
        trend = {
            "total_income": self.calculate_income(),
            "total_expenditure": self.calculate_expenditure(),
            "status": "saving" if self.calculate_income() > self.calculate_expenditure() else "spending more"
        }
        return trend

    def check_alerts(self, transaction):
        if transaction.amount > 10000:
            self.alerts.append(f"High transaction alert: {transaction.amount} on {transaction.date}")
        if self.calculate_expenditure() > self.calculate_income():
            self.alerts.append("Expenditure is greater than income.")
            

    def daily_finance_tip(self):
        tips = [
            "Track your expenses daily to avoid overspending.",
            "Invest in a diversified portfolio to minimize risk.",
            "Set financial goals and review them regularly.",
            "Save at least 20% of your income every month.",
            "Avoid impulse purchases by making a shopping list."
        ]
        return random.choice(tips)

class User:
    def __init__(self, initial_balance):
        self.manager = FinanceManager()
        self.balance = initial_balance

    def record_income(self, amount, description):
        self.manager.add_transaction(Income(amount, description))
        self.balance += amount

    def record_expenditure(self, amount, description):
        if self.balance - amount < 1000:
            return "Error: Balance cannot go below 1000."
        self.manager.add_transaction(Expenditure(amount, description))
        self.balance -= amount

    def make_investment(self, type, amount, duration, monthly=None):
        if self.balance - amount < 1000:
            return "Error: Balance cannot go below 1000."
        if type == "SIP":
            self.manager.add_investment(SIP(amount, duration, monthly))
        elif type == "FD":
            self.manager.add_investment(FD(amount, duration))
        self.balance -= amount

    def get_finance_info(self):
        return self.manager.display_record(self.balance)

    def get_alerts(self):
        return self.manager.display_alerts()

    def get_trend_analysis(self):
        return self.manager.trend_analysis()

    def get_daily_tip(self):
        return self.manager.daily_finance_tip()

user = User(2000)  # Create user with initial balance 2000

@app.route('/')
def index():
    return render_template('index.html', balance=user.balance, transactions=user.get_finance_info()["transactions"], investments=user.get_finance_info()["investments"], alerts=user.get_alerts(), trend=user.get_trend_analysis(), tip=user.get_daily_tip())

@app.route('/add_income', methods=['POST'])
def add_income():
    amount = float(request.form['amount'])
    description = request.form['description']
    user.record_income(amount, description)
    return redirect(url_for('index'))

@app.route('/add_expenditure', methods=['POST'])
def add_expenditure():
    amount = float(request.form['amount'])
    description = request.form['description']
    user.record_expenditure(amount, description)
    return redirect(url_for('index'))

@app.route('/add_investment', methods=['POST'])
def add_investment():
    type = request.form['type']
    amount = float(request.form['amount'])
    duration = int(request.form['duration'])
    monthly = float(request.form['monthly']) if 'monthly' in request.form else None
    user.make_investment(type, amount, duration, monthly)
    return redirect(url_for('index'))

@app.route('/resources')
def resources():
    return render_template('resources.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
