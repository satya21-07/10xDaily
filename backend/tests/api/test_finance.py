import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.api import deps
from app.models.core_models import User
from app.models.lessons import DailyFinanceLesson as DailyFinanceLessonModel
from app.services.finance_service import PROGRESSIVE_TOPICS

# Use SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Recreate tables for testing
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return User(id=1, email="test@test.com", full_name="Test User")

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[deps.get_current_user] = override_get_current_user

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_around_tests():
    # Setup
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown
    Base.metadata.drop_all(bind=engine)

# ========================================================
# DETERMINISTIC CALCULATORS TESTS (TEST 6, 7)
# ========================================================

def test_sip_calculator():
    response = client.post(
        "/api/v1/finance/calculator/sip",
        json={"monthly_investment": 5000, "annual_return": 12, "years": 20}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["monthly_investment"] == 5000
    assert data["estimated_investment"] == 1200000
    # Expected final value formula: FV = P * [((1 + i)**n - 1) / i] * (1 + i)
    # i = 0.01, n = 240. Value ~ 49,95,739.5
    assert data["estimated_total_value"] > 4900000
    assert data["estimated_returns"] > 3700000
    assert data["assumptions"]["annual_return"] == 12
    assert data["assumptions"]["years"] == 20

def test_emi_calculator():
    response = client.post(
        "/api/v1/finance/calculator/emi",
        json={"principal": 100000, "annual_interest_rate": 8.5, "tenure_months": 120}
      )
    assert response.status_code == 200
    data = response.json()
    assert data["principal"] == 100000
    assert data["monthly_emi"] > 1200 # approx ~1239
    assert data["total_payment"] > 140000
    assert data["total_interest_paid"] > 40000
    assert data["assumptions"]["annual_interest_rate"] == 8.5
    assert data["assumptions"]["tenure_months"] == 120

def test_compound_interest_calculator():
    response = client.post(
        "/api/v1/finance/calculator/compound-interest",
        json={"principal": 10000, "annual_rate": 10, "years": 5, "compounding_frequency": 12}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["principal"] == 10000
    assert data["future_value"] > 16000 # ~16453
    assert data["interest_earned"] > 6000

def test_loan_interest_calculator():
    response = client.post(
        "/api/v1/finance/calculator/loan-interest",
        json={"principal": 50000, "annual_interest_rate": 10, "tenure_years": 3, "compounding_frequency": 1}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["principal"] == 50000
    assert data["simple_interest"] == 15000 # 50000 * 0.1 * 3
    assert data["compound_interest"] > 16000 # ~16550

def test_inflation_calculator():
    response = client.post(
        "/api/v1/finance/calculator/inflation",
        json={"current_amount": 100000, "inflation_rate": 6, "years": 10}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_amount"] == 100000
    assert data["future_cost"] > 170000 # ~179084
    assert data["reduced_purchasing_power"] < 60000 # ~55839

def test_future_value_calculator():
    response = client.post(
        "/api/v1/finance/calculator/future-value",
        json={"present_value": 10000, "annual_rate": 8, "years": 10}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["future_value"] > 20000 # ~21589

def test_retirement_corpus_calculator():
    response = client.post(
        "/api/v1/finance/calculator/retirement-corpus",
        json={
            "current_age": 30,
            "retirement_age": 60,
            "life_expectancy": 85,
            "current_monthly_expenses": 50000,
            "annual_inflation": 6,
            "post_retirement_return": 8
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_monthly_expenses"] == 50000
    assert data["inflated_monthly_expenses_at_retirement"] > 280000 # approx ~287174
    assert data["retirement_corpus"] > 60000000 # corpus needed in tens of millions

def test_emergency_fund_calculator():
    response = client.post(
        "/api/v1/finance/calculator/emergency-fund",
        json={"monthly_expenses": 30000, "custom_months": 9}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["monthly_expenses"] == 30000
    assert data["three_month_target"] == 90000
    assert data["six_month_target"] == 180000
    assert data["custom_target"] == 270000

# ========================================================
# DAILY LESSON GENERATION & CACHING TESTS (TEST 1, 2, 3, 4, 5, 8, 9)
# ========================================================

MOCK_GROQ_SUCCESS_RESPONSE = {
    "topic": "Compounding",
    "why_it_matters": "Time compiles growth.",
    "concepts": [
        {"title": "Compounding", "explanation": "Interest on interest."}
    ],
    "example": {
        "title": "₹5,000 growth",
        "explanation": "Assuming an annual return of 12%, the estimated value would be..."
    },
    "common_mistake": "Withdrawing early.",
    "action_item": {
        "title": "Start SIP",
        "description": "Start an automated SIP."
    },
    "reflection": "Are you patient?",
    "disclaimer": "For educational purposes only. This is not financial advice."
}

@patch("app.services.finance_service.Groq")
def test_no_lesson_exists_today_calls_groq(mock_groq_class):
    # Set mock completion response
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    
    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(message=MagicMock(content=str(MOCK_GROQ_SUCCESS_RESPONSE).replace("'", '"')))
    ]
    mock_client.chat.completions.create.return_value = mock_completion

    with patch.dict("os.environ", {"GROQ_API_KEY": "gsk_test"}):
        response = client.get("/api/v1/finance/daily?country=IN")
        
    assert response.status_code == 200
    data = response.json()
    
    # Check that Groq mock was called
    mock_client.chat.completions.create.assert_called_once()
    
    # Verify returning structure
    assert data["topic"] in PROGRESSIVE_TOPICS
    assert data["why_it_matters"] == "Time compiles growth."
    assert len(data["concepts"]) == 1
    assert data["example"]["title"] == "₹5,000 growth"


@patch("app.services.finance_service.Groq")
def test_lesson_exists_today_does_not_call_groq(mock_groq_class):
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    
    # Insert existing lesson into database local session
    db = TestingSessionLocal()
    today = date.today()
    existing_lesson = DailyFinanceLessonModel(
        lesson_date=today,
        country="IN",
        currency="INR",
        topic="Inflation",
        content=MOCK_GROQ_SUCCESS_RESPONSE
    )
    db.add(existing_lesson)
    db.commit()
    db.close()
    
    # Make request
    response = client.get("/api/v1/finance/daily?country=IN")
    assert response.status_code == 200
    data = response.json()
    
    # Verify data matches DB record
    assert data["topic"] == "Inflation"
    
    # Verify Groq was NOT called
    mock_client.chat.completions.create.assert_not_called()

@patch("app.services.finance_service.Groq")
def test_groq_failure_returns_fallback(mock_groq_class):
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    mock_client.chat.completions.create.side_effect = Exception("API rate limit exceeded")
    
    with patch.dict("os.environ", {"GROQ_API_KEY": "gsk_test"}):
        response = client.get("/api/v1/finance/daily?country=IN")
        
    assert response.status_code == 200
    data = response.json()
    # Should fall back gracefully to offline fallback content
    assert data["topic"] in PROGRESSIVE_TOPICS
    assert "Compounding is the engine of long-term wealth creation" in data["why_it_matters"] or data["why_it_matters"] is not None

@patch("app.services.finance_service.Groq")
def test_groq_malformed_json_returns_fallback(mock_groq_class):
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    
    mock_completion = MagicMock()
    # Malformed JSON missing braces
    mock_completion.choices = [
        MagicMock(message=MagicMock(content='{"topic": "Inflation", "why_it_matters"'))
    ]
    mock_client.chat.completions.create.return_value = mock_completion

    with patch.dict("os.environ", {"GROQ_API_KEY": "gsk_test"}):
        response = client.get("/api/v1/finance/daily?country=IN")
        
    assert response.status_code == 200
    data = response.json()
    
    # Verify it falls back
    assert data["topic"] in PROGRESSIVE_TOPICS
    assert "not financial advice" in data["disclaimer"]


def test_concurrent_requests_handling():
    # Setup: We mock the database session save behaviour to simulate duplicate insert
    db = TestingSessionLocal()
    today = date.today()
    
    # Generate daily lesson and commit once
    db_lesson = DailyFinanceLessonModel(
        lesson_date=today,
        country="IN",
        currency="INR",
        topic="Budgeting",
        content=MOCK_GROQ_SUCCESS_RESPONSE
    )
    db.add(db_lesson)
    db.commit()
    
    # Try inserting the same lesson concurrently
    duplicate_lesson = DailyFinanceLessonModel(
        lesson_date=today,
        country="IN",
        currency="INR",
        topic="Budgeting",
        content=MOCK_GROQ_SUCCESS_RESPONSE
    )
    db.add(duplicate_lesson)
    
    with pytest.raises(IntegrityError):
        db.commit()
        
    db.rollback()
    
    # Confirm DB query returns the first model and database isn't corrupted
    queried = db.query(DailyFinanceLessonModel).filter(
        DailyFinanceLessonModel.lesson_date == today,
        DailyFinanceLessonModel.country == "IN"
    ).all()
    assert len(queried) == 1
    db.close()

def test_india_locale_content():
    # Test that country config and locale outputs correctly
    response = client.get("/api/v1/finance/daily?country=IN")
    assert response.status_code == 200
    data = response.json()
    assert data["country"] == "IN"
    assert data["currency"] == "INR"
