# ✅ Command-Line To-Do Manager (Python + Typer + SQLite)

A fast, clean, colorful, and feature-rich **command-line task manager** built with  
**Python**, **Typer**, **Rich**, and **SQLite**.  
This tool helps you track tasks, deadlines, priorities, and categories — all from your terminal.

---

## 🚀 Features

- 📥 Add tasks with **priority** & **due dates**
- 🎨 Colored categories & priorities (thanks to Rich)
- 🔎 Search tasks (`search`)
- 📂 Filter by:
  - Category
  - Status (open/done)
  - Priority
  - Due-before / due-after
- 🗂 Sorting support:
  - By ID
  - By priority
  - By due date
  - By creation date
  - By status
- ✏️ Update tasks
- ✔️ Mark tasks completed
- 🗑 Delete tasks
- 🧹 Clear completed tasks
- 📊 Show task statistics (`stats`)
- 📤 Export tasks to CSV (`export`)
- 🔄 Reset the database safely (`reset --confirm`)
- 💾 Uses SQLite (lightweight & built-in)

---

## 📦 Installation

### Clone this repository:
```bash
git clone https://github.com/NewGenCoder25/CLI-Task-Manager.git
cd CLI-Task-Manager
```
### Install dependencies:
```bash
pip install -r requirements.txt
```
### Run the app:
```bash
python main.py
```

---

### 🧠 Basic Usage

#### ➕ Add a task
```bash
python main.py add "Learn Python" Learn --priority high --due 2025-02-01
```
#### 📋 Show tasks
```bash
python main.py show
```
#### 🏷 Filter tasks
```bash
python main.py show --category Code
python main.py show --priority high
python main.py show --status done
```
#### ✏️ Update a task
```bash
python main.py update 2 --task "Learn APIs" --priority medium
```
#### ✔ Mark as done
```bash
python main.py complete 3
```
#### ❌ Delete a task
```bash
python main.py delete 2
```

---

### 🔍 Search
```bash
python main.py search "python"
```

---

### 📤 Export Tasks
```bash
python main.py export tasks.csv --priority high
```

---

### 📊 Statistics
```bash
python main.py stats
```
Outputs total, completed, pending, overdue, and completion rate.


---

### 💣 Reset Database

⚠ This deletes all tasks.
```bash
python main.py reset --confirm
```

---


## 📁 Project Structure

```bash

└── CLI Task Manager/
    ├── main.py
    ├── model.py
    ├── database.py
    ├── requirements.txt
    ├── README.md
    └── LICENSE

```
---

## 🛡 License

This project is licensed under the MIT License
Feel free to use it, modify it, and share it.


---

## 🤝 Contributing

Pull requests are welcome!
Suggestions for new features are appreciated too.


---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!

---
