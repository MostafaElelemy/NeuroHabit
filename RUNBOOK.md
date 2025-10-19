# NeuroHabit - Complete Runbook

## 🚀 Quick Start Guide

This runbook provides step-by-step instructions to get NeuroHabit running locally.

---

## Prerequisites

Before starting, ensure you have:

- **Docker Desktop** installed and running
- **Docker Compose** (usually included with Docker Desktop)
- **Git** (optional, for cloning)
- At least **4GB of free RAM**
- Ports **5173**, **8000**, and **5432** available

---

## Step 1: Setup Environment Variables

1. Navigate to the project directory:
   ```bash
   cd neurohabit
   ```

2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

3. (Optional) Edit `.env` to customize settings:
   ```bash
   # On Windows
   notepad .env
   
   # On Mac/Linux
   nano .env
   ```

   **Note**: The default values work fine for local development. You only need to change them for production or if you want to use real Google OAuth.

---

## Step 2: Build Docker Images

Build all services (this may take 5-10 minutes the first time):

```bash
docker-compose build
```

**Expected output**: You should see Docker building images for `backend`, `frontend`, and pulling `postgres`.

---

## Step 3: Start All Services

Start the application stack:

```bash
docker-compose up -d
```

**What this does**:
- Starts PostgreSQL database
- Starts FastAPI backend server
- Starts React frontend development server

**Verify services are running**:
```bash
docker-compose ps
```

You should see three services running:
- `neurohabit_postgres`
- `neurohabit_backend`
- `neurohabit_frontend`

---

## Step 4: Run Database Migrations

Create the database schema:

```bash
docker-compose exec backend alembic upgrade head
```

**Expected output**: 
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial migration
```

---

## Step 5: Train the ML Model

Generate and train the LightGBM model:

```bash
docker-compose exec backend python -m app.ml.trainer
```

**Expected output**:
```
============================================================
NeuroHabit ML Model Training
============================================================
Generating synthetic training data...
Training set: 4000 samples
Test set: 1000 samples
Training LightGBM model...

Model Performance:
Accuracy: 0.8xxx
AUC-ROC: 0.8xxx

Model saved to: /app/models/habit_model.txt
============================================================
```

---

## Step 6: Seed Demo Data

Populate the database with demo user and habits:

```bash
docker-compose exec backend python seed.py
```

**Expected output**:
```
============================================================
Seeding NeuroHabit Database
============================================================

1. Creating demo user...
   ✓ Created demo user (ID: 1)

2. Creating demo habits...
   ✓ Created habit: Morning Meditation
   ✓ Created habit: Exercise
   ...

Demo User Credentials:
  Email: demo@neurohabit.com
  Password: demo123
  User ID: 1
============================================================
```

---

## Step 7: Access the Application

Open your browser and navigate to:

### 🌐 Frontend Application
**URL**: http://localhost:5173

**Login with demo credentials**:
- Email: `demo@neurohabit.com`
- Password: `demo123`

### 📚 API Documentation
**URL**: http://localhost:8000/docs

Interactive Swagger UI for testing API endpoints.

### 🔧 Backend API
**URL**: http://localhost:8000

---

## Step 8: Verify Everything Works

### Test the Frontend
1. Go to http://localhost:5173
2. Login with demo credentials
3. You should see:
   - Dashboard with stats
   - 6 demo habits
   - Habit completion graph
   - Pet with level 5

### Test the Backend
1. Go to http://localhost:8000/docs
2. Try the `/` endpoint (health check)
3. Expected response:
   ```json
   {
     "status": "healthy",
     "service": "NeuroHabit API",
     "version": "1.0.0"
   }
   ```

### Test ML Predictions
1. In the API docs, find `/predict` endpoint
2. Click "Try it out"
3. Use this request body:
   ```json
   {
     "habit_id": 1,
     "context": {}
   }
   ```
4. You should get a prediction with risk_score and recommendations

---

## Running Tests

### Backend Tests

Run Python unit tests:

```bash
docker-compose exec backend pytest -v
```

**Expected output**: All tests should pass ✓

### Frontend Tests

Run React component tests:

```bash
docker-compose exec frontend npm test
```

---

## Common Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes database data)
docker-compose down -v
```

### Access Service Shells

```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh

# PostgreSQL shell
docker-compose exec postgres psql -U neurohabit -d neurohabit
```

### Database Operations

```bash
# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback one migration
docker-compose exec backend alembic downgrade -1

# View migration history
docker-compose exec backend alembic history
```

---

## Troubleshooting

### Port Already in Use

**Error**: `Bind for 0.0.0.0:5173 failed: port is already allocated`

**Solution**:
1. Find and stop the process using the port:
   ```bash
   # Windows
   netstat -ano | findstr :5173
   taskkill /PID <PID> /F
   
   # Mac/Linux
   lsof -ti:5173 | xargs kill -9
   ```

2. Or change the port in `docker-compose.yml`

### Database Connection Failed

**Error**: Backend can't connect to database

**Solution**:
```bash
# Check if postgres is running
docker-compose ps postgres

# Restart postgres
docker-compose restart postgres

# Check postgres logs
docker-compose logs postgres
```

### Frontend Not Loading

**Error**: White screen or connection refused

**Solution**:
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

### ML Model Not Found

**Error**: `Model not found at /app/models/habit_model.txt`

**Solution**:
```bash
# Retrain the model
docker-compose exec backend python -m app.ml.trainer
```

### Permission Denied (Linux/Mac)

**Error**: Permission issues with Docker

**Solution**:
```bash
# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and back in, then:
docker-compose up -d
```

---

## Development Workflow

### Making Backend Changes

1. Edit files in `backend/app/`
2. Changes auto-reload (FastAPI --reload mode)
3. View logs: `docker-compose logs -f backend`

### Making Frontend Changes

1. Edit files in `frontend/src/`
2. Changes auto-reload (Vite HMR)
3. View in browser at http://localhost:5173

### Adding New Dependencies

**Backend**:
```bash
# Add to requirements.txt
echo "new-package==1.0.0" >> backend/requirements.txt

# Rebuild
docker-compose build backend
docker-compose up -d backend
```

**Frontend**:
```bash
# Install in container
docker-compose exec frontend npm install new-package

# Or rebuild
docker-compose build frontend
docker-compose up -d frontend
```

---

## Production Deployment Checklist

Before deploying to production:

- [ ] Change all secrets in `.env`
- [ ] Set `DEBUG=false`
- [ ] Configure real Google OAuth credentials
- [ ] Set up production PostgreSQL (AWS RDS, etc.)
- [ ] Configure HTTPS/SSL
- [ ] Set proper CORS origins
- [ ] Use production-grade WSGI server (Gunicorn)
- [ ] Set up monitoring and logging
- [ ] Configure automated backups
- [ ] Use environment-specific Docker builds
- [ ] Set up CI/CD pipeline
- [ ] Configure rate limiting
- [ ] Set up error tracking (Sentry, etc.)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     NeuroHabit Stack                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Frontend (React + TypeScript + Vite)                   │
│  ├── Port: 5173                                         │
│  ├── Tailwind CSS for styling                           │
│  ├── Recharts for visualizations                        │
│  └── Axios for API calls                                │
│                                                          │
│  Backend (FastAPI + Python)                             │
│  ├── Port: 8000                                         │
│  ├── SQLAlchemy ORM                                     │
│  ├── Alembic migrations                                 │
│  ├── JWT authentication                                 │
│  └── LightGBM ML model                                  │
│                                                          │
│  Database (PostgreSQL)                                  │
│  ├── Port: 5432                                         │
│  └── Persistent volume                                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## API Endpoints Summary

### Authentication
- `POST /auth/token` - Login
- `POST /auth/register` - Register
- `GET /auth/google` - Google OAuth

### Users
- `GET /users/me` - Get current user
- `PUT /users/me` - Update user

### Habits
- `GET /habits` - List habits
- `POST /habits` - Create habit
- `GET /habits/{id}` - Get habit
- `PUT /habits/{id}` - Update habit
- `DELETE /habits/{id}` - Delete habit

### Events
- `GET /habits/{id}/events` - List events
- `POST /habits/{id}/events` - Log completion

### ML
- `POST /predict` - Get prediction

### Dashboard
- `GET /dashboard` - Get dashboard data

---

## Support & Resources

- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173
- **Database**: localhost:5432

For issues or questions, check the logs:
```bash
docker-compose logs -f
```

---

## Success Indicators

You'll know everything is working when:

✅ All three containers are running (`docker-compose ps`)  
✅ Frontend loads at http://localhost:5173  
✅ You can login with demo credentials  
✅ Dashboard shows 6 habits with data  
✅ Pet is displayed with level 5  
✅ Graph shows completion trends  
✅ API docs accessible at http://localhost:8000/docs  
✅ ML predictions work via `/predict` endpoint  

---

**Congratulations! NeuroHabit is now running! 🎉**

Start building better habits with AI-powered insights!
