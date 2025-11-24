from fastmcp import FastMCP
import os
import sqlite3
import json
from datetime import datetime
import csv

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP("ExpensesTracker")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            mobile TEXT DEFAULT "",
            description TEXT DeFAULT "",
            subcategory TEXT DeFAULT ""
        )
    ''')

init_db()

@mcp.tool()
def add_expense(amount, category, date, description="", subcategory=""):
    """Add a new expense to the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (amount, category, date, description, subcategory) VALUES (?, ?, ?, ?, ?)", 
            (amount, category, date, description, subcategory)
            )
        return {"status": "success", "message": "Expense added successfully.","id": cursor.lastrowid}
        

@mcp.tool()
def list_expenses():
    """List all expenses from the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses")
        rows = cursor.fetchall()
        expenses = [
            {
                "id": row[0],
                "amount": row[1],
                "category": row[2],
                "date": row[3],
                "description": row[4],
                "subcategory": row[5]
            }
            for row in rows
        ]
        return expenses
    
@mcp.tool()
def remove_expense(expense_id):
    """Remove an expense from the database by ID."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        return {"status": "success", "message": "Expense removed successfully."}
    
@mcp.tool()
def edit_expense(expense_id, amount=None, category=None, date=None, description=None, subcategory=None):
    """Edit an existing expense in the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        fields = []
        values = []
        if amount is not None:
            fields.append("amount = ?")
            values.append(amount)
        if category is not None:
            fields.append("category = ?")
            values.append(category)
        if date is not None:
            fields.append("date = ?")
            values.append(date)
        if description is not None:
            fields.append("description = ?")
            values.append(description)
        if subcategory is not None:
            fields.append("subcategory = ?")
            values.append(subcategory)
        values.append(expense_id)
        sql = f"UPDATE expenses SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(sql, values)
        return {"status": "success", "message": "Expense updated successfully."}

@mcp.tool()
def credit():
    """Return the credit information."""
    return "Expenses Tracker MCP by Akash Bankar."

@mcp.tool()
def total_expenses(start_date=None, end_date=None):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        query = "SELECT SUM(amount) FROM expenses WHERE 1=1"
        params = []
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        cursor.execute(query, params)
        total = cursor.fetchone()[0] or 0
        return {"total": total}

@mcp.tool()
def expenses_by_category():
    """Get total expenses grouped by category."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        rows = cursor.fetchall()
        return {row[0]: row[1] for row in rows}


@mcp.tool()
def export_expenses(file_path="expenses_export.csv"):
    """Export all expenses to a CSV file."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses")
        rows = cursor.fetchall()
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "amount", "category", "date", "description", "subcategory"])
        writer.writerows(rows)
    return {"status": "success", "file": file_path}


@mcp.tool()
def monthly_summary():
    """Provide a simple dashboard of this month's expenses."""
    today = datetime.now()
    start_date = today.replace(day=1).strftime("%Y-%m-%d")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE date >= ?", (start_date,))
        total = cursor.fetchone()[0] or 0
        cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE date >= ? GROUP BY category", (start_date,))
        by_category = {row[0]: row[1] for row in cursor.fetchall()}
    return {"month": today.month, "total_expenses": total, "by_category": by_category}


@mcp.tool()
def import_expenses(file_path):
    """Import expenses from CSV."""
    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for row in data:
            cursor.execute(
                "INSERT INTO expenses (amount, category, date, description, subcategory) VALUES (?, ?, ?, ?, ?)",
                (float(row["amount"]), row["category"], row["date"], row.get("description",""), row.get("subcategory",""))
            )
    return {"status": "success", "message": f"{len(data)} expenses imported."}


@mcp.tool()
def list_categories():
    """List all categories."""
    with open(CATEGORIES_PATH) as f:
        return json.load(f)

@mcp.tool()
def add_category(name):
    """Add a new category."""
    with open(CATEGORIES_PATH) as f:
        categories = json.load(f)
    if name not in categories:
        categories.append(name)
        with open(CATEGORIES_PATH, "w") as f:
            json.dump(categories, f)
    return {"status": "success", "categories": categories}


@mcp.tool()
def remove_category(name):
    """Remove a category."""
    with open(CATEGORIES_PATH) as f:
        categories = json.load(f)
    if name in categories:
        categories.remove(name)
        with open(CATEGORIES_PATH, "w") as f:
            json.dump(categories, f)
    return {"status": "success", "categories": categories}

@mcp.tool()
def set_reminder(date, message):
    """Set a reminder for a specific date with a message."""
    # This is a placeholder implementation.
    # In a real application, you would integrate with a scheduling system.
    return {"status": "success", "message": f"Reminder set for {date} with message: {message}"}

def reminder_on_mobile_message(mobile, date, message):
    """Send a reminder message to the specified mobile number."""
    # This is a placeholder implementation.
    # In a real application, you would integrate with an SMS gateway.
    return {"status": "success", "message": f"Reminder sent to {mobile} for {date} with message: {message}"}

@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    """Provide the categories JSON resource."""
    with open(CATEGORIES_PATH, "r",encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    mcp.run()
