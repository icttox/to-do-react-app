from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sqlite3
import datetime

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database initialization
def init_db():
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS todos
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         title TEXT NOT NULL,
         description TEXT,
         status BOOLEAN DEFAULT FALSE,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')
    conn.commit()
    conn.close()

init_db()

# Pydantic models
class TodoBase(BaseModel):
    title: str
    description: str | None = None
    status: bool = False

class Todo(TodoBase):
    id: int
    created_at: str

# CRUD operations
@app.post("/todos/", response_model=Todo)
async def create_todo(todo: TodoBase):
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO todos (title, description, status) VALUES (?, ?, ?)",
        (todo.title, todo.description, todo.status)
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
        "created_at": todo_data[4]
    }

@app.get("/todos/", response_model=List[Todo])
async def get_todos():
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute("SELECT * FROM todos")
    todos = c.fetchall()
    conn.close()
    
    return [{
        "id": todo[0],
        "title": todo[1],
        "description": todo[2],
        "status": bool(todo[3]),
        "created_at": todo[4]
    } for todo in todos]

@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, todo: TodoBase):
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute(
        "UPDATE todos SET title = ?, description = ?, status = ? WHERE id = ?",
        (todo.title, todo.description, todo.status, todo_id)
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
        "created_at": todo_data[4]
    }

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")
    
    conn.commit()
    conn.close()
    return {"message": "Todo deleted successfully"}