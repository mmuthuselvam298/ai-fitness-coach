"""API route integration tests."""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "FormFit AI" in data["name"]


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["vision_engine"]["model_ready"] is True


def test_exercises_endpoints():
    response = client.get("/api/exercises")
    assert response.status_code == 200
    exercises = response.json()
    assert len(exercises) >= 3
    ids = [e["id"] for e in exercises]
    assert "squat" in ids
    assert "pushup" in ids
    assert "bicep_curl" in ids

    # Specific detail
    single_res = client.get("/api/exercises/squat")
    assert single_res.status_code == 200
    assert single_res.json()["name"] == "Squats"

    # 404 for unknown exercise
    unknown_res = client.get("/api/exercises/invalid_exercise")
    assert unknown_res.status_code == 404


def test_workout_lifecycle():
    # 1. Start workout
    start_res = client.post(
        "/api/workouts/start",
        json={"exercise": "squat", "target_reps": 10},
    )
    assert start_res.status_code == 200
    session_data = start_res.json()
    session_id = session_data["session_id"]
    assert session_id is not None

    # 2. Finish workout
    finish_res = client.post(f"/api/workouts/{session_id}/finish")
    assert finish_res.status_code == 200
    summary = finish_res.json()
    assert summary["id"] == session_id
    assert summary["exercise"] == "squat"
    assert "what_went_well" in summary
    assert "focus_next_time" in summary

    # 3. Retrieve from history
    get_res = client.get(f"/api/workouts/{session_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == session_id


def test_analytics_endpoint():
    response = client.get("/api/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_workouts" in data
    assert "avg_form_score" in data


def test_demo_endpoints():
    samples_res = client.get("/api/demo/samples")
    assert samples_res.status_code == 200
    samples = samples_res.json()
    assert len(samples) >= 3

    # Simulation endpoint
    sim_res = client.post("/api/demo/simulate/squat?reps=2")
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert sim_data["reps_counted"] == 2
    assert sim_data["average_form_score"] > 70.0
