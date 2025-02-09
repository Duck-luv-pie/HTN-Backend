import pytest
from fastapi.testclient import TestClient
from main import app
from app.database import get_db, SessionLocal
from app.models import Base, User, Scan
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

#To use the user data json provided in the HTN Backend 2025 Challenge Document
TEST_DATABASE_URL = "sqlite:///./test_database.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the database dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test database
Base.metadata.create_all(bind=engine)

# Create test client
client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Setup and teardown the test database"""
    db = TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)  #Create a clean slate before each run of testing
    Base.metadata.create_all(bind=engine)
    db.close()

#Test 1: Test User Creation
def test_create_user():
    response = client.post("/users", json={
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+1 (555) 123-4567",
        "badge_code": "test-badge-123-random"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"

#Test 2: Test Getting a User
def test_get_user():
    client.post("/users", json={
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "+1 (555) 987-6543",
        "badge_code": "test-badge-456-random"
    })
    response = client.get("/users/test-badge-456-random")
    assert response.status_code == 200
    assert response.json()["email"] == "jane@example.com"

#Test 3: Test Updating User Info
def test_update_user():
    client.post("/users", json={
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1 (555) 123-4567",
        "badge_code": "test-badge-123-random"
    })
    response = client.put("/users/test-badge-123-random", json={"phone": "+1 (555) 999-8888"})
    assert response.status_code == 200
    assert response.json()["phone"] == "+1 (555) 999-8888"

#Test 4: Test Adding a Scan
def test_scan_user():
    client.post("/users", json={
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "+1 (555) 987-6543",
        "badge_code": "test-badge-456-random"
    })
    response = client.post("/scan/test-badge-456-random", json={"activity_name": "Workshop", "activity_category": "learning"})
    assert response.status_code == 200
    assert response.json()["activity_name"] == "Workshop"

#Test 5: Test Scan Restrictions (No Double Dip)
def test_scan_limit():
    client.post("/users", json={
        "name": "User A",
        "email": "usera@example.com",
        "phone": "+1 (555) 123-4567",
        "badge_code": "test-user-a-badge"
    })

    # First scan (should work)
    response = client.post("/scan/test-user-a-badge", json={"activity_name": "Midnight Snack", "activity_category": "food"})
    assert response.status_code == 200

    # Second scan (should fail)
    response = client.post("/scan/test-user-a-badge", json={"activity_name": "Midnight Snack", "activity_category": "food"})
    assert response.status_code == 403  # Forbidden

#Test 6: Test Check-in and Check-out
def test_check_in_out():
    client.post("/users", json={
        "name": "User B",
        "email": "userb@example.com",
        "phone": "+1 (555) 987-6543",
        "badge_code": "test-user-b-badge"
    })
    
    response = client.post("/check-in/test-user-b-badge")
    assert response.status_code == 200
    assert response.json()["status"] == "IN"

    response = client.get("/check-status/test-user-b-badge")
    assert response.json()["checked_in"] == "IN"

    response = client.post("/check-out/test-user-b-badge")
    assert response.status_code == 200
    assert response.json()["status"] == "OUT"

#Test 7: Test Friend System
def test_add_friend():
    client.post("/users", json={
        "name": "Alice",
        "email": "alice@example.com",
        "phone": "+1 (555) 222-3333",
        "badge_code": "test-alice-1-badge"
    })
    client.post("/users", json={
        "name": "Bob",
        "email": "bob@example.com",
        "phone": "+1 (555) 444-5555",
        "badge_code": "test-bob-1-badge"
    })

    response = client.post("/users/test-alice-1-badge/add-friend/test-bob-1-badge")
    assert response.status_code == 200
    assert "test-bob-1-badge" in response.json()["friends"]

#Test 8: Test Activity Scans by Hour
def test_activity_scans():
    client.post("/users", json={
        "name": "Event User",
        "email": "eventuser@example.com",
        "phone": "+1 (555) 666-7777",
        "badge_code": "test-event-1-badge"
    })
    client.post("/scan/test-event-1-badge", json={"activity_name": "Dinner", "activity_category": "meal"})
    client.post("/scan/testevent-1-badge", json={"activity_name": "Dinner", "activity_category": "meal"})

    response = client.get("/activity-scans?activity_name=Dinner")
    assert response.status_code == 200
    assert len(response.json()) > 0

#Test 9: Test Duplicate User Creation
def test_duplicate_user_creation():
    client.post("/users", json={
        "name": "Duplicate User",
        "email": "duplicate@example.com",
        "phone": "+1 (555) 777-8888",
        "badge_code": "green-mountain-happy-sky"
    })

    #Try to create the same user again
    response = client.post("/users", json={
        "name": "Duplicate User",
        "email": "duplicate@example.com",
        "phone": "+1 (555) 777-8888",
        "badge_code": "green-mountain-happy-sky"
    })
    assert response.status_code == 400  
    assert "User with this email already exists" in response.json()["detail"]

#Test 10: Test Non-Existent User Retrieval
def test_get_non_existent_user():
    response = client.get("/users/blue-river-bright-sunset")
    assert response.status_code == 404  

#Test 11: Test Updating Non-Existent User
def test_update_non_existent_user():
    response = client.put("/users/red-forest-silent-moon", json={"phone": "+1 (555) 999-9999"})
    assert response.status_code == 404  

#Test 12: Test Adding a Scan for a Non-Existent User
def test_scan_non_existent_user():
    response = client.post("/scan/yellow-ocean-loud-breeze", json={"activity_name": "Workshop", "activity_category": "learning"})
    assert response.status_code == 404  

#Test 13: Test Friend Request to Non-Existent User
def test_add_friend_non_existent():
    client.post("/users", json={
        "name": "Charlie",
        "email": "charlie@example.com",
        "phone": "+1 (555) 111-2222",
        "badge_code": "purple-cloud-fast-wind"
    })

    response = client.post("/users/purple-cloud-fast-wind/add-friend/white-tree-quiet-sky")
    assert response.status_code == 404 

#Test 14: Test Self Friendship Request
def test_add_self_as_friend():
    client.post("/users", json={
        "name": "Dave",
        "email": "dave@example.com",
        "phone": "+1 (555) 333-4444",
        "badge_code": "golden-sunset-soft-rain"
    })

    response = client.post("/users/golden-sunset-soft-rain/add-friend/golden-sunset-soft-rain")
    assert response.status_code == 400  
    assert "You cannot add yourself as a friend" in response.json()["detail"]

#Test 15: Test Check-In for Non-Existent User
def test_check_in_non_existent_user():
    response = client.post("/check-in/black-mountain-strong-wave")
    assert response.status_code == 404 

#Test 16: Test Check-Out for Non-Existent User
def test_check_out_non_existent_user():
    response = client.post("/check-out/orange-river-calm-flower")
    assert response.status_code == 404  

#Test 17: Test Get Check-In Status for Non-Existent User
def test_check_status_non_existent_user():
    response = client.get("/check-status/silver-leaf-warm-breeze")
    assert response.status_code == 200  #Default to "OUT"
    assert response.json()["checked_in"] == "OUT"

#Test 18: Test Checked-In Users List
def test_checked_in_users_list():
    client.post("/users", json={
        "name": "Eve",
        "email": "eve@example.com",
        "phone": "+1 (555) 666-7777",
        "badge_code": "bright-river-shining-moon"
    })

    client.post("/users", json={
        "name": "Frank",
        "email": "frank@example.com",
        "phone": "+1 (555) 888-9999",
        "badge_code": "silent-ocean-deep-sky"
    })

    client.post("/check-in/bright-river-shining-moon")
    client.post("/check-in/silent-ocean-deep-sky")

    response = client.get("/checked-in-users")
    assert response.status_code == 200
    checked_in_users = response.json()["checked_in_users"]
    assert "bright-river-shining-moon" in checked_in_users
    assert "silent-ocean-deep-sky" in checked_in_users

#Test 19: Test Scan Limit for Multiple Activities
def test_scan_limit_multiple_activities():
    client.post("/users", json={
        "name": "Grace",
        "email": "grace@example.com",
        "phone": "+1 (555) 123-7890",
        "badge_code": "dancing-leaves-quiet-mountain"
    })

    #Scans that meet requirements
    response1 = client.post("/scan/dancing-leaves-quiet-mountain", json={"activity_name": "Lunch", "activity_category": "food"})
    response2 = client.post("/scan/dancing-leaves-quiet-mountain", json={"activity_name": "Lunch", "activity_category": "food"})
    response3 = client.post("/scan/dancing-leaves-quiet-mountain", json={"activity_name": "Lunch", "activity_category": "food"})
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200

    #Exceeding scan limit
    response4 = client.post("/scan/dancing-leaves-quiet-mountain", json={"activity_name": "Lunch", "activity_category": "food"})
    assert response4.status_code == 403

#Test 20: Test User Without Friends List
def test_user_no_friends():
    client.post("/users", json={
        "name": "Hank",
        "email": "hank@example.com",
        "phone": "+1 (555) 777-9999",
        "badge_code": "stormy-sea-bold-mountain"
    })

    response = client.get("/users/stormy-sea-bold-mountain")
    assert response.status_code == 200
    assert response.json()["friends"] == []

#Test 21: Test Invalid Badge Code Format
def test_invalid_badge_code():
    response = client.post("/users", json={
        "name": "Jack",
        "email": "jack@example.com",
        "phone": "+1 (555) 222-4444",
        "badge_code": "invalid badge format"  #Invalid format
    })
    assert response.status_code == 400  

#Test 22: Test Fetching Scans with Filters
def test_fetch_scans_with_filter():
    client.post("/users", json={
        "name": "Kara",
        "email": "kara@example.com",
        "phone": "+1 (555) 111-3333",
        "badge_code": "green-valley-windy-morning"
    })
    client.post("/scan/green-valley-windy-morning", json={"activity_name": "Breakfast", "activity_category": "meal"})
    client.post("/scan/green-valley-windy-morning", json={"activity_name": "Lunch", "activity_category": "meal"})
    client.post("/scan/green-valley-windy-morning", json={"activity_name": "Workshop", "activity_category": "learning"})

    response = client.get("/scans?activity_category=meal")
    assert response.status_code == 200
    scans = response.json()
    assert len(scans) == 2  #Only Breakfast & Lunch should be returned
