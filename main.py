from fastmcp import FastMCP
import os
import sqlite3


DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")

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


if __name__ == "__main__":
    mcp.run()
