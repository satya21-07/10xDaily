import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.api import deps
from app.models.core_models import User
from app.models.feedback import Feedback

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_feedback.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_user():
    return User(id=1, email="testuser@10xdaily.app", full_name="Test User", is_active=True, is_superuser=False)

def override_get_current_user_optional():
    return User(id=1, email="testuser@10xdaily.app", full_name="Test User", is_active=True, is_superuser=False)

def override_get_current_active_superuser():
    return User(id=99, email="admin@10xdaily.app", full_name="Admin User", is_active=True, is_superuser=True)

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[deps.get_db] = override_get_db
app.dependency_overrides[deps.get_current_user] = override_get_current_user
app.dependency_overrides[deps.get_current_active_user] = override_get_current_user
app.dependency_overrides[deps.get_current_user_optional] = override_get_current_user_optional
app.dependency_overrides[deps.get_current_active_superuser] = override_get_current_active_superuser


client = TestClient(app)

@pytest.fixture(autouse=True)
def run_around_tests():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_submit_feedback_authenticated():
    payload = {
        "feedback_type": "bug_report",
        "category": "Vocabulary",
        "subject": "Audio pronunciation not playing",
        "message": "When I tap on the speaker icon in the vocabulary flashcard, nothing happens on iOS.",
        "rating": 4,
        "device_info": "iOS 17.5 / Safari"
    }
    response = client.post("/api/v1/feedback/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["subject"] == "Audio pronunciation not playing"
    assert data["user_email"] == "testuser@10xdaily.app"
    assert data["user_name"] == "Test User"
    assert data["feedback_type"] == "bug_report"
    assert data["category"] == "Vocabulary"
    assert data["rating"] == 4
    assert data["status"] == "pending"
    assert "id" in data

def test_submit_feedback_guest():
    app.dependency_overrides[deps.get_current_user_optional] = lambda: None
    try:
        payload = {
            "feedback_type": "feature_request",
            "category": "Games",
            "subject": "Dark mode for Sudoku grid",
            "message": "Please add a high contrast dark mode option for the mini sudoku game.",
            "user_email": "guest_learner@example.com",
            "user_name": "Guest Learner",
            "rating": 5
        }
        response = client.post("/api/v1/feedback/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["user_email"] == "guest_learner@example.com"
        assert data["user_id"] is None
        assert data["subject"] == "Dark mode for Sudoku grid"
    finally:
        app.dependency_overrides[deps.get_current_user_optional] = override_get_current_user_optional

def test_submit_feedback_guest_missing_email_fails():
    app.dependency_overrides[deps.get_current_user_optional] = lambda: None
    try:
        payload = {
            "subject": "No email provided",
            "message": "This should fail because no email was provided."
        }
        response = client.post("/api/v1/feedback/", json=payload)
        assert response.status_code == 400
        assert "email address is required" in response.json()["detail"]
    finally:
        app.dependency_overrides[deps.get_current_user_optional] = override_get_current_user_optional

def test_get_my_feedback():
    # Submit 2 feedbacks
    client.post("/api/v1/feedback/", json={
        "subject": "Feedback 1",
        "message": "First feedback description."
    })
    client.post("/api/v1/feedback/", json={
        "subject": "Feedback 2",
        "message": "Second feedback description."
    })

    response = client.get("/api/v1/feedback/my-feedback")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["subject"] == "Feedback 2"

def test_admin_get_and_update_status():
    # Submit a feedback
    post_res = client.post("/api/v1/feedback/", json={
        "feedback_type": "bug_report",
        "subject": "Fix button alignment",
        "message": "The close button on modal is misaligned on small screens."
    })
    fb_id = post_res.json()["id"]

    # Admin lists feedback
    list_res = client.get("/api/v1/feedback/")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # Admin updates status
    patch_res = client.patch(f"/api/v1/feedback/{fb_id}/status", json={"status": "resolved"})
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "resolved"
