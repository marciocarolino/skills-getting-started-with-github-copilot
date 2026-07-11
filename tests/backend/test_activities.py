from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def _sample_activity(participants=None):
    return {
        "description": "Temporary test activity",
        "schedule": "Tuesdays",
        "max_participants": 5,
        "participants": participants or [],
    }


def setup_function():
    # Keep per-test data isolated because the API uses an in-memory store.
    setup_function.original_activities = deepcopy(activities)


def teardown_function():
    activities.clear()
    activities.update(setup_function.original_activities)


def test_get_activities_returns_dictionary():
    response = client.get("/activities")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_signup_adds_student_to_activity():
    activity_name = "Test Activity"
    email = "new.student@example.com"
    activities[activity_name] = _sample_activity()

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_returns_404_for_missing_activity():
    response = client.post("/activities/Unknown%20Activity/signup?email=test@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_returns_400_for_duplicate_student():
    activity_name = "Test Activity"
    email = "student@example.com"
    activities[activity_name] = _sample_activity(participants=[email])

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_removes_student_from_activity():
    activity_name = "Test Activity"
    email = "student@example.com"
    activities[activity_name] = _sample_activity(participants=[email])

    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_unregister_returns_404_for_missing_activity():
    response = client.delete("/activities/Unknown%20Activity/signup?email=test@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_404_for_student_not_signed_up():
    activity_name = "Test Activity"
    activities[activity_name] = _sample_activity(participants=[])

    response = client.delete(f"/activities/{activity_name}/signup?email=missing@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
