import pytest
from app import create_app
from extensions import db


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_student_signup_and_login(client):
    signup = client.post("/auth/signup", json={
        "name": "Test Student",
        "email": "teststudent_new@test.com",
        "password": "password123",
        "role": "student"
    })

    assert signup.status_code in [201, 409]

    login = client.post("/auth/login", json={
        "email": "teststudent_new@test.com",
        "password": "password123"
    })

    assert login.status_code == 200
    assert "token" in login.get_json()


def test_protected_endpoint_without_token(client):
    response = client.post("/batches", json={
        "name": "No Token Batch"
    })

    assert response.status_code == 401


def test_post_monitoring_attendance_returns_405(client):
    response = client.post("/monitoring/attendance")

    assert response.status_code == 405


def test_trainer_creates_session(client):
    trainer_login = client.post("/auth/login", json={
        "email": "trainer@test.com",
        "password": "password123"
    })

    token = trainer_login.get_json()["token"]

    response = client.post(
        "/sessions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Pytest Session",
            "date": "2026-05-06",
            "start_time": "10:00",
            "end_time": "12:00",
            "batch_id": 1
        }
    )

    assert response.status_code in [201, 404]


def test_student_marks_attendance(client):
    student_login = client.post("/auth/login", json={
        "email": "john@test.com",
        "password": "password123"
    })

    token = student_login.get_json()["token"]

    response = client.post(
        "/attendance/mark",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "session_id": 1,
            "status": "present"
        }
    )

    assert response.status_code in [200, 201]