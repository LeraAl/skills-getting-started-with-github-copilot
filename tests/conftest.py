"""
Shared pytest fixtures and configuration for API tests.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
from copy import deepcopy

# Add src to path so we can import the actual app
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app import app as production_app


# Initial activities data (master copy for reset)
INITIAL_ACTIVITIES = {
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
        "description": "Competitive basketball league and practice",
        "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["james@mergington.edu"]
    },
    "Soccer Club": {
        "description": "Recreational and competitive soccer matches",
        "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
        "max_participants": 18,
        "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and sculpture techniques",
        "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["isabella@mergington.edu"]
    },
    "Drama Club": {
        "description": "Theater performances and acting workshops",
        "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["noah@mergington.edu", "mia@mergington.edu", "ethan@mergington.edu"]
    },
    "Science Club": {
        "description": "Hands-on experiments and scientific exploration",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["charlotte@mergington.edu"]
    },
    "Debate Team": {
        "description": "Competitive debate and public speaking",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["benjamin@mergington.edu", "amelia@mergington.edu"]
    }
}




@pytest.fixture
def app():
    """Fixture that provides the production app with reset activities for each test."""
    # Import the activities dict from the actual app
    from src.app import activities
    
    # Reset activities to initial state before each test
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    
    return production_app


@pytest.fixture
def client(app):
    """Fixture that provides a TestClient for each test."""
    return TestClient(app)


@pytest.fixture
def activity_names():
    """Fixture that provides all valid activity names."""
    return list(INITIAL_ACTIVITIES.keys())


@pytest.fixture
def activities_data():
    """Fixture that provides a deep copy of the initial activities data."""
    return deepcopy(INITIAL_ACTIVITIES)
