"""
Unit tests for habit endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app import models, schemas, crud, auth

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """Create a test user and return authentication token."""
    db = TestingSessionLocal()
    
    # Create user
    user = crud.create_user(
        db,
        schemas.UserCreate(
            email="test@example.com",
            full_name="Test User",
            password="testpass123"
        )
    )
    
    # Create token
    token = auth.create_access_token(data={"sub": user.email})
    
    db.close()
    
    return {"user": user, "token": token}


def test_create_habit(test_user):
    """Test creating a new habit."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    
    habit_data = {
        "title": "Test Habit",
        "description": "A test habit",
        "category": "health",
        "frequency": "daily",
        "target_count": 1,
        "color": "#3B82F6",
        "icon": "⭐",
        "difficulty_rating": 3,
        "importance_rating": 4
    }
    
    response = client.post("/habits", json=habit_data, headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == habit_data["title"]
    assert data["description"] == habit_data["description"]
    assert data["user_id"] == test_user["user"].id
    assert "id" in data
    assert data["current_streak"] == 0


def test_list_habits(test_user):
    """Test listing all habits for a user."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    
    # Create some habits
    for i in range(3):
        habit_data = {
            "title": f"Habit {i}",
            "description": f"Description {i}",
            "category": "health"
        }
        client.post("/habits", json=habit_data, headers=headers)
    
    # List habits
    response = client.get("/habits", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(habit["user_id"] == test_user["user"].id for habit in data)


def test_get_habit(test_user):
    """Test getting a specific habit."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    
    # Create habit
    habit_data = {"title": "Test Habit", "category": "health"}
    create_response = client.post("/habits", json=habit_data, headers=headers)
    habit_id = create_response.json()["id"]
    
    # Get habit
    response = client.get(f"/habits/{habit_id}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == habit_id
    assert data["title"] == habit_data["title"]


def test_update_habit(test_user):
    """Test updating a habit."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    
    # Create habit
    habit_data = {"title": "Original Title", "category": "health"}
    create_response = client.post("/habits", json=habit_data, headers=headers)
    habit_id = create_response.json()["id"]
    
    # Update habit
    update_data = {"title": "Updated Title", "is_active": False}
    response = client.put(f"/habits/{habit_id}", json=update_data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["is_active"] is False


def test_delete_habit(test_user):
    """Test deleting a habit."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    
    # Create habit
    habit_data = {"title": "To Delete", "category": "health"}
    create_response = client.post("/habits", json=habit_data, headers=headers)
    habit_id = create_response.json()["id"]
    
    # Delete habit
    response = client.delete(f"/habits/{habit_id}", headers=headers)
    
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get(f"/habits/{habit_id}", headers=headers)
    assert get_response.status_code == 404


def test_create_habit_event(test_user):
    """Test logging a habit completion event."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    
    # Create habit
    habit_data = {"title": "Test Habit", "category": "health"}
    create_response = client.post("/habits", json=habit_data, headers=headers)
    habit_id = create_response.json()["id"]
    
    # Create event
    event_data = {
        "notes": "Completed successfully",
        "mood": 5,
        "energy_level": 4,
        "time_of_day": "morning"
    }
    response = client.post(f"/habits/{habit_id}/events", json=event_data, headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["habit_id"] == habit_id
    assert data["notes"] == event_data["notes"]
    assert data["mood"] == event_data["mood"]


def test_unauthorized_access():
    """Test that endpoints require authentication."""
    response = client.get("/habits")
    assert response.status_code == 401


def test_habit_not_found(test_user):
    """Test accessing non-existent habit."""
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    response = client.get("/habits/99999", headers=headers)
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
