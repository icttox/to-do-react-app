# Todo App with FastAPI and React

A full-stack todo application using FastAPI for the backend and React with Material-UI for the frontend.

## Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

## Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install fastapi uvicorn sqlalchemy
```

3. Run the backend server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Frontend Setup

1. Create a new React application:
```bash
npx create-react-app todo-app
cd todo-app
```

2. Install dependencies:
```bash
npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
```

3. Replace the contents of `src/App.js` with the provided frontend code

4. Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:3000`

## Features

- Create, Read, Update, and Delete todos
- Mark todos as complete/incomplete
- Local data persistence using SQLite
- Material UI components
- Responsive design

## API Endpoints

- GET `/todos/` - Retrieve all todos
- POST `/todos/` - Create a new todo
- PUT `/todos/{todo_id}` - Update a todo
- DELETE `/todos/{todo_id}` - Delete a todo

## Project Structure

```
├── backend/
│   ├── main.py
│   └── todos.db
└── frontend/
    ├── public/
    └── src/
        ├── App.js
        └── ...
```