"""
Tests for the feedback endpoint (/api/feedback).

Covers:
  - Valid feedback submission (201).
  - Missing ratings (400).
  - Out-of-range ratings (400).
  - Non-numeric ratings (400).
"""


def test_create_feedback_valid(client):
    response = client.post(
        "/api/feedback",
        json={
            "visitor_name": "Tester",
            "clarity_rating": 4,
            "identity_rating": 5,
            "comments": "Looks good!",
        },
    )
    assert response.status_code == 201
    assert "id" in response.json


def test_create_feedback_missing_ratings(client):
    response = client.post("/api/feedback", json={"visitor_name": "Tester"})
    assert response.status_code == 400
    assert "error" in response.json


def test_create_feedback_out_of_range(client):
    response = client.post(
        "/api/feedback",
        json={"clarity_rating": 0, "identity_rating": 6},
    )
    assert response.status_code == 400
    assert "error" in response.json


def test_create_feedback_non_numeric_ratings(client):
    response = client.post(
        "/api/feedback",
        json={"clarity_rating": "high", "identity_rating": "low"},
    )
    assert response.status_code == 400
    assert "error" in response.json
