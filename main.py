from fastmcp import FastMCP
import os
import aiosqlite
import json
from datetime import datetime
import csv
import asyncio

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP("ExpensesTracker")

# ================= Database =================
async def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                mobile TEXT DEFAULT "",
                description TEXT DEFAULT "",
                subcategory TEXT DEFAULT ""
            )
        ''')
        await db.commit()

# ================= MCP Tools =================
@mcp.tool()
async def add_expense(amount, category, date, description="", subcategory=""):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO expenses (amount, category, date, description, subcategory) VALUES (?, ?, ?, ?, ?)",
            (amount, category, date, description, subcategory)
        )
        await db.commit()
        return {"status": "success", "message": "Expense added successfully.", "id": cursor.lastrowid}


@mcp.tool()
async def list_expenses():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM expenses")
        rows = await cursor.fetchall()
        return [
            {
                "id": row[0],
                "amount": row[1],
                "category": row[2],
                "date": row[3],
                "description": row[4],
                "subcategory": row[5]
            } for row in rows
        ]


@mcp.tool()
async def remove_expense(expense_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        await db.commit()
        return {"status": "success", "message": "Expense removed successfully."}


@mcp.tool()
async def edit_expense(expense_id, amount=None, category=None, date=None, description=None, subcategory=None):
    fields, values = [], []
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
    
    if not fields:
        return {"status": "error", "message": "No fields to update"}
    
    values.append(expense_id)
    sql = f"UPDATE expenses SET {', '.join(fields)} WHERE id = ?"

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(sql, values)
        await db.commit()
    return {"status": "success", "message": "Expense updated successfully."}


@mcp.tool()
async def total_expenses(start_date=None, end_date=None):
    query = "SELECT SUM(amount) FROM expenses WHERE 1=1"
    params = []
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(query, params)
        total = await cursor.fetchone()
        return {"total": total[0] or 0}


@mcp.tool()
async def expenses_by_category():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        rows = await cursor.fetchall()
        return {row[0]: row[1] for row in rows}


@mcp.tool()
async def monthly_summary():
    today = datetime.now()
    start_date = today.replace(day=1).strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT SUM(amount) FROM expenses WHERE date >= ?", (start_date,))
        total = await cursor.fetchone()
        cursor = await db.execute("SELECT category, SUM(amount) FROM expenses WHERE date >= ? GROUP BY category", (start_date,))
        by_category = {row[0]: row[1] for row in await cursor.fetchall()}
        return {"month": today.month, "total_expenses": total[0] or 0, "by_category": by_category}


# ================= Category Tools =================
@mcp.tool()
async def list_categories():
    return await asyncio.to_thread(lambda: json.load(open(CATEGORIES_PATH)))


@mcp.tool()
async def add_category(name):
    categories = await asyncio.to_thread(lambda: json.load(open(CATEGORIES_PATH)))
    if name not in categories:
        categories.append(name)
        await asyncio.to_thread(lambda: json.dump(categories, open(CATEGORIES_PATH, "w")))
    return {"status": "success", "categories": categories}


@mcp.tool()
async def remove_category(name):
    categories = await asyncio.to_thread(lambda: json.load(open(CATEGORIES_PATH)))
    if name in categories:
        categories.remove(name)
        await asyncio.to_thread(lambda: json.dump(categories, open(CATEGORIES_PATH, "w")))
    return {"status": "success", "categories": categories}


@mcp.tool()
def credit():
    return "Expenses Tracker MCP by Akash Bankar."


@mcp.resource("expense://categories", mime_type="application/json")
async def categories_resource():
    return await asyncio.to_thread(lambda: open(CATEGORIES_PATH, "r", encoding="utf-8").read())


# ================= Startup =================
async def startup():
    await init_db()


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000, on_startup=startup)