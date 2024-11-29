import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Checkbox,
  Paper,
  Box,
  ThemeProvider,
  createTheme,
  CssBaseline,
  CircularProgress,
  Snackbar,
  Alert,
} from '@mui/material';
import { Delete as DeleteIcon, Edit as EditIcon } from '@mui/icons-material';

const theme = createTheme({
  palette: {
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#ff4081',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          transition: 'transform 0.2s, box-shadow 0.2s',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
  },
});

const API_URL = 'http://localhost:8000';

function App() {
  const [todos, setTodos] = useState([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [editingTodo, setEditingTodo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    fetchTodos();
  }, []);

  const fetchTodos = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/todos/`);
      const data = await response.json();
      setTodos(data);
    } catch (error) {
      showSnackbar('Error fetching todos', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    const todoData = {
      title,
      description,
      status: false
    };

    setLoading(true);
    try {
      if (editingTodo) {
        await fetch(`${API_URL}/todos/${editingTodo.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(todoData)
        });
        showSnackbar('Todo updated successfully');
        setEditingTodo(null);
      } else {
        await fetch(`${API_URL}/todos/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(todoData)
        });
        showSnackbar('Todo created successfully');
      }
      setTitle('');
      setDescription('');
      fetchTodos();
    } catch (error) {
      showSnackbar('Error saving todo', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await fetch(`${API_URL}/todos/${id}`, { method: 'DELETE' });
      showSnackbar('Todo deleted successfully');
      fetchTodos();
    } catch (error) {
      showSnackbar('Error deleting todo', 'error');
    }
  };

  const handleEdit = (todo) => {
    setEditingTodo(todo);
    setTitle(todo.title);
    setDescription(todo.description || '');
  };

  const handleToggleStatus = async (todo) => {
    try {
      await fetch(`${API_URL}/todos/${todo.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...todo, status: !todo.status })
      });
      fetchTodos();
      showSnackbar('Todo status updated');
    } catch (error) {
      showSnackbar('Error updating todo status', 'error');
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="md" sx={{ py: 6 }}>
        <Typography 
          variant="h3" 
          component="h1" 
          gutterBottom 
          align="center"
          sx={{ 
            fontWeight: 700,
            color: 'primary.main',
            mb: 4
          }}
        >
          Todo App
        </Typography>

        <Paper 
          elevation={3} 
          sx={{ 
            p: 4, 
            mb: 4,
            borderRadius: 2
          }}
        >
          <form onSubmit={handleSubmit}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <TextField
                label="Title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                variant="outlined"
                fullWidth
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              />
              <TextField
                label="Description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                multiline
                rows={3}
                variant="outlined"
                fullWidth
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              />
              <Button
                type="submit"
                variant="contained"
                size="large"
                disabled={loading}
                sx={{ 
                  py: 1.5,
                  px: 4,
                  alignSelf: 'flex-start'
                }}
              >
                {loading ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  editingTodo ? 'Update Todo' : 'Add Todo'
                )}
              </Button>
            </Box>
          </form>
        </Paper>

        {loading && !todos.length ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <List>
            {todos.map((todo) => (
              <ListItem
                key={todo.id}
                sx={{
                  mb: 2,
                  bgcolor: 'background.paper',
                  borderRadius: 2,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                }}
              >
                <Checkbox
                  checked={todo.status}
                  onChange={() => handleToggleStatus(todo)}
                  sx={{
                    '&.Mui-checked': {
                      color: 'primary.main',
                    },
                  }}
                />
                <ListItemText
                  primary={
                    <Typography
                      variant="h6"
                      sx={{
                        textDecoration: todo.status ? 'line-through' : 'none',
                        color: todo.status ? 'text.secondary' : 'text.primary',
                      }}
                    >
                      {todo.title}
                    </Typography>
                  }
                  secondary={
                    <Typography
                      variant="body2"
                      sx={{
                        color: 'text.secondary',
                        mt: 0.5,
                      }}
                    >
                      {todo.description}
                    </Typography>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    onClick={() => handleEdit(todo)}
                    sx={{ 
                      mr: 1,
                      color: 'primary.main',
                      '&:hover': { 
                        bgcolor: 'primary.light',
                        color: 'primary.contrastText',
                      }
                    }}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    edge="end"
                    onClick={() => handleDelete(todo.id)}
                    sx={{ 
                      color: 'error.main',
                      '&:hover': { 
                        bgcolor: 'error.light',
                        color: 'error.contrastText',
                      }
                    }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        )}
        
        <Snackbar 
          open={snackbar.open} 
          autoHideDuration={3000} 
          onClose={handleSnackbarClose}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert 
            onClose={handleSnackbarClose} 
            severity={snackbar.severity}
            elevation={6}
            variant="filled"
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Container>
    </ThemeProvider>
  );
}

export default App;