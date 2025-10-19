"""
Main FastAPI application for NeuroHabit.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import os

from app.database import get_db, engine
from app import models, schemas, crud, auth
from app.ml.predictor import get_predictor

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="NeuroHabit API",
    description="AI-powered habit tracking and coaching platform",
    version="1.0.0"
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "service": "NeuroHabit API",
        "version": "1.0.0"
    }


# Authentication endpoints
@app.post("/auth/token", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login.
    Get an access token for future requests.
    """
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/google")
async def google_auth():
    """
    Initiate Google OAuth flow.
    Returns the authorization URL to redirect the user to.
    """
    auth_url = auth.google_oauth.get_authorization_url()
    return {"authorization_url": auth_url}


@app.get("/auth/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback.
    Exchange code for token and create/login user.
    """
    try:
        # Exchange code for token
        token_data = await auth.google_oauth.exchange_code_for_token(code)
        
        # Get user info
        user_info = await auth.google_oauth.get_user_info(token_data['access_token'])
        
        # Check if user exists
        user = crud.get_user_by_google_id(db, user_info['google_id'])
        
        if not user:
            # Create new user
            user = crud.create_user(
                db,
                schemas.UserCreate(
                    email=user_info['email'],
                    full_name=user_info.get('name'),
                    google_id=user_info['google_id']
                )
            )
        
        # Create access token
        access_token = auth.create_access_token(data={"sub": user.email})
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )


@app.post("/auth/register", response_model=schemas.User)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with email and password.
    """
    # Check if user already exists
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    db_user = crud.create_user(db, user)
    return db_user


# User endpoints
@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    """Get current user information."""
    return current_user


@app.put("/users/me", response_model=schemas.User)
async def update_user_me(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    updated_user = crud.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


# Habit endpoints
@app.get("/habits", response_model=List[schemas.Habit])
async def list_habits(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all habits for the current user."""
    habits = crud.get_habits(db, current_user.id, skip=skip, limit=limit)
    return habits


@app.post("/habits", response_model=schemas.Habit, status_code=status.HTTP_201_CREATED)
async def create_habit(
    habit: schemas.HabitCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new habit."""
    return crud.create_habit(db, habit, current_user.id)


@app.get("/habits/{habit_id}", response_model=schemas.Habit)
async def get_habit(
    habit_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific habit by ID."""
    habit = crud.get_habit(db, habit_id, current_user.id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


@app.put("/habits/{habit_id}", response_model=schemas.Habit)
async def update_habit(
    habit_id: int,
    habit_update: schemas.HabitUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a habit."""
    habit = crud.update_habit(db, habit_id, current_user.id, habit_update)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


@app.delete("/habits/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a habit."""
    success = crud.delete_habit(db, habit_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Habit not found")
    return None


# Habit event endpoints
@app.get("/habits/{habit_id}/events", response_model=List[schemas.HabitEvent])
async def list_habit_events(
    habit_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all events for a specific habit."""
    events = crud.get_habit_events(db, habit_id, current_user.id, skip=skip, limit=limit)
    return events


@app.post("/habits/{habit_id}/events", response_model=schemas.HabitEvent, status_code=status.HTTP_201_CREATED)
async def create_habit_event(
    habit_id: int,
    event: schemas.HabitEventCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Log a habit completion event."""
    db_event = crud.create_habit_event(db, habit_id, current_user.id, event)
    if not db_event:
        raise HTTPException(status_code=404, detail="Habit not found")
    return db_event


# ML Prediction endpoint
@app.post("/predict", response_model=schemas.PredictionResponse)
async def predict_habit_success(
    request: schemas.PredictionRequest,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Predict habit success probability using ML model.
    Returns risk score and feature importance.
    """
    # Get habit
    habit = crud.get_habit(db, request.habit_id, current_user.id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    # Prepare data for prediction
    habit_data = {
        'difficulty_rating': habit.difficulty_rating,
        'importance_rating': habit.importance_rating,
        'current_streak': habit.current_streak,
        'longest_streak': habit.longest_streak,
        'habit_age_days': (habit.updated_at or habit.created_at).date().toordinal() - habit.created_at.date().toordinal() + 1,
        'completion_rate_7d': 0.7,  # TODO: Calculate from events
        'completion_rate_30d': 0.65,  # TODO: Calculate from events
        'avg_mood': 3.5,  # TODO: Calculate from events
        'avg_energy': 3.5,  # TODO: Calculate from events
    }
    
    user_data = {
        'pet_level': current_user.pet_level,
        'pet_happiness': current_user.pet_happiness,
    }
    
    context = request.context or {}
    
    # Get predictor and make prediction
    try:
        predictor = get_predictor()
        risk_score, feature_importance = predictor.predict(habit_data, user_data, context)
        
        # Generate recommendation
        recommendation = predictor.get_recommendation(risk_score, feature_importance)
        
        # Convert feature importance to schema format
        feature_importance_list = [
            schemas.FeatureImportance(feature=f['feature'], importance=f['importance'])
            for f in feature_importance
        ]
        
        return schemas.PredictionResponse(
            risk_score=risk_score,
            success_probability=1.0 - risk_score,
            feature_importance=feature_importance_list,
            recommendation=recommendation
        )
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model not available. Please train the model first."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


# Dashboard endpoint
@app.get("/dashboard", response_model=schemas.DashboardResponse)
async def get_dashboard(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dashboard data with habits, stats, and recent events."""
    # Get habits
    habits = crud.get_habits(db, current_user.id)
    
    # Get stats
    stats_dict = crud.get_user_stats(db, current_user.id)
    stats = schemas.HabitStats(**stats_dict)
    
    # Get recent events (last 10)
    recent_events = []
    for habit in habits[:3]:  # Get events from top 3 habits
        events = crud.get_habit_events(db, habit.id, current_user.id, limit=3)
        recent_events.extend(events)
    
    # Sort by date and limit
    recent_events.sort(key=lambda x: x.completed_at, reverse=True)
    recent_events = recent_events[:10]
    
    return schemas.DashboardResponse(
        user=current_user,
        habits=habits,
        stats=stats,
        recent_events=recent_events
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
