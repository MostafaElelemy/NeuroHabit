"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: Optional[str] = None
    google_id: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_premium: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    is_premium: bool
    pet_level: int
    pet_experience: int
    pet_happiness: int
    created_at: datetime

    class Config:
        from_attributes = True


# Habit Schemas
class HabitBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    frequency: str = "daily"
    target_count: int = 1
    color: str = "#3B82F6"
    icon: str = "⭐"
    difficulty_rating: int = Field(default=3, ge=1, le=5)
    importance_rating: int = Field(default=3, ge=1, le=5)


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    frequency: Optional[str] = None
    target_count: Optional[int] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None
    difficulty_rating: Optional[int] = Field(None, ge=1, le=5)
    importance_rating: Optional[int] = Field(None, ge=1, le=5)


class Habit(HabitBase):
    id: int
    user_id: int
    is_active: bool
    current_streak: int
    longest_streak: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Habit Event Schemas
class HabitEventBase(BaseModel):
    notes: Optional[str] = None
    mood: Optional[int] = Field(None, ge=1, le=5)
    energy_level: Optional[int] = Field(None, ge=1, le=5)
    time_of_day: Optional[str] = None


class HabitEventCreate(HabitEventBase):
    pass


class HabitEvent(HabitEventBase):
    id: int
    habit_id: int
    completed_at: datetime
    day_of_week: Optional[int] = None

    class Config:
        from_attributes = True


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class GoogleAuthRequest(BaseModel):
    code: str


# ML Prediction Schemas
class PredictionRequest(BaseModel):
    habit_id: int
    context: Optional[dict] = None


class FeatureImportance(BaseModel):
    feature: str
    importance: float


class PredictionResponse(BaseModel):
    risk_score: float
    success_probability: float
    feature_importance: List[FeatureImportance]
    recommendation: str


# Dashboard Schemas
class HabitStats(BaseModel):
    total_habits: int
    active_habits: int
    total_completions: int
    average_streak: float
    completion_rate: float


class DashboardResponse(BaseModel):
    user: User
    habits: List[Habit]
    stats: HabitStats
    recent_events: List[HabitEvent]
