from fastmcp import FastMCP
import os
import sqlite3

mcp = FastMCP("ExpenseTracker")
DB_PATH = os.path.join(os.path.dirname(__file__), "expense.db")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute(
                """
                CREATE TABLE IF NOT EXISTS expense(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT DEFAULT '',
                    note TEXT DEFAULT '' 
                    )
                """
                )

init_db()

@mcp.tool()
def add_expense(date, amount, category, subcategory="", note=""):
    '''Add a new expense entry to the database'''
    with sqlite3.connect(DB_PATH) as c:
        curr = c.execute(
                "INSERT INTO expense(date,amount,category,subcategory,note) VALUES(?,?,?,?,?)",
                (date,amount,category,subcategory,note)
        )
        return {"status": "ok", "id": curr.lastrowid}


@mcp.tool()
def list_expense():
    '''List all the expenses in the database'''
    with sqlite3.connect(DB_PATH) as c:
        curr = c.execute("SELECT id, date, amount, category, subcategory, note FROM expense ORDER BY id ASC")
        cols = [d[0] for d in curr.description]
        return [dict(zip(cols, r)) for r in curr.fetchall()]

@mcp.tool()
def summerize(start_date, end_date, category=None):
    '''Summerizes the expenses in perticluar time frame for a particular category'''
    with sqlite3.connect(DB_PATH) as c:

        query = """
                SELECT category, SUM(amount) AS total_amount
                FROM expense
                WHERE date between ? AND ?
                """

        params = [start_date, end_date]
        if category:
            query += "AND category = ?"
            params.append(query)
        
        query += "GROUP BY category ORDER BY category ASC"

        curr = c.execute(query, params)
        cols = [d[0] for d in curr.description]
        return [dict(zip(cols, r)) for r in curr.fetchall()]


if __name__ == "__main__":
    mcp.run()

