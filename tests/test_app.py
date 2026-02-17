"""
Test suite for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    global activities
    activities.clear()
    activities.update({
        "Basketball Team": {
            "description": "Team training, drills, and inter-school matches",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Skill development and friendly soccer competitions",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting workshops and stage performance practice",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["amelia@mergington.edu", "lucas@mergington.edu"]
        }
    })


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the activities endpoint"""
    
    def test_get_activities_returns_all_activities(self):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        assert "Basketball Team" in data
        assert "Soccer Club" in data
        assert "Drama Club" in data
        
    def test_get_activities_structure(self):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Basketball Team"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert activity["max_participants"] == 15
        assert len(activity["participants"]) == 2


class TestSignupEndpoint:
    """Tests for the signup endpoint"""
    
    def test_signup_for_existing_activity_success(self):
        """Test successful signup for an existing activity"""
        response = client.post("/activities/Basketball Team/signup?email=test@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Signed up test@mergington.edu for Basketball Team"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" in activities_data["Basketball Team"]["participants"]
        
    def test_signup_for_nonexistent_activity(self):
        """Test signup for non-existent activity returns 404"""
        response = client.post("/activities/Nonexistent Activity/signup?email=test@mergington.edu")
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
        
    def test_signup_duplicate_participant(self):
        """Test that duplicate signup returns 400"""
        # First signup
        response1 = client.post("/activities/Basketball Team/signup?email=test@mergington.edu")
        assert response1.status_code == 200
        
        # Duplicate signup
        response2 = client.post("/activities/Basketball Team/signup?email=test@mergington.edu")
        assert response2.status_code == 400
        assert response2.json()["detail"] == "Student already signed up for this activity"
        
    def test_signup_existing_participant_returns_400(self):
        """Test signup for already registered participant returns 400"""
        response = client.post("/activities/Basketball Team/signup?email=liam@mergington.edu")
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"


class TestRemoveParticipantEndpoint:
    """Tests for the remove participant endpoint"""
    
    def test_remove_existing_participant_success(self):
        """Test successful removal of existing participant"""
        response = client.delete("/activities/Basketball Team/participants/liam@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Removed liam@mergington.edu from Basketball Team"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "liam@mergington.edu" not in activities_data["Basketball Team"]["participants"]
        
    def test_remove_participant_from_nonexistent_activity(self):
        """Test removal from non-existent activity returns 404"""
        response = client.delete("/activities/Nonexistent Activity/participants/test@mergington.edu")
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
        
    def test_remove_nonexistent_participant(self):
        """Test removal of non-existent participant returns 404"""
        response = client.delete("/activities/Basketball Team/participants/nonexistent@mergington.edu")
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found in this activity"
        
    def test_remove_all_participants(self):
        """Test removing all participants from an activity"""
        # Remove first participant
        response1 = client.delete("/activities/Basketball Team/participants/liam@mergington.edu")
        assert response1.status_code == 200
        
        # Remove second participant
        response2 = client.delete("/activities/Basketball Team/participants/ava@mergington.edu")
        assert response2.status_code == 200
        
        # Verify no participants left
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert len(activities_data["Basketball Team"]["participants"]) == 0


class TestIntegrationWorkflow:
    """Integration tests for complete workflows"""
    
    def test_complete_signup_and_removal_workflow(self):
        """Test complete workflow: signup -> verify -> remove -> verify"""
        email = "workflow@mergington.edu"
        activity = "Soccer Club"
        
        # Check initial state
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data[activity]["participants"])
        
        # Signup
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup = client.get("/activities")
        after_signup_data = after_signup.json()
        assert email in after_signup_data[activity]["participants"]
        assert len(after_signup_data[activity]["participants"]) == initial_count + 1
        
        # Remove participant
        remove_response = client.delete(f"/activities/{activity}/participants/{email}")
        assert remove_response.status_code == 200
        
        # Verify removal
        after_removal = client.get("/activities")
        after_removal_data = after_removal.json()
        assert email not in after_removal_data[activity]["participants"]
        assert len(after_removal_data[activity]["participants"]) == initial_count
        
    def test_multiple_activities_signup(self):
        """Test signing up the same student for multiple activities"""
        email = "multi@mergington.edu"
        
        # Sign up for multiple activities
        activities_to_join = ["Basketball Team", "Soccer Club", "Drama Club"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
            
        # Verify student is in all activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for activity in activities_to_join:
            assert email in activities_data[activity]["participants"]