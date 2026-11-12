"""Integration tests for the MealBridge FastAPI Dispatcher web application."""

import pytest
from fastapi.testclient import TestClient
from src.web.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_dashboard_renders_cleanly(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "MealBridge" in response.text
    assert "Dispatch Board" in response.text


def test_voice_intake_and_proposals_api(client):
    # Reset first
    client.post("/api/reset")

    # Send voice cancellation
    res = client.post(
        "/api/voice-intake",
        data={"transcript": "Marcus V01 here, my car broke down on 4th street, can't deliver today."},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["update"]["intent"] == "cancel"
    assert data["proposals_count"] >= 20

    # 1-Click Approve proposals
    app_res = client.post("/api/approve-all")
    assert app_res.status_code == 200
    app_data = app_res.json()
    assert app_data["status"] == "success"
    assert app_data["reassigned_count"] == 18
    assert app_data["escalated_count"] >= 2


def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "MealBridge"


def test_audit_api_returns_pass(client):
    res = client.get("/api/audit")
    assert res.status_code == 200
    data = res.json()
    assert data["passed"] is True
    assert data["violations_count"] == 0
