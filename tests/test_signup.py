"""
Tests for signup and unregister endpoints.
"""

import pytest


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_with_valid_activity_and_email_returns_200(self, client):
        """Test successful signup returns HTTP 200."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200

    def test_signup_with_valid_activity_and_email_returns_success_message(self, client):
        """Test successful signup returns confirmation message."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_adds_student_to_participants(self, client):
        """Test that signup actually adds the student to participants list."""
        email = "newstudent@mergington.edu"
        
        # Verify student is not in participants initially
        initial = client.get("/activities").json()
        assert email not in initial["Chess Club"]["participants"]
        
        # Perform signup
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify student is now in participants
        after = client.get("/activities").json()
        assert email in after["Chess Club"]["participants"]

    def test_signup_to_nonexistent_activity_returns_404(self, client):
        """Test signup to non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_returns_400(self, client):
        """Test that signing up twice with same email returns 400."""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_multiple_students_different_activities(self, client):
        """Test multiple students can sign up to different activities."""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email1}
        )
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email2}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both are enrolled
        activities = client.get("/activities").json()
        assert email1 in activities["Chess Club"]["participants"]
        assert email2 in activities["Programming Class"]["participants"]

    def test_signup_same_student_multiple_activities(self, client):
        """Test same student can sign up for multiple activities."""
        email = "versatile@mergington.edu"
        
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify student is in both activities
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]

    def test_signup_with_case_sensitive_activity_name(self, client):
        """Test that activity name matching is case-sensitive."""
        response = client.post(
            "/activities/chess club/signup",  # lowercase
            params={"email": "student@mergington.edu"}
        )
        # Should fail because "chess club" != "Chess Club"
        assert response.status_code == 404

    def test_signup_various_email_formats(self, client):
        """Test signup works with various email formats."""
        emails = [
            "simple@example.com",
            "user.name@example.co.uk",
            "first+last@example.org",
        ]
        
        for i, email in enumerate(emails):
            response = client.post(
                "/activities/Programming Class/signup",
                params={"email": email}
            )
            assert response.status_code == 200, f"Failed for email: {email}"

    def test_signup_with_whitespace_in_activity_name(self, client):
        """Test that activity names with spaces work correctly."""
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "player@mergington.edu"}
        )
        assert response.status_code == 200

    def test_signup_increments_participant_count(self, client):
        """Test that each signup increases the participant count."""
        email = "counter@mergington.edu"
        
        initial = client.get("/activities").json()
        initial_count = len(initial["Soccer Club"]["participants"])
        
        response = client.post(
            "/activities/Soccer Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        after = client.get("/activities").json()
        after_count = len(after["Soccer Club"]["participants"])
        
        assert after_count == initial_count + 1


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/signup endpoint."""

    def test_unregister_existing_student_returns_200(self, client):
        """Test that unregistering an existing student returns 200."""
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}  # Already signed up
        )
        assert response.status_code == 200

    def test_unregister_returns_success_message(self, client):
        """Test that unregister returns a confirmation message."""
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]

    def test_unregister_removes_student_from_participants(self, client):
        """Test that unregister actually removes the student."""
        email = "michael@mergington.edu"
        
        # Verify student is in participants initially
        initial = client.get("/activities").json()
        assert email in initial["Chess Club"]["participants"]
        
        # Perform unregister
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify student is no longer in participants
        after = client.get("/activities").json()
        assert email not in after["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test unregister from non-existent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404

    def test_unregister_student_not_signed_up_returns_400(self, client):
        """Test unregistering a student not signed up returns 400."""
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "notsigndup@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_then_signup_again_succeeds(self, client):
        """Test that a student can sign up again after unregistering."""
        email = "flexible@mergington.edu"
        
        # Sign up
        response1 = client.post(
            "/activities/Drama Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            "/activities/Drama Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(
            "/activities/Drama Club/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
        
        # Verify signed up
        activities = client.get("/activities").json()
        assert email in activities["Drama Club"]["participants"]

    def test_unregister_one_student_not_affecting_others(self, client):
        """Test that unregistering one student doesn't affect others."""
        # Get initial participants
        initial = client.get("/activities").json()
        chess_participants = initial["Chess Club"]["participants"].copy()
        
        # Unregister first student
        client.delete(
            "/activities/Chess Club/signup",
            params={"email": chess_participants[0]}
        )
        
        # Verify other students are still there
        after = client.get("/activities").json()
        remaining = after["Chess Club"]["participants"]
        
        # Second student should still be enrolled
        if len(chess_participants) > 1:
            assert chess_participants[1] in remaining
        assert chess_participants[0] not in remaining

    def test_unregister_multiple_from_same_activity(self, client):
        """Test unregistering multiple students from the same activity."""
        initial = client.get("/activities").json()
        drama_participants = initial["Drama Club"]["participants"].copy()
        
        # Unregister first two students
        for email in drama_participants[:2]:
            response = client.delete(
                "/activities/Drama Club/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify they're gone
        after = client.get("/activities").json()
        remaining = after["Drama Club"]["participants"]
        
        assert drama_participants[0] not in remaining
        assert drama_participants[1] not in remaining
        if len(drama_participants) > 2:
            assert drama_participants[2] in remaining

    def test_unregister_decrements_participant_count(self, client):
        """Test that each unregister decreases the participant count."""
        email_to_remove = "daniel@mergington.edu"  # In Chess Club
        
        initial = client.get("/activities").json()
        initial_count = len(initial["Chess Club"]["participants"])
        
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": email_to_remove}
        )
        assert response.status_code == 200
        
        after = client.get("/activities").json()
        after_count = len(after["Chess Club"]["participants"])
        
        assert after_count == initial_count - 1


class TestSignupUnregisterIntegration:
    """Integration tests combining signup and unregister."""

    def test_signup_signup_unregister_flow(self, client):
        """Test complete flow: signup, signup again (fails), unregister, signup again."""
        email = "flow@mergington.edu"
        activity = "Science Club"
        
        # Sign up
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Try to sign up again (should fail)
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        
        # Unregister
        response3 = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
        
        # Sign up again (should succeed)
        response4 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response4.status_code == 200
        
        # Verify final state
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]

    def test_state_isolation_between_requests(self, client):
        """Test that state changes persist correctly across multiple requests."""
        email1 = "persist1@mergington.edu"
        email2 = "persist2@mergington.edu"
        
        # Sign up email1
        client.post(
            "/activities/Art Studio/signup",
            params={"email": email1}
        )
        
        # Sign up email2
        client.post(
            "/activities/Art Studio/signup",
            params={"email": email2}
        )
        
        # Check both are present
        activities = client.get("/activities").json()
        assert email1 in activities["Art Studio"]["participants"]
        assert email2 in activities["Art Studio"]["participants"]
        
        # Unregister email1
        client.delete(
            "/activities/Art Studio/signup",
            params={"email": email1}
        )
        
        # Check only email2 remains
        activities = client.get("/activities").json()
        assert email1 not in activities["Art Studio"]["participants"]
        assert email2 in activities["Art Studio"]["participants"]
