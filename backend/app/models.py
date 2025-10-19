"""
SQLAlchemy models for NeuroHabit application.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User model for authentication and profile."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    google_id = Column(String, unique=True, nullable=True, index=True)
    hashed_password = Column(String, nullable=True)  # For non-OAuth users
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Pet stats for gamification
    pet_level = Column(Integer, default=1)
    pet_experience = Column(Integer, default=0)
    pet_happiness = Column(Integer, default=50)
    
    # Relationships
    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")


class Habit(Base):
    """Habit model for tracking user habits."""
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)  # e.g., health, productivity, social
    frequency = Column(String, default="daily")  # daily, weekly, custom
    target_count = Column(Integer, default=1)  # How many times per frequency period
    color = Column(String, default="#3B82F6")  # For UI visualization
    icon = Column(String, default="⭐")  # Emoji or icon identifier
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Streak tracking
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    
    # ML features
    difficulty_rating = Column(Integer, default=3)  # 1-5 scale
    importance_rating = Column(Integer, default=3)  # 1-5 scale
    
    # Relationships
    user = relationship("User", back_populates="habits")
    events = relationship("HabitEvent", back_populates="habit", cascade="all, delete-orphan")


class HabitEvent(Base):
    """Event model for logging habit completions."""
    __tablename__ = "habit_events"

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)
    mood = Column(Integer, nullable=True)  # 1-5 scale
    energy_level = Column(Integer, nullable=True)  # 1-5 scale
    
    # Context features for ML
    time_of_day = Column(String, nullable=True)  # morning, afternoon, evening, night
    day_of_week = Column(Integer, nullable=True)  # 0-6
    
    # Relationships
    habit = relationship("Habit", back_populates="events")


class Prediction(Base):
    """Model for storing ML predictions."""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=True)
    risk_score = Column(Float, nullable=False)  # 0-1 probability of failure
    prediction_type = Column(String, nullable=False)  # e.g., "habit_success", "streak_break"
    features_used = Column(Text, nullable=True)  # JSON string of features
    created_at = Column(DateTime(timezone=True), server_default=func.now())
