from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_unregister_participant_removes_the_student():
    activity_name = "Test Activity"
    activities[activity_name] = {
        "description": "Temporary test activity",
        "schedule": "Tuesdays",
        "max_participants": 5,
        "participants": ["student@example.com"],
    }

    response = client.delete(f"/activities/{activity_name}/signup?email=student@example.com")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed student@example.com from {activity_name}"
    assert activities[activity_name]["participants"] == []
