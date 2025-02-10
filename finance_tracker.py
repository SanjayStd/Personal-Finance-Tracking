from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime

app = Flask(__name__)

INCOME_FILE = "income.xlsx"
EXPENSE_FILE = "expense.xlsx"
CHART_PATH_PIE = "static/pie_chart.png"
CHART_PATH_BAR = "static/bar_chart.png"

def initialize_files():
    for file, columns in [(INCOME_FILE, ["Date", "Type", "Amount"]),
                          (EXPENSE_FILE, ["Date", "Type", "Amount"])]:
        if not os.path.exists(file):
            df = pd.DataFrame(columns=columns)
            df.to_excel(file, index=False, engine='openpyxl')
    
    # Generate empty charts at the start
    generate_charts()


def load_excel(file):
    if os.path.exists(file):
        return pd.read_excel(file, engine='openpyxl')
    return pd.DataFrame(columns=["Date", "Type", "Amount"])

def save_to_excel(file, new_data):
    df = load_excel(file)
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel(file, index=False, engine='openpyxl')

def calculate_totals():
    df_income = load_excel(INCOME_FILE)
    df_expense = load_excel(EXPENSE_FILE)

    total_income = df_income["Amount"].sum() if not df_income.empty else 0
    total_expense = df_expense["Amount"].sum() if not df_expense.empty else 0
    balance = total_income - total_expense

    return total_income, total_expense, balance

def generate_charts():
    df_income = load_excel(INCOME_FILE)
    df_expense = load_excel(EXPENSE_FILE)

    if df_income.empty and df_expense.empty:
        return

    # Income Pie Chart
    if not df_income.empty:
        plt.figure(figsize=(5, 5))
        df_income.groupby("Type")["Amount"].sum().plot(kind="pie", autopct="%1.1f%%", colors=["blue", "green", "cyan"])
        plt.title("Income Breakdown")
        plt.ylabel("")
        plt.savefig("static/income_pie_chart.png")
        plt.close()

    # Expense Pie Chart
    if not df_expense.empty:
        plt.figure(figsize=(5, 5))
        df_expense.groupby("Type")["Amount"].sum().plot(kind="pie", autopct="%1.1f%%", colors=["red", "orange", "yellow"])
        plt.title("Expense Breakdown")
        plt.ylabel("")
        plt.savefig("static/expense_pie_chart.png")
        plt.close()

    # Income vs Expense Bar Chart
    plt.figure(figsize=(5, 5))
    plt.bar(["Income", "Expense"], [df_income["Amount"].sum(), df_expense["Amount"].sum()], color=["green", "red"])
    plt.title("Income vs Expense")
    plt.ylabel("Amount")
    plt.savefig("static/bar_chart.png")
    plt.close()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        category = request.form["category"]

        if category == "income":
            income_type = request.form["type"]
            amount = float(request.form["amount"])
            new_entry = pd.DataFrame([[datetime.today().strftime("%Y-%m-%d"), income_type, amount]],
                                     columns=["Date", "Type", "Amount"])
            save_to_excel(INCOME_FILE, new_entry)

        elif category == "expense":
            expense_type = request.form["type"]
            amount = float(request.form["amount"])
            new_expense = pd.DataFrame([[datetime.today().strftime("%Y-%m-%d"), expense_type, amount]],
                                       columns=["Date", "Type", "Amount"])
            save_to_excel(EXPENSE_FILE, new_expense)

        generate_charts()
        return redirect(url_for("index"))

    total_income, total_expense, balance = calculate_totals()
    return render_template("index.html", total_income=total_income, total_expense=total_expense, balance=balance)

if __name__ == "__main__":
    initialize_files()
    app.run(debug=True)

