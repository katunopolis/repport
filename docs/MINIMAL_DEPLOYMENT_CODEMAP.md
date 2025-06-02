# REPPORT PROJECT CODEBASE MAP

This document provides a comprehensive map of the Repport helpdesk ticketing system codebase. It can be used to understand the project structure and rebuild it from scratch if needed.

## Project Structure

```
repport/
├── backend/                 # Python FastAPI backend
│   ├── app/                 # Main application code
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── core/            # Configuration, database setup
│   │   ├── models/          # SQLModel data models
│   │   └── api/             # API route definitions
│   ├── scripts/             # Utility scripts
│   ├── data/                # Database files
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Backend container definition
├── frontend/                # React frontend
│   ├── src/                 # React source code
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page-level components
│   │   ├── api/             # API client code
│   │   ├── App.tsx          # Main component
│   │   └── index.tsx        # Entry point
│   ├── public/              # Static assets
│   ├── package.json         # JS dependencies
│   └── Dockerfile           # Frontend container definition
├── docs/                    # Documentation
└── docker-compose.yml       # Container orchestration
```

## Backend Architecture

### Core Configuration and Setup

**app/core/config.py**
```python
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Repport Helpdesk"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:80"]
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

**app/core/database.py**
```python
from sqlmodel import create_engine, SQLModel, Session
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

async def init_db():
    # Create all tables
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

### Main Application Entry Point

**app/main.py**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import tickets, auth
from app.core.database import init_db
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(tickets.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    await init_db()

# Health endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "version": "1.0.0",
        "api_prefix": settings.API_V1_STR
    }
```

### Database Models

**app/models/user.py**
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from pydantic import EmailStr
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    tickets: List["Ticket"] = Relationship(back_populates="created_by_user")
```

**app/models/ticket.py**
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    status: str = "open"  # open, in_progress, closed
    is_public: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: int = Field(foreign_key="user.id")
    created_by_user: "User" = Relationship(back_populates="tickets")
    responses: List["TicketResponse"] = Relationship(back_populates="ticket")

class TicketResponse(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ticket_id: int = Field(foreign_key="ticket.id")
    ticket: Ticket = Relationship(back_populates="responses")
    response: str
    responded_at: datetime = Field(default_factory=datetime.now)
    responded_by: int = Field(foreign_key="user.id")
    responded_by_user: "User" = Relationship()
```

### API Endpoints

**app/api/auth.py**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings
from app.core.database import get_session
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/signup")
async def signup(email: str, password: str, session: Session = Depends(get_session)):
    # Check if user exists
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(password)
    user = User(email=email, hashed_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Create and return access token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user": user}
```

**app/api/tickets.py**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.ticket import Ticket, TicketResponse
from app.models.user import User
from app.api.auth import get_current_active_user
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/tickets", tags=["tickets"])

class TicketCreate(BaseModel):
    title: str
    description: str
    status: str = "open"
    is_public: bool = False

class TicketResponseCreate(BaseModel):
    response: str

@router.get("/", response_model=List[Ticket])
async def get_tickets(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.is_superuser:
        # Admins see all tickets
        tickets = session.exec(select(Ticket)).all()
    else:
        # Regular users see their own tickets + public tickets
        tickets = session.exec(
            select(Ticket).where(
                (Ticket.created_by == current_user.id) | (Ticket.is_public == True)
            )
        ).all()
    return tickets

@router.post("/", response_model=Ticket)
async def create_ticket(
    ticket_data: TicketCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    # Create new ticket
    ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        status=ticket_data.status,
        is_public=ticket_data.is_public,
        created_by=current_user.id
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket

@router.get("/{ticket_id}", response_model=Ticket)
async def get_ticket(
    ticket_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check access - admin or ticket owner or public ticket
    if not current_user.is_superuser and ticket.created_by != current_user.id and not ticket.is_public:
        raise HTTPException(status_code=403, detail="Not authorized to view this ticket")
    
    return ticket

@router.post("/{ticket_id}/respond", response_model=Ticket)
async def respond_to_ticket(
    ticket_id: int,
    response_data: TicketResponseCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    # Only admins can respond to tickets
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can respond to tickets")
    
    # Get ticket
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Create response
    ticket_response = TicketResponse(
        ticket_id=ticket.id,
        response=response_data.response,
        responded_by=current_user.id
    )
    session.add(ticket_response)
    
    # Update ticket status to in_progress if it was open
    if ticket.status == "open":
        ticket.status = "in_progress"
    
    session.commit()
    session.refresh(ticket)
    return ticket

@router.put("/{ticket_id}/toggle-public", response_model=Ticket)
async def toggle_ticket_public(
    ticket_id: int,
    is_public: bool,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    # Only admins can change visibility
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can change ticket visibility")
    
    # Get ticket
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Update visibility
    ticket.is_public = is_public
    session.commit()
    session.refresh(ticket)
    return ticket

@router.put("/{ticket_id}/solve", response_model=Ticket)
async def solve_ticket(
    ticket_id: int,
    response_data: TicketResponseCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    # Only admins can solve tickets
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can solve tickets")
    
    # Get ticket
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Create final response
    ticket_response = TicketResponse(
        ticket_id=ticket.id,
        response=response_data.response,
        responded_by=current_user.id
    )
    session.add(ticket_response)
    
    # Mark ticket as closed
    ticket.status = "closed"
    
    session.commit()
    session.refresh(ticket)
    return ticket
```

## Frontend Architecture

### Key Components

**src/App.tsx**
```tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';

// Import pages
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import TicketPage from './pages/TicketPage';
import NotFoundPage from './pages/NotFoundPage';

const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
    background: { default: '#f5f5f5' },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/dashboard" element={<UserDashboard />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/ticket/:id" element={<TicketPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
```

**src/api/api.ts**
```typescript
import axios from 'axios';
import { config } from '../config';

// Create axios instance with base URL
const api = axios.create({
  baseURL: config.apiUrl,
});

// Add request interceptor to include auth token in headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth API
export const login = async (email: string, password: string) => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  
  return api.post('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
};

export const signup = async (email: string, password: string) => {
  return api.post('/auth/signup', { email, password });
};

export const getCurrentUser = async () => {
  return api.get('/users/me');
};

// Tickets API
export const getTickets = async () => {
  return api.get('/tickets/');
};

export const getTicket = async (id: number) => {
  return api.get(`/tickets/${id}`);
};

export const createTicket = async (title: string, description: string, status: string = 'open', is_public: boolean = false) => {
  return api.post('/tickets/', { title, description, status, is_public });
};

export const respondToTicket = async (id: number, response: string) => {
  return api.post(`/tickets/${id}/respond`, { response });
};

export const toggleTicketPublic = async (id: number, is_public: boolean) => {
  return api.put(`/tickets/${id}/toggle-public`, { is_public });
};

export const solveTicket = async (id: number, response: string) => {
  return api.put(`/tickets/${id}/solve`, { response });
};
```

**src/pages/LoginPage.tsx**
```tsx
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  Container, Box, TextField, Button, Typography, Alert,
  Paper, Avatar, Grid
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { login } from '../api/api';

const LoginPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await login(email, password);
      
      // Store token in localStorage
      localStorage.setItem('token', response.data.access_token);
      
      // Redirect to dashboard
      const userData = await getCurrentUser();
      if (userData.data.is_superuser) {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      setError('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
          <Avatar sx={{ bgcolor: 'primary.main', margin: '0 auto' }}>
            <LockOutlinedIcon />
          </Avatar>
          <Typography component="h1" variant="h5" align="center" sx={{ mt: 1 }}>
            Log in to Repport
          </Typography>
          
          {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
          
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              autoFocus
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? 'Logging in...' : 'Log In'}
            </Button>
            <Grid container>
              <Grid item xs>
                <Link to="/forgot-password">Forgot password?</Link>
              </Grid>
              <Grid item>
                <Link to="/signup">Don't have an account? Sign Up</Link>
              </Grid>
            </Grid>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default LoginPage;
```

## Docker Setup and Deployment

**Dockerfile (Backend)**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Dockerfile (Frontend)**
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml**
```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend:/app
      - ./backend/data:/app/data
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    volumes:
      - ./frontend:/app:ro
      - /app/node_modules
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:8000
```

## Environment Variables

### Backend (.env)
```
# FastAPI settings
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./data/repport.db

# CORS settings
CORS_ORIGINS=http://localhost:3000,http://localhost:80

# Email settings (for password resets - optional)
MAIL_USERNAME=email@example.com
MAIL_PASSWORD=your-mail-password
MAIL_FROM=noreply@example.com
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_TLS=True
MAIL_SSL=False
```

## Critical Code Interactions

1. **Authentication Flow**:
   - Frontend: User submits login form → call login API → store JWT token in localStorage
   - Backend: Verify credentials → generate JWT token → return token
   - Subsequent API calls include the JWT token in the Authorization header

2. **Ticket Management Flow**:
   - Create Ticket: User submits form → API call → database entry created
   - List Tickets: API fetches tickets filtered by access level → display in frontend
   - Respond to Ticket: Admin submits response → API call → add response to ticket
   - Toggle Public: Admin toggles visibility → API call → update ticket's is_public field
   - Solve Ticket: Admin submits final response → API call → change status to 'closed'

3. **User Management Flow**:
   - Signup: User enters email/password → API call → create user in database
   - Admin View: Load users list from API → display in admin dashboard
   - Promote User: Admin clicks promote button → API call → update user's is_superuser field

## Rebuild Instructions

1. **Setup Directory Structure**:
   ```
   mkdir -p repport/{backend/{app/{api,core,models},data,scripts},frontend/{public,src/{api,components,pages}},docs}
   ```

2. **Backend Implementation**:
   - Create the Python files as described in this document
   - Install dependencies: `pip install fastapi uvicorn sqlmodel pydantic python-jose[cryptography] passlib[bcrypt]`

3. **Frontend Implementation**:
   - Set up React with TypeScript: `npx create-react-app frontend --template typescript`
   - Install dependencies: `npm install react-router-dom @mui/material @mui/icons-material axios`
   - Create the component files as described in this document

4. **Docker Setup**:
   - Create Dockerfiles and docker-compose.yml as described
   - Run with `docker-compose up --build`

5. **First Admin User**:
   - Use the script create_admin.py in backend/scripts to create the first admin user
   - Access the admin interface at http://localhost:3000/admin

## API Endpoints Summary

| Method | Endpoint                       | Description                   | Authentication  |
|--------|--------------------------------|-------------------------------|----------------|
| GET    | /health                        | API health check              | None           |
| POST   | /api/v1/auth/login             | User login                    | None           |
| POST   | /api/v1/auth/signup            | User registration             | None           |
| GET    | /api/v1/users/me               | Get current user              | JWT Token      |
| GET    | /api/v1/tickets/               | List tickets                  | JWT Token      |
| POST   | /api/v1/tickets/               | Create ticket                 | JWT Token      |
| GET    | /api/v1/tickets/{id}           | Get specific ticket           | JWT Token      |
| POST   | /api/v1/tickets/{id}/respond   | Respond to ticket             | JWT Token (Admin) |
| PUT    | /api/v1/tickets/{id}/toggle-public | Toggle ticket visibility  | JWT Token (Admin) |
| PUT    | /api/v1/tickets/{id}/solve     | Solve and close ticket        | JWT Token (Admin) |
</rewritten_file> 