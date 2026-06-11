import pytest
from urllib.parse import quote
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_get_activities_returns_activity_list():
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity_adds_participant():
    activity = "Chess Club"
    email = "test_signup_student@mergington.edu"

    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    response = client.post(
        f"/activities/{quote(activity)}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    assert email in activities[activity]["participants"]

    activities[activity]["participants"].remove(email)


def test_delete_participant_unregisters_student():
    activity = "Programming Class"
    email = "test_unregister_student@mergington.edu"

    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    response = client.delete(
        f"/activities/{quote(activity)}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity}"
    assert email not in activities[activity]["participants"]


def test_duplicate_signup_is_rejected():
    activity = "Gym Class"
    email = "test_duplicate_student@mergington.edu"

    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    first_response = client.post(
        f"/activities/{quote(activity)}/signup",
        params={"email": email},
    )
    assert first_response.status_code == 200
    assert email in activities[activity]["participants"]

    second_response = client.post(
        f"/activities/{quote(activity)}/signup",
        params={"email": email},
    )
    assert second_response.status_code == 400
    assert "already signed up" in second_response.json()["detail"]

    activities[activity]["participants"].remove(email)
