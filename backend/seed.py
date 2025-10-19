"""
Seed script to populate database with demo data.
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models, schemas, crud
from datetime import datetime, timedelta
import random


def seed_database():
    """Seed the database with demo user and habits."""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("Seeding NeuroHabit Database")
        print("=" * 60)
        
        # Create demo user
        print("\n1. Creating demo user...")
        demo_email = "demo@neurohabit.com"
        
        # Check if user already exists
        existing_user = crud.get_user_by_email(db, demo_email)
        if existing_user:
            print(f"   ✓ Demo user already exists (ID: {existing_user.id})")
            user = existing_user
        else:
            user = crud.create_user(
                db,
                schemas.UserCreate(
                    email=demo_email,
                    full_name="Demo User",
                    password="demo123"
                )
            )
            print(f"   ✓ Created demo user (ID: {user.id})")
        
        # Create demo habits
        print("\n2. Creating demo habits...")
        
        demo_habits = [
            {
                "title": "Morning Meditation",
                "description": "10 minutes of mindfulness meditation",
                "category": "health",
                "frequency": "daily",
                "target_count": 1,
                "color": "#8B5CF6",
                "icon": "🧘",
                "difficulty_rating": 2,
                "importance_rating": 5
            },
            {
                "title": "Exercise",
                "description": "30 minutes of physical activity",
                "category": "health",
                "frequency": "daily",
                "target_count": 1,
                "color": "#EF4444",
                "icon": "💪",
                "difficulty_rating": 4,
                "importance_rating": 5
            },
            {
                "title": "Read for 30 minutes",
                "description": "Read books or articles",
                "category": "learning",
                "frequency": "daily",
                "target_count": 1,
                "color": "#3B82F6",
                "icon": "📚",
                "difficulty_rating": 2,
                "importance_rating": 4
            },
            {
                "title": "Drink 8 glasses of water",
                "description": "Stay hydrated throughout the day",
                "category": "health",
                "frequency": "daily",
                "target_count": 8,
                "color": "#06B6D4",
                "icon": "💧",
                "difficulty_rating": 3,
                "importance_rating": 4
            },
            {
                "title": "Practice coding",
                "description": "Work on programming skills",
                "category": "productivity",
                "frequency": "daily",
                "target_count": 1,
                "color": "#10B981",
                "icon": "💻",
                "difficulty_rating": 3,
                "importance_rating": 5
            },
            {
                "title": "Journal",
                "description": "Write down thoughts and reflections",
                "category": "mental_health",
                "frequency": "daily",
                "target_count": 1,
                "color": "#F59E0B",
                "icon": "📝",
                "difficulty_rating": 2,
                "importance_rating": 3
            }
        ]
        
        created_habits = []
        for habit_data in demo_habits:
            # Check if habit already exists
            existing_habits = crud.get_habits(db, user.id)
            if any(h.title == habit_data["title"] for h in existing_habits):
                print(f"   - Habit '{habit_data['title']}' already exists")
                habit = next(h for h in existing_habits if h.title == habit_data["title"])
            else:
                habit = crud.create_habit(
                    db,
                    schemas.HabitCreate(**habit_data),
                    user.id
                )
                print(f"   ✓ Created habit: {habit.title}")
            
            created_habits.append(habit)
        
        # Create demo events (completions) for the last 14 days
        print("\n3. Creating demo habit events...")
        
        moods = [3, 4, 5]  # Mostly positive moods
        energy_levels = [3, 4, 5]
        times_of_day = ["morning", "afternoon", "evening"]
        
        events_created = 0
        for habit in created_habits:
            # Create events for last 14 days with some randomness
            for days_ago in range(14):
                # 80% chance of completion
                if random.random() < 0.8:
                    completed_at = datetime.utcnow() - timedelta(days=days_ago)
                    
                    event = models.HabitEvent(
                        habit_id=habit.id,
                        completed_at=completed_at,
                        notes=f"Completed on {completed_at.strftime('%Y-%m-%d')}",
                        mood=random.choice(moods),
                        energy_level=random.choice(energy_levels),
                        time_of_day=random.choice(times_of_day),
                        day_of_week=completed_at.weekday()
                    )
                    db.add(event)
                    events_created += 1
        
        db.commit()
        print(f"   ✓ Created {events_created} habit events")
        
        # Update streaks
        print("\n4. Updating habit streaks...")
        for habit in created_habits:
            crud.update_habit_streak(db, habit)
        db.commit()
        print("   ✓ Streaks updated")
        
        # Update pet stats
        print("\n5. Updating pet stats...")
        user.pet_experience = 500
        user.pet_level = 5
        user.pet_happiness = 85
        db.commit()
        print(f"   ✓ Pet stats updated (Level {user.pet_level}, {user.pet_happiness}% happiness)")
        
        print("\n" + "=" * 60)
        print("Database seeding completed successfully!")
        print("=" * 60)
        print(f"\nDemo User Credentials:")
        print(f"  Email: {demo_email}")
        print(f"  Password: demo123")
        print(f"  User ID: {user.id}")
        print(f"\nCreated {len(created_habits)} habits with {events_created} events")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
