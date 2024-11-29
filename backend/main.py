from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from datetime import datetime
from auth import get_current_user, User, init_auth_db
from enum import Enum

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TodoBase(BaseModel):
    title: str
    description: str | None = None
    status: bool = False
    priority: PriorityLevel = PriorityLevel.MEDIUM
    due_date: Optional[str] = None

class Todo(TodoBase):
    id: int
    created_at: str
    user_id: int

def init_db():
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS todos
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         title TEXT NOT NULL,
         description TEXT,
         status BOOLEAN DEFAULT FALSE,
         priority TEXT DEFAULT 'medium',
         due_date TEXT,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         user_id INTEGER,
         FOREIGN KEY(user_id) REFERENCES users(id))
    ''')
    conn.commit()
    conn.close()

init_db()
init_auth_db()

@app.post("/todos/", response_model=Todo)
async def create_todo(todo: TodoBase, current_user: User = Depends(get_current_user)):
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO todos (title, description, status, priority, due_date, user_id) VALUES (?, ?, ?, ?, ?, ?)",
        (todo.title, todo.description, todo.status, todo.priority, todo.due_date, current_user.id)
    )
    todo_id = c.lastrowid
    conn.commit()
    
    c.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    todo_data = c.fetchone()
    conn.close()
    
    return {
        "id": todo_data[0],
        "title": todo_data[1],
        "description": todo_data[2],
        "status": bool(todo_data[3]),
        "priority": todo_data[4],
        "due_date": todo_data[5],
        "created_at": todo_data[6],
        "user_id": todo_data[7]
    }

@app.get("/todos/", response_model=List[Todo])
async def get_todos(current_user: User = Depends(get_current_user)):
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute("SELECT * FROM todos WHERE user_id = ?", (current_user.id,))
    todos = c.fetchall()
    conn.close()
    
    return [{
        "id": todo[0],
        "title": todo[1],
        "description": todo[2],
        "status": bool(todo[3]),
        "priority": todo[4],
        "due_date": todo[5],
        "created_at": todo[6],
        "user_id": todo[7]
    } for todo in todos]

@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, todo: TodoBase, current_user: User = Depends(get_current_user)):
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    
    # Verify ownership
    c.execute("SELECT user_id FROM todos WHERE id = ?", (todo_id,))
    result = c.fetchone()
    if not result or result[0] != current_user.id:
        conn.close()
        raise HTTPException(status_code=403, detail="Not authorized to update this todo")
    
    c.execute(
        """UPDATE todos 
           SET title = ?, description = ?, status = ?, priority = ?, due_date = ? 
           WHERE id = ?""",
        (todo.title, todo.description, todo.status, todo.priority, todo.due_date, todo_id)
    )
    
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")
    
    c.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    todo_data = c.fetchone()
    conn.commit()
    conn.close()
    
    return {
        "id": todo_data[0],
        "title": todo_data[1],
        "description": todo_data[2],
        "status": bool(todo_data[3]),
        "priority": todo_data[4],
        "due_date": todo_data[5],
        "created_at": todo_data[6],
        "user_id": todo_data[7]
    }

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int, current_user: User = Depends(get_current_user)):
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    
    # Verify ownership
    c.execute("SELECT user_id FROM todos WHERE id = ?", (todo_id,))
    result = c.fetchone()
    if not result or result[0] != current_user.id:
        conn.close()
        raise HTTPException(status_code=403, detail="Not authorized to delete this todo")
    
    c.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")
    
    conn.commit()
    conn.close()
    return {"message": "Todo deleted successfully"}