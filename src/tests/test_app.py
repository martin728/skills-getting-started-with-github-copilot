"""
Tests for Mergington High School API

Tests are organized using the AAA pattern:
- Arrange: Set up test data and fixtures
- Act: Execute the action being tested
- Assert: Verify the results
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Arrange: Set up test client"""
    return TestClient(app)


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """Verify root endpoint redirects to static index.html"""
        # Arrange: Test client is ready
        
        # Act: Make request to root
        response = client.get("/", follow_redirects=False)
        
        # Assert: Should redirect
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Verify get_activities returns all activities in database"""
        # Arrange: Test client is ready
        
        # Act: Request all activities
        response = client.get("/activities")
        
        # Assert: Should return 200 with activities
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) > 0
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_activities_have_required_fields(self, client):
        """Verify each activity has required fields"""
        # Arrange: Test client is ready
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act: Request all activities
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Each activity has required fields
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"{activity_name} missing {field}"


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_existing_activity_succeeds(self, client):
        """Verify student can sign up for an existing activity"""
        # Arrange: Valid activity and email
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act: Sign up for activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Should succeed
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_signup_for_nonexistent_activity_fails(self, client):
        """Verify signup fails for non-existent activity"""
        # Arrange: Non-existent activity name
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act: Try to sign up for non-existent activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Should return 404
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_fails(self, client):
        """Verify student cannot sign up twice for same activity"""
        # Arrange: Student already in activity
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act: Try to sign up again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Should return 400 for duplicate
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_from_existing_activity_succeeds(self, client):
        """Verify student can unregister from an activity"""
        # Arrange: Student currently in activity
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act: Unregister from activity
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Should succeed
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_unregister_from_nonexistent_activity_fails(self, client):
        """Verify unregister fails for non-existent activity"""
        # Arrange: Non-existent activity name
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act: Try to unregister from non-existent activity
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Should return 404
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_signed_up_fails(self, client):
        """Verify unregister fails if student not signed up"""
        # Arrange: Student not in this activity
        activity_name = "Basketball Team"
        email = "michael@mergington.edu"  # Not in Basketball Team
        
        # Act: Try to unregister
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Should return 400
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]