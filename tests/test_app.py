from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


import pytest


@pytest.fixture(autouse=True)
def restore_activities_state():
    original_activities = deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(deepcopy(original_activities))


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_seed_data():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_adds_participant():
    response = client.post(
        "/activities/Tennis%20Club/signup",
        params={"email": "new.student@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new.student@mergington.edu for Tennis Club"}
    assert "new.student@mergington.edu" in activities["Tennis Club"]["participants"]


def test_signup_rejects_duplicate_participant():
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_remove_participant_removes_email():
    response = client.delete(
        "/activities/Art%20Studio/participants",
        params={"email": "mia@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Removed mia@mergington.edu from Art Studio"}
    assert "mia@mergington.edu" not in activities["Art Studio"]["participants"]


def test_remove_participant_rejects_unknown_email():
    response = client.delete(
        "/activities/Drama%20Club/participants",
        params={"email": "missing@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Student not signed up for this activity"}