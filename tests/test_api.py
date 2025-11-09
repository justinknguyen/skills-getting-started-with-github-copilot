import json

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a deep copy of initial activities dict so tests can modify safely
    import copy

    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture
def client():
    return TestClient(app)

def test_get_activities(client):
    """Test GET /activities endpoint returns all activities with correct structure."""
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    
    # Verify activity structure
    chess = data["Chess Club"]
    assert all(key in chess for key in ["description", "schedule", "max_participants", "participants"])
    assert isinstance(chess["participants"], list)

def test_signup_success(client):
    """Test successful signup to activity."""
    activity = "Chess Club"
    email = "teststudent@mergington.edu"

    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 200
    assert "Signed up" in res.json()["message"]

    # Verify participant was added
    res = client.get("/activities")
    assert email in res.json()[activity]["participants"]

def test_signup_duplicate(client):
    """Test signup fails for already registered participant."""
    activity = "Chess Club"
    email = "michael@mergington.edu"  # existing participant
    
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 400
    assert "already signed up" in res.json()["detail"].lower()

def test_signup_nonexistent_activity(client):
    """Test signup fails for non-existent activity."""
    res = client.post("/activities/NoSuchClub/signup?email=test@mergington.edu")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

def test_unregister_success(client):
    """Test successful unregistration from activity."""
    activity = "Chess Club"
    email = "daniel@mergington.edu"  # existing participant

    res = client.delete(f"/activities/{activity}/participants?email={email}")
    assert res.status_code == 200
    assert "Unregistered" in res.json()["message"]

    # Verify participant was removed
    res = client.get("/activities")
    assert email not in res.json()[activity]["participants"]

def test_unregister_not_found(client):
    """Test unregister fails for non-registered participant."""
    activity = "Chess Club"
    email = "notfound@mergington.edu"
    
    res = client.delete(f"/activities/{activity}/participants?email={email}")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

def test_unregister_nonexistent_activity(client):
    """Test unregister fails for non-existent activity."""
    res = client.delete("/activities/NoSuchClub/participants?email=test@mergington.edu")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()
