from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.core_models import User
from app.services.finance_service import get_or_generate_daily_finance_lesson

# Import calculator functions
from app.services.finance_calculator import (
    calculate_compound_interest,
    calculate_sip,
    calculate_emi,
    calculate_loan_interest,
    calculate_inflation,
    calculate_future_value,
    calculate_retirement_corpus,
    calculate_emergency_fund
)

# Import validation schemas
from app.schemas.finance import (
    DailyFinanceLessonResponse,
    CompoundInterestRequest, CompoundInterestResponse,
    SIPRequest, SIPResponse,
    EMIRequest, EMIResponse,
    LoanInterestRequest, LoanInterestResponse,
    InflationRequest, InflationResponse,
    FutureValueRequest, FutureValueResponse,
    RetirementCorpusRequest, RetirementCorpusResponse,
    EmergencyFundRequest, EmergencyFundResponse
)

router = APIRouter()

@router.get("/daily", response_model=DailyFinanceLessonResponse)
def get_daily_finance(
    country: str = Query("IN", description="Country code (e.g. IN, US, GB)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    lesson = get_or_generate_daily_finance_lesson(db, country=country)
    return {
        **lesson.content,
        "id": lesson.id,
        "lesson_date": lesson.lesson_date,
        "country": lesson.country,
        "currency": lesson.currency,
        "topic": lesson.topic
    }

@router.post("/calculator/compound-interest", response_model=CompoundInterestResponse)
def compound_interest_calc(
    req: CompoundInterestRequest,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Deterministic Compound Interest calculation."""
    return calculate_compound_interest(
        principal=req.principal,
        annual_rate=req.annual_rate,
        years=req.years,
        compounding_frequency=req.compounding_frequency
    )

@router.post("/calculator/sip", response_model=SIPResponse)
def sip_calc(
    req: SIPRequest,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Deterministic Systematic Investment Plan (SIP) calculation."""
    return calculate_sip(
        monthly_investment=req.monthly_investment,
        annual_return=req.annual_return,
        years=req.years
    )

@router.post("/calculator/emi", response_model=EMIResponse)
def emi_calc(
    req: EMIRequest,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Deterministic Equated Monthly Installment (EMI) calculation."""
    return calculate_emi(
        principal=req.principal,
        annual_interest_rate=req.annual_interest_rate,
        tenure_months=req.tenure_months
    )

@router.post("/calculator/loan-interest", response_model=LoanInterestResponse)
def loan_interest_calc(
    req: LoanInterestRequest,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Deterministic loan interest comparison calculation."""
    return calculate_loan_interest(
        principal=req.principal,
        annual_interest_rate=req.annual_interest_rate,
        tenure_years=req.tenure_years,
        compounding_frequency=req.compounding_frequency
    )

@router.post("/calculator/inflation", response_model=InflationResponse)
def inflation_calc(
    req: InflationRequest,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Deterministic Inflation / Purchasing Power calculation."""
    return calculate_inflation(
        current_amount=req.current_amount,
        inflation_rate=req.inflation_rate,
        years=req.years
    )

@router.post("/calculator/future-value", response_model=FutureValueResponse)
def future_value_calc(
    req: FutureValueRequest,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Deterministic Future Value calculation of a lump sum."""
    return calculate_future_value(
        present_value=req.present_value,
        annual_rate=req.annual_rate,
        years=req.years
    )

@router.post("/calculator/retirement-corpus", response_model=RetirementCorpusResponse)
def retirement_corpus_calc(
    req: RetirementCorpusRequest,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Deterministic inflation-adjusted Retirement Corpus target calculation."""
    return calculate_retirement_corpus(
        current_age=req.current_age,
        retirement_age=req.retirement_age,
        life_expectancy=req.life_expectancy,
        current_monthly_expenses=req.current_monthly_expenses,
        annual_inflation=req.annual_inflation,
        post_retirement_return=req.post_retirement_return
    )

@router.post("/calculator/emergency-fund", response_model=EmergencyFundResponse)
def emergency_fund_calc(
    req: EmergencyFundRequest,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Deterministic Emergency Fund target calculation."""
    return calculate_emergency_fund(
        monthly_expenses=req.monthly_expenses,
        custom_months=req.custom_months
    )
