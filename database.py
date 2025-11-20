import sqlite3
from typing import List, Optional, Tuple, Dict
import datetime
import csv
import os
from model import Todo

DB_FILE = "todos.db"
VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {1, 2}  # 1=open, 2=done

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_connection()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                category TEXT NOT NULL,
                status INTEGER NOT NULL,
                priority TEXT NOT NULL,
                due_date TEXT,
                created_at TEXT NOT NULL,
                date_completed TEXT
            )
            """
        )
    conn.close()

create_table()

def insert_todo(todo: Todo) -> int:
    conn = get_connection()
    with conn:
        cur = conn.execute(
            "INSERT INTO todos (task, category, status, priority, due_date, created_at, date_completed) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (todo.task, todo.category, todo.status, todo.priority, todo.due_date, todo.created_at, todo.date_completed),
        )
        tid = cur.lastrowid
    conn.close()
    return tid

def _row_to_todo(row: sqlite3.Row) -> Todo:
    return Todo(
        id=row["id"],
        task=row["task"],
        category=row["category"],
        status=row["status"],
        priority=row["priority"],
        due_date=row["due_date"],
        created_at=row["created_at"],
        date_completed=row["date_completed"],
    )

def get_all_todos() -> List[Todo]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM todos ORDER BY id").fetchall()
    conn.close()
    return [_row_to_todo(r) for r in rows]

def get_todo_by_id(tid: int) -> Optional[Todo]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (tid,)).fetchone()
    conn.close()
    return _row_to_todo(row) if row else None

def delete_todo(tid: int) -> None:
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM todos WHERE id = ?", (tid,))
    conn.close()

def update_todo(tid: int, task: Optional[str] = None, category: Optional[str] = None,
                priority: Optional[str] = None, due_date: Optional[str] = None) -> None:
    conn = get_connection()
    with conn:
        if task is not None:
            conn.execute("UPDATE todos SET task = ? WHERE id = ?", (task, tid))
        if category is not None:
            conn.execute("UPDATE todos SET category = ? WHERE id = ?", (category, tid))
        if priority is not None:
            conn.execute("UPDATE todos SET priority = ? WHERE id = ?", (priority, tid))
        if due_date is not None:
            conn.execute("UPDATE todos SET due_date = ? WHERE id = ?", (due_date, tid))
    conn.close()

def complete_todo(tid: int) -> None:
    conn = get_connection()
    with conn:
        conn.execute("UPDATE todos SET status = 2, date_completed = ? WHERE id = ?",
                     (datetime.datetime.utcnow().isoformat(), tid))
    conn.close()

def clear_completed() -> int:
    conn = get_connection()
    with conn:
        cur = conn.execute("DELETE FROM todos WHERE status = 2")
        deleted = cur.rowcount
    conn.close()
    return deleted

def reset_db() -> None:
    # remove file and recreate
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    create_table()

def export_csv(path: str, todos: List[Todo]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id","task","category","status","priority","due_date","created_at","date_completed"])
        for t in todos:
            writer.writerow([t.id, t.task, t.category, t.status, t.priority, t.due_date, t.created_at, t.date_completed])

def search_todos(query: str) -> List[Todo]:
    q = f"%{query.lower()}%"
    conn = get_connection()
    rows = conn.execute("SELECT * FROM todos WHERE LOWER(task) LIKE ? OR LOWER(category) LIKE ? ORDER BY id", (q, q)).fetchall()
    conn.close()
    return [_row_to_todo(r) for r in rows]

def stats() -> Dict[str, int]:
    todos = get_all_todos()
    total = len(todos)
    done = sum(1 for t in todos if t.status == 2)
    pending = total - done
    now = datetime.date.today()
    overdue = 0
    for t in todos:
        if t.due_date and t.status == 1:
            try:
                d = datetime.date.fromisoformat(t.due_date)
                if d < now:
                    overdue += 1
            except Exception:
                pass
    completion_rate = int((done / total * 100) if total else 0)
    return {"total": total, "done": done, "pending": pending, "overdue": overdue, "completion_rate": completion_rate}