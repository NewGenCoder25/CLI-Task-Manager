import typer
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.padding import Padding
from datetime import date, datetime
import re

from model import Todo
import database as db

app = typer.Typer()
console = Console()

CATEGORY_COLORS = {
    "Learn": "cyan",
    "YouTube": "red",
    "Code": "green",
    "Gaming": "yellow",
    "Travel": "magenta",
}
PRIORITY_COLORS = {
    "high": "red",
    "medium": "yellow",
    "low": "green",
}

def parse_date_opt(d: Optional[str]) -> Optional[str]:
    if not d:
        return None
    # accept YYYY-MM-DD or ISO, normalize to YYYY-MM-DD
    try:
        if re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            # validate
            datetime.fromisoformat(d)
            return d
        else:
            # try parse ISO
            dt = datetime.fromisoformat(d)
            return dt.date().isoformat()
    except Exception:
        raise typer.BadParameter("Date must be YYYY-MM-DD or ISO format")

def validate_priority(p: Optional[str]) -> Optional[str]:
    if p is None or not isinstance(p, str):
        return None
    if p not in {"low", "medium", "high"}:
        raise typer.BadParameter("priority must be low, medium, or high")
    return p

def index_to_todo_id(position: int, current_list: Optional[List[Todo]] = None) -> int:
    if current_list is None:
        current_list = db.get_all_todos()
    if position < 1 or position > len(current_list):
        console.print("[red]Invalid item number[/red]")
        raise typer.Exit(code=1)
    return current_list[position - 1].id

@app.command()
def add(task: str = typer.Argument(..., help="Task description"),
        category: str = typer.Argument(..., help="Category"),
        priority: str = typer.Option("medium", "--priority", "-p", help="low|medium|high"),
        due: Optional[str] = typer.Option(None, "--due", "-d", help="Due date YYYY-MM-DD")):
    """Add a new task"""
    due_norm = parse_date_opt(due)
    pr = validate_priority(priority)
    todo = Todo(id=None, task=task, category=category, priority=pr, due_date=due_norm)
    tid = db.insert_todo(todo)
    console.print(f"[green]Added task[/green] (id={tid}): {task}")
    show()

@app.command()
def show(category: Optional[str] = typer.Option(None, "--category", "-c"),
         status: Optional[str] = typer.Option(None, "--status", "-s", help="open|done"),
         priority: Optional[str] = typer.Option(None, "--priority", "-p", help="low|medium|high"),
         due_before: Optional[str] = typer.Option(None, "--due-before", help="YYYY-MM-DD"),
         due_after: Optional[str] = typer.Option(None, "--due-after", help="YYYY-MM-DD"),
         sort: Optional[str] = typer.Option("id", "--sort", help="id|priority|due|created|status")):
    """Show tasks (supports filters)"""
    # prepare filters
    pr = validate_priority(priority) if priority else None
    sb = parse_date_opt(due_before) if due_before else None
    sa = parse_date_opt(due_after) if due_after else None
    status_val = None
    if status:
        st = status.lower()
        if st == "open":
            status_val = 1
        elif st == "done":
            status_val = 2
        else:
            raise typer.BadParameter("status must be 'open' or 'done'")

    todos = db.get_all_todos()

    def keep(t: Todo) -> bool:
        if category and t.category != category:
            return False
        if status_val and t.status != status_val:
            return False
        if pr and t.priority != pr:
            return False
        if sb:
            if not t.due_date:
                return False
            try:
                if datetime.fromisoformat(t.due_date).date() >= datetime.fromisoformat(sb).date():
                    return False
            except Exception:
                return False
        if sa:
            if not t.due_date:
                return False
            try:
                if datetime.fromisoformat(t.due_date).date() <= datetime.fromisoformat(sa).date():
                    return False
            except Exception:
                return False
        return True

    filtered = [t for t in todos if keep(t)]

    # sorting
    if sort == "priority":
        order = {"high": 0, "medium": 1, "low": 2}
        filtered.sort(key=lambda x: order.get(x.priority, 1))
    elif sort == "due":
        filtered.sort(key=lambda x: (x.due_date is None, x.due_date or ""))
    elif sort == "created":
        filtered.sort(key=lambda x: x.created_at or "")
    elif sort == "status":
        filtered.sort(key=lambda x: x.status)
    else:
        filtered.sort(key=lambda x: x.id or 0)

    # display
    console.print(Padding("[bold magenta]Todos[/bold magenta] 💻", (0,0,1,0)))
    if not filtered:
        console.print("[yellow]No tasks match your filters.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("#", style="dim", width=4)
    table.add_column("Task", min_width=20)
    table.add_column("Category", min_width=12)
    table.add_column("Priority", min_width=8, justify="center")
    table.add_column("Due", min_width=12, justify="center")
    table.add_column("Done", min_width=6, justify="center")

    for idx, t in enumerate(filtered, start=1):
        cat_color = CATEGORY_COLORS.get(t.category, "white")
        pr_color = PRIORITY_COLORS.get(t.priority, "white")
        done = "✅" if t.status == 2 else "❌"
        due_str = t.due_date or "-"
        table.add_row(str(idx), t.task, f"[{cat_color}]{t.category}[/{cat_color}]", f"[{pr_color}]{t.priority}[/{pr_color}]", due_str, done)

    console.print(table)
    # small legend
    console.print()
    console.print("[dim]Use the index (#) shown above for update/complete/delete operations.[/dim]")

@app.command()
def update(position: int = typer.Argument(..., help="Index from `show`"),
           task: Optional[str] = typer.Option(None, "--task"),
           category: Optional[str] = typer.Option(None, "--category"),
           priority: Optional[str] = typer.Option(None, "--priority"),
           due: Optional[str] = typer.Option(None, "--due")):
    """Update fields of a task (by shown position)"""
    todos = db.get_all_todos()
    # map using current full list
    tid = index_to_todo_id(position, todos)
    due_norm = parse_date_opt(due) if due else None
    pr = validate_priority(priority) if priority else None
    db.update_todo(tid, task=task, category=category, priority=pr, due_date=due_norm)
    console.print(f"[green]Updated task (id={tid})[/green]")
    show()

@app.command()
def delete(position: int):
    """Delete a task by its shown position"""
    todos = db.get_all_todos()
    tid = index_to_todo_id(position, todos)
    db.delete_todo(tid)
    console.print(f"[red]Deleted task (id={tid})[/red]")
    show()

@app.command()
def complete(position: int):
    """Mark a task completed by its shown position"""
    todos = db.get_all_todos()
    tid = index_to_todo_id(position, todos)
    db.complete_todo(tid)
    console.print(f"[cyan]Completed task (id={tid})[/cyan]")
    show()

@app.command("clear-completed")
def clear_completed():
    """Remove all completed tasks"""
    removed = db.clear_completed()
    console.print(f"[yellow]Cleared {removed} completed task(s).[/yellow]")
    show()

@app.command()
def export(path: str = typer.Argument(..., help="Path to CSV file"),
           category: Optional[str] = typer.Option(None, "--category"),
           status: Optional[str] = typer.Option(None, "--status"),
           priority: Optional[str] = typer.Option(None, "--priority")):
    """Export tasks (filtered) to CSV"""
    # reuse show's filtering behavior by building filtered list
    # simple way: call get_all and apply filters like show
    # (we replicate minimal filtering here)
    status_val = None
    if status:
        if status.lower() == "open":
            status_val = 1
        elif status.lower() == "done":
            status_val = 2
    pr = validate_priority(priority) if priority else None
    todos = db.get_all_todos()
    filtered = [t for t in todos if (not category or t.category == category) and (not status_val or t.status == status_val) and (not pr or t.priority == pr)]
    db.export_csv(path, filtered)
    console.print(f"[green]Exported {len(filtered)} tasks to {path}[/green]")

@app.command()
def reset(confirm: bool = typer.Option(False, "--confirm", help="Confirm reset; destroys DB")):
    """Reset the database (delete all tasks). Use --confirm to actually reset."""
    if not confirm:
        console.print("[red]This command will delete your database. Re-run with --confirm to proceed.[/red]")
        raise typer.Exit()
    db.reset_db()
    console.print("[yellow]Database reset complete.[/yellow]")

@app.command()
def search(query: str):
    """Search tasks by text in task or category"""
    results = db.search_todos(query)
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return
    # show results with their natural order (id), but index corresponds to this result list
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("#", style="dim", width=4)
    table.add_column("Task")
    table.add_column("Category")
    table.add_column("Priority")
    table.add_column("Due")
    table.add_column("Done", justify="center")
    for idx, t in enumerate(results, start=1):
        cat_color = CATEGORY_COLORS.get(t.category, "white")
        pr_color = PRIORITY_COLORS.get(t.priority, "white")
        done = "✅" if t.status == 2 else "❌"
        due_str = t.due_date or "-"
        table.add_row(str(idx), t.task, f"[{cat_color}]{t.category}[/{cat_color}]", f"[{pr_color}]{t.priority}[/{pr_color}]", due_str, done)
    console.print(table)

@app.command()
def stats():
    """Show simple stats"""
    s = db.stats()
    console.print("[bold magenta]Stats[/bold magenta]")
    console.print(f"Total: {s['total']}")
    console.print(f"Completed: {s['done']}")
    console.print(f"Pending: {s['pending']}")
    console.print(f"Overdue: {s['overdue']}")
    console.print(f"Completion rate: {s['completion_rate']}%")

if __name__ == "__main__":
    app()