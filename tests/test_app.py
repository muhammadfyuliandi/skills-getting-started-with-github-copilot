"""
Pytest tests for the Mergington High School Management System API

Tests follow the AAA (Arrange-Act-Assert) pattern and include an autouse
fixture that resets the activities dict before each test.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities dict to initial state before each test"""
    # Arrange: Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for all skill levels",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["sarah@mergington.edu", "james@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in plays and develop theatrical skills",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 25,
            "participants": ["ryan@mergington.edu", "grace@mergington.edu"]
        },
        "Debate Team": {
            "description": "Compete in debate tournaments and develop argumentation skills",
            "schedule": "Fridays, 3:00 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["lucas@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Tuesdays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["nina@mergington.edu", "henry@mergington.edu"]
        }
    }
    
    # Clear and restore activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup: Reset after test
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index_html(self, client):
        # Arrange: Root endpoint should redirect
        
        # Act: Make GET request to root
        response = client.get("/", follow_redirects=False)
        
        # Assert: Verify redirect status and location
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        # Arrange: Expected number of activities
        expected_count = 9
        
        # Act: Fetch all activities
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Verify all activities are returned
        assert response.status_code == 200
        assert len(data) == expected_count
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_returns_correct_activity_structure(self, client):
        # Arrange: Expected keys for each activity
        required_keys = {"description", "schedule", "max_participants", "participants"}
        
        # Act: Fetch all activities
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Verify structure of each activity
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            assert required_keys.issubset(activity_data.keys())
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_chess_club_has_initial_participants(self, client):
        # Arrange: Chess Club should have 2 participants
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act: Fetch activities
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Verify Chess Club participants
        assert data["Chess Club"]["participants"] == expected_participants


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_success(self, client):
        # Arrange: New participant to add to Chess Club
        activity_name = "Chess Club"
        email = "new_student@mergington.edu"
        
        # Act: Sign up new participant
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Assert: Verify successful signup
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
    
    def test_signup_duplicate_participant_fails(self, client):
        # Arrange: Participant already in Chess Club
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act: Try to sign up duplicate participant
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Assert: Verify error response
        assert response.status_code == 400
        assert "Student already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client):
        # Arrange: Non-existent activity name
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act: Try to sign up for non-existent activity
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Assert: Verify activity not found error
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_multiple_sequential_participants(self, client):
        # Arrange: Multiple new participants for Drama Club
        activity_name = "Drama Club"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Act: Sign up multiple participants
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
            assert response.status_code == 200
        
        # Assert: Verify all participants are added
        for email in emails:
            assert email in activities[activity_name]["participants"]


class TestRemoveParticipantEndpoint:
    """Tests for the DELETE /activities/{activity_name}/participants endpoint"""
    
    def test_remove_existing_participant_success(self, client):
        # Arrange: Participant to remove from Chess Club
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act: Remove participant
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert: Verify successful removal
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1
    
    def test_remove_nonexistent_participant_fails(self, client):
        # Arrange: Participant not in Tennis Club
        activity_name = "Tennis Club"
        email = "nonexistent@mergington.edu"
        
        # Act: Try to remove non-existent participant
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert: Verify participant not found error
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_remove_from_nonexistent_activity_fails(self, client):
        # Arrange: Non-existent activity name
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act: Try to remove from non-existent activity
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert: Verify activity not found error
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_remove_and_readd_participant(self, client):
        # Arrange: Participant in Gym Class
        activity_name = "Gym Class"
        email = "john@mergington.edu"
        
        # Act: Remove participant
        response_remove = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert: Verify removal
        assert response_remove.status_code == 200
        assert email not in activities[activity_name]["participants"]
        
        # Act: Re-add participant
        response_readd = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Assert: Verify re-addition
        assert response_readd.status_code == 200
        assert email in activities[activity_name]["participants"]


class TestActivityDataConsistency:
    """Tests for data consistency across operations"""
    
    def test_activities_modifications_persist_within_test(self, client):
        # Arrange: Initial state
        activity_name = "Programming Class"
        email = "test@mergington.edu"
        
        # Act: Signup and then fetch
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Modification persists
        assert email in data[activity_name]["participants"]
    
    def test_state_reset_between_tests_via_fixture(self, client):
        # Arrange & Act: The fixture automatically resets state
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Verify initial state is restored
        assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]
