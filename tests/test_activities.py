"""
Tests for the /activities endpoint.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_all_activities_returns_200(self, client):
        """Test that GET /activities returns HTTP 200."""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_all_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary/object."""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_all_activities_contains_nine_activities(self, client, activity_names):
        """Test that all 9 activities are returned."""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities) == 9

    def test_get_all_activities_contains_all_expected_names(self, client, activity_names):
        """Test that all expected activity names are present."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name in activity_names:
            assert activity_name in activities

    def test_activity_has_required_fields(self, client):
        """Test that each activity has all required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict), f"{activity_name} data should be a dict"
            assert required_fields.issubset(activity_data.keys()), \
                f"{activity_name} missing required fields. Has: {activity_data.keys()}"

    def test_activity_description_is_string(self, client):
        """Test that activity descriptions are strings."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["description"], str), \
                f"{activity_name} description should be a string"
            assert len(activity_data["description"]) > 0, \
                f"{activity_name} description should not be empty"

    def test_activity_schedule_is_string(self, client):
        """Test that activity schedules are strings."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["schedule"], str), \
                f"{activity_name} schedule should be a string"
            assert len(activity_data["schedule"]) > 0, \
                f"{activity_name} schedule should not be empty"

    def test_activity_max_participants_is_positive_integer(self, client):
        """Test that max_participants is a positive integer."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int), \
                f"{activity_name} max_participants should be an integer"
            assert activity_data["max_participants"] > 0, \
                f"{activity_name} max_participants should be positive"

    def test_activity_participants_is_list(self, client):
        """Test that participants is a list."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"{activity_name} participants should be a list"

    def test_activity_participants_contains_strings(self, client):
        """Test that all participants are strings (email addresses)."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str), \
                    f"{activity_name} participant '{participant}' should be a string"

    def test_participants_not_exceeding_capacity(self, client):
        """Test that no activity has more participants than max_participants."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert len(activity_data["participants"]) <= activity_data["max_participants"], \
                f"{activity_name} has {len(activity_data['participants'])} participants " \
                f"but max is {activity_data['max_participants']}"

    def test_specific_activity_data_chess_club(self, client):
        """Test specific data for Chess Club activity."""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert chess_club["max_participants"] == 12
        assert "strategies" in chess_club["description"].lower() or \
               "chess" in chess_club["description"].lower()
        assert "Friday" in chess_club["schedule"]

    def test_specific_activity_initial_participants(self, client):
        """Test that activities have correct initial participant counts."""
        response = client.get("/activities")
        activities = response.json()
        
        # Known initial participant counts
        expected_participant_counts = {
            "Chess Club": 2,
            "Programming Class": 2,
            "Gym Class": 2,
            "Basketball Team": 1,
            "Soccer Club": 2,
            "Art Studio": 1,
            "Drama Club": 3,
            "Science Club": 1,
            "Debate Team": 2
        }
        
        for activity_name, expected_count in expected_participant_counts.items():
            actual_count = len(activities[activity_name]["participants"])
            assert actual_count == expected_count, \
                f"{activity_name} should have {expected_count} initial participants, " \
                f"but has {actual_count}"
