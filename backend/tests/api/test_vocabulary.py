import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_around_tests():
    # Setup: create tables before each test
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown: drop tables after each test
    Base.metadata.drop_all(bind=engine)

def test_create_vocabulary_word():
    response = client.post(
        "/api/v1/vocabulary/",
        json={
            "word": "TestWord",
            "meaning": "A word used for testing",
            "difficulty": "Easy"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["word"] == "TestWord"
    assert "id" in data

def test_get_daily_vocabulary():
    # Insert a word first
    client.post(
        "/api/v1/vocabulary/",
        json={
            "word": "DailyWord",
            "meaning": "Daily testing",
            "difficulty": "Medium"
        }
    )
    
    response = client.get("/api/v1/vocabulary/daily")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["word"] == "DailyWord"
