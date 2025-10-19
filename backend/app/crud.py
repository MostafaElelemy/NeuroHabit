"""
CRUD operations for database models.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta

from app import models, schemas
from app.auth import get_password_hash


# User CRUD
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_google_id(db: Session, google_id: str) -> Optional[models.User]:
    """Get user by Google ID."""
    return db.query(models.User).filter(models.User.google_id == google_id).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user."""
    hashed_password = None
    if user.password:
        hashed_password = get_password_hash(user.password)
    
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        google_id=user.google_id,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """Update user information."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


# Habit CRUD
def get_habits(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Habit]:
    """Get all habits for a user."""
    return db.query(models.Habit).filter(
        models.Habit.user_id == user_id
    ).offset(skip).limit(limit).all()


def get_habit(db: Session, habit_id: int, user_id: int) -> Optional[models.Habit]:
    """Get a specific habit by ID for a user."""
    return db.query(models.Habit).filter(
        and_(models.Habit.id == habit_id, models.Habit.user_id == user_id)
    ).first()


def create_habit(db: Session, habit: schemas.HabitCreate, user_id: int) -> models.Habit:
    """Create a new habit."""
    db_habit = models.Habit(**habit.model_dump(), user_id=user_id)
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit


def update_habit(
    db: Session,
    habit_id: int,
    user_id: int,
    habit_update: schemas.HabitUpdate
) -> Optional[models.Habit]:
    """Update a habit."""
    db_habit = get_habit(db, habit_id, user_id)
    if not db_habit:
        return None
    
    update_data = habit_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_habit, field, value)
    
    db.commit()
    db.refresh(db_habit)
    return db_habit


def delete_habit(db: Session, habit_id: int, user_id: int) -> bool:
    """Delete a habit."""
    db_habit = get_habit(db, habit_id, user_id)
    if not db_habit:
        return False
    
    db.delete(db_habit)
    db.commit()
    return True


# Habit Event CRUD
def get_habit_events(
    db: Session,
    habit_id: int,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.HabitEvent]:
    """Get events for a specific habit."""
    # Verify habit belongs to user
    habit = get_habit(db, habit_id, user_id)
    if not habit:
        return []
    
    return db.query(models.HabitEvent).filter(
        models.HabitEvent.habit_id == habit_id
    ).order_by(models.HabitEvent.completed_at.desc()).offset(skip).limit(limit).all()


def create_habit_event(
    db: Session,
    habit_id: int,
    user_id: int,
    event: schemas.HabitEventCreate
) -> Optional[models.HabitEvent]:
    """Create a new habit event (log completion)."""
    # Verify habit belongs to user
    habit = get_habit(db, habit_id, user_id)
    if not habit:
        return None
    
    # Create event
    now = datetime.utcnow()
    db_event = models.HabitEvent(
        habit_id=habit_id,
        notes=event.notes,
        mood=event.mood,
        energy_level=event.energy_level,
        time_of_day=event.time_of_day or get_time_of_day(now),
        day_of_week=now.weekday(),
        completed_at=now
    )
    db.add(db_event)
    
    # Update streak
    update_habit_streak(db, habit)
    
    # Update pet stats
    update_pet_stats(db, user_id, 10)  # +10 XP per completion
    
    db.commit()
    db.refresh(db_event)
    return db_event


def update_habit_streak(db: Session, habit: models.Habit) -> None:
    """Update habit streak based on recent events."""
    # Get events from last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_events = db.query(models.HabitEvent).filter(
        and_(
            models.HabitEvent.habit_id == habit.id,
            models.HabitEvent.completed_at >= week_ago
        )
    ).order_by(models.HabitEvent.completed_at.desc()).all()
    
    if not recent_events:
        habit.current_streak = 0
        return
    
    # Calculate streak
    streak = 1
    last_date = recent_events[0].completed_at.date()
    
    for event in recent_events[1:]:
        event_date = event.completed_at.date()
        days_diff = (last_date - event_date).days
        
        if days_diff == 1:
            streak += 1
            last_date = event_date
        elif days_diff > 1:
            break
    
    habit.current_streak = streak
    if streak > habit.longest_streak:
        habit.longest_streak = streak


def update_pet_stats(db: Session, user_id: int, xp_gain: int) -> None:
    """Update user's pet stats."""
    user = get_user(db, user_id)
    if not user:
        return
    
    user.pet_experience += xp_gain
    user.pet_happiness = min(100, user.pet_happiness + 2)
    
    # Level up logic
    xp_for_next_level = user.pet_level * 100
    if user.pet_experience >= xp_for_next_level:
        user.pet_level += 1
        user.pet_experience -= xp_for_next_level


def get_time_of_day(dt: datetime) -> str:
    """Determine time of day from datetime."""
    hour = dt.hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


# Dashboard stats
def get_user_stats(db: Session, user_id: int) -> dict:
    """Get statistics for user dashboard."""
    habits = get_habits(db, user_id)
    active_habits = [h for h in habits if h.is_active]
    
    total_completions = db.query(func.count(models.HabitEvent.id)).join(
        models.Habit
    ).filter(models.Habit.user_id == user_id).scalar() or 0
    
    avg_streak = db.query(func.avg(models.Habit.current_streak)).filter(
        models.Habit.user_id == user_id
    ).scalar() or 0.0
    
    # Calculate completion rate (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    expected_completions = len(active_habits) * 7  # Assuming daily habits
    actual_completions = db.query(func.count(models.HabitEvent.id)).join(
        models.Habit
    ).filter(
        and_(
            models.Habit.user_id == user_id,
            models.HabitEvent.completed_at >= week_ago
        )
    ).scalar() or 0
    
    completion_rate = (actual_completions / expected_completions * 100) if expected_completions > 0 else 0.0
    
    return {
        "total_habits": len(habits),
        "active_habits": len(active_habits),
        "total_completions": total_completions,
        "average_streak": float(avg_streak),
        "completion_rate": float(completion_rate)
    }
