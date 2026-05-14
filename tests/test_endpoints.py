"""
Tests for endpoint routing and integration scenarios.
"""

import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_returns_redirect_status(self, client):
        """Test that GET / returns a redirect status code."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code in [301, 302, 303, 307, 308]

    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert "static" in response.headers.get("location", "").lower()
        assert "index.html" in response.headers.get("location", "").lower()

    def test_root_location_header_exact_value(self, client):
        """Test the exact redirect location."""
        response = client.get("/", follow_redirects=False)
        location = response.headers.get("location", "")
        assert location == "/static/index.html"

    def test_root_with_follow_redirects_reaches_static(self, client):
        """Test that following redirects from root reaches static files."""
        response = client.get("/", follow_redirects=True)
        # Should get HTML content from index.html or a successful response
        # Status 200 means we successfully reached the static file
        assert response.status_code == 200


class TestAPIIntegration:
    """Integration tests for complete API workflows."""

    def test_complete_activity_signup_workflow(self, client):
        """Test complete workflow: view activities, sign up, verify."""
        # Step 1: Get all activities
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert "Chess Club" in activities
        
        # Step 2: Sign up for an activity
        email = "workflow@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Step 3: Verify signup by getting activities again
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]

    def test_multiple_activities_independent(self, client):
        """Test that changes to one activity don't affect others."""
        email = "independent@mergington.edu"
        
        # Get initial state
        initial = client.get("/activities").json()
        initial_chess = len(initial["Chess Club"]["participants"])
        initial_prog = len(initial["Programming Class"]["participants"])
        
        # Sign up for Chess Club
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Check only Chess Club changed
        after = client.get("/activities").json()
        assert len(after["Chess Club"]["participants"]) == initial_chess + 1
        assert len(after["Programming Class"]["participants"]) == initial_prog

    def test_sequential_signup_unregister_operations(self, client):
        """Test multiple sequential sign-up and unregister operations."""
        email1 = "seq1@mergington.edu"
        email2 = "seq2@mergington.edu"
        
        # Sign up email1
        assert client.post(
            "/activities/Drama Club/signup",
            params={"email": email1}
        ).status_code == 200
        
        # Sign up email2
        assert client.post(
            "/activities/Drama Club/signup",
            params={"email": email2}
        ).status_code == 200
        
        # Unregister email1
        assert client.delete(
            "/activities/Drama Club/signup",
            params={"email": email1}
        ).status_code == 200
        
        # Verify state
        activities = client.get("/activities").json()
        assert email1 not in activities["Drama Club"]["participants"]
        assert email2 in activities["Drama Club"]["participants"]

    def test_error_handling_preserves_state(self, client):
        """Test that failed operations don't corrupt state."""
        initial = client.get("/activities").json()
        initial_count = len(initial["Debate Team"]["participants"])
        
        # Try invalid operation
        response = client.post(
            "/activities/Debate Team/signup",
            params={"email": "benjamin@mergington.edu"}  # Already signed up
        )
        assert response.status_code == 400
        
        # Verify state unchanged
        after = client.get("/activities").json()
        assert len(after["Debate Team"]["participants"]) == initial_count

    def test_all_activities_can_be_modified(self, client):
        """Test that we can perform operations on all 9 activities."""
        activities = client.get("/activities").json()
        activity_names = list(activities.keys())
        
        assert len(activity_names) == 9
        
        for i, activity_name in enumerate(activity_names):
            email = f"alltest{i}@mergington.edu"
            
            # Sign up
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
            
            # Verify
            activities = client.get("/activities").json()
            assert email in activities[activity_name]["participants"]

    def test_activity_structure_consistency(self, client):
        """Test that activity structure remains consistent through operations."""
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Initial check
        activities = client.get("/activities").json()
        for activity in activities.values():
            assert required_fields.issubset(activity.keys())
        
        # After signup
        client.post(
            "/activities/Soccer Club/signup",
            params={"email": "struct@mergington.edu"}
        )
        
        activities = client.get("/activities").json()
        for activity in activities.values():
            assert required_fields.issubset(activity.keys())

    def test_concurrent_style_operations(self, client):
        """Test multiple operations in quick succession."""
        emails = [f"concurrent{i}@mergington.edu" for i in range(5)]
        
        # Sign up all at once
        for email in emails:
            client.post(
                "/activities/Gym Class/signup",
                params={"email": email}
            )
        
        # Verify all are signed up
        activities = client.get("/activities").json()
        for email in emails:
            assert email in activities["Gym Class"]["participants"]
        
        # Unregister half of them
        for email in emails[:3]:
            client.delete(
                "/activities/Gym Class/signup",
                params={"email": email}
            )
        
        # Verify final state
        activities = client.get("/activities").json()
        for email in emails[:3]:
            assert email not in activities["Gym Class"]["participants"]
        for email in emails[3:]:
            assert email in activities["Gym Class"]["participants"]


class TestErrorScenarios:
    """Tests for error handling and edge cases."""

    def test_signup_special_characters_in_email(self, client):
        """Test signup with special characters in email."""
        emails = [
            "user+tag@example.com",
            "user_name@example.com",
            "user-name@example.com",
        ]
        
        for email in emails:
            response = client.post(
                "/activities/Basketball Team/signup",
                params={"email": email}
            )
            assert response.status_code == 200

    def test_activity_name_with_typo_fails(self, client):
        """Test that slightly wrong activity names are rejected."""
        response = client.post(
            "/activities/Chess Clubs/signup",  # Extra 's'
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404

    def test_empty_activities_response_never_happens(self, client):
        """Test that activities list is never empty."""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities) > 0

    def test_participant_list_never_none(self, client):
        """Test that participants list is never None."""
        response = client.get("/activities")
        activities = response.json()
        for activity in activities.values():
            assert activity["participants"] is not None
            assert isinstance(activity["participants"], list)
