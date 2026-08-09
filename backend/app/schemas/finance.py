from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field

# Daily Lesson Content schemas (used to validate Groq response)
class FinanceConcept(BaseModel):
    title: str = Field(..., description="Title of the concept")
    explanation: str = Field(..., description="Detailed explanation of the concept")

class FinanceExample(BaseModel):
    title: str = Field(..., description="Title of the example scenario")
    explanation: str = Field(..., description="Step-by-step example using locale-specific currency (e.g., INR ₹)")

class FinanceAction(BaseModel):
    title: str = Field(..., description="Title of the action item")
    description: str = Field(..., description="Detailed actionable steps")

class DailyFinanceLessonContent(BaseModel):
    topic: str = Field(..., description="Topic of the day")
    why_it_matters: str = Field(..., description="Explanation of why this topic is important")
    concepts: List[FinanceConcept] = Field(..., min_items=1, description="List of core concepts")
    example: FinanceExample = Field(..., description="Concrete, practical illustration of the concepts")
    common_mistake: str = Field(..., description="Common pitfall or misunderstanding")
    action_item: FinanceAction = Field(..., description="Today's actionable task")
    reflection: str = Field(..., description="Self-reflection question or prompt")
    disclaimer: str = Field("For educational purposes only. This is not financial advice.", description="Disclaimer")

# Database Response Schema
class DailyFinanceLessonResponse(DailyFinanceLessonContent):
    id: int
    lesson_date: date
    country: str
    currency: str
    
    class Config:
        from_attributes = True

# Calculator Schemas
class CompoundInterestRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Initial principal amount")
    annual_rate: float = Field(..., ge=0, description="Annual nominal interest rate in percent")
    years: float = Field(..., gt=0, description="Time duration in years")
    compounding_frequency: int = Field(12, gt=0, description="Compounding frequency per year (12 for monthly, 1 for annually, etc.)")

class CompoundInterestResponse(BaseModel):
    principal: float
    future_value: float
    interest_earned: float
    assumptions: dict

class SIPRequest(BaseModel):
    monthly_investment: float = Field(..., gt=0, description="Monthly investment amount")
    annual_return: float = Field(..., ge=0, description="Expected annual rate of return in percent")
    years: float = Field(..., gt=0, description="Investment tenure in years")

class SIPResponse(BaseModel):
    monthly_investment: float
    estimated_investment: float
    estimated_returns: float
    estimated_total_value: float
    assumptions: dict

class EMIRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Loan principal amount")
    annual_interest_rate: float = Field(..., ge=0, description="Annual interest rate in percent")
    tenure_months: int = Field(..., gt=0, description="Loan tenure in months")

class EMIResponse(BaseModel):
    principal: float
    monthly_emi: float
    total_payment: float
    total_interest_paid: float
    assumptions: dict

class LoanInterestRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Loan principal amount")
    annual_interest_rate: float = Field(..., ge=0, description="Annual interest rate in percent")
    tenure_years: float = Field(..., gt=0, description="Loan tenure in years")
    compounding_frequency: int = Field(12, gt=0, description="Compounding frequency per year (default 12 for monthly)")

class LoanInterestResponse(BaseModel):
    principal: float
    simple_interest: float
    compound_interest: float
    assumptions: dict

class InflationRequest(BaseModel):
    current_amount: float = Field(..., gt=0, description="Current amount of money or expense")
    inflation_rate: float = Field(..., ge=0, description="Annual inflation rate in percent")
    years: float = Field(..., gt=0, description="Number of years in the future")

class InflationResponse(BaseModel):
    current_amount: float
    future_cost: float
    reduced_purchasing_power: float
    assumptions: dict

class FutureValueRequest(BaseModel):
    present_value: float = Field(..., gt=0, description="Present lump sum value")
    annual_rate: float = Field(..., ge=0, description="Expected annual rate of return in percent")
    years: float = Field(..., gt=0, description="Number of years")

class FutureValueResponse(BaseModel):
    present_value: float
    future_value: float
    interest_earned: float
    assumptions: dict

class RetirementCorpusRequest(BaseModel):
    current_age: int = Field(..., gt=0, description="User's current age")
    retirement_age: int = Field(..., gt=0, description="Age at which user wants to retire")
    life_expectancy: int = Field(..., gt=0, description="Estimated age of life expectancy")
    current_monthly_expenses: float = Field(..., gt=0, description="Current monthly living expenses")
    annual_inflation: float = Field(..., ge=0, description="Assumed inflation rate in percent")
    post_retirement_return: float = Field(..., ge=0, description="Expected annual return rate post-retirement in percent")

class RetirementCorpusResponse(BaseModel):
    current_monthly_expenses: float
    inflated_monthly_expenses_at_retirement: float
    retirement_corpus: float
    assumptions: dict

class EmergencyFundRequest(BaseModel):
    monthly_expenses: float = Field(..., gt=0, description="Essential monthly living expenses")
    custom_months: int = Field(6, gt=0, description="Number of months of emergency expenses to target")

class EmergencyFundResponse(BaseModel):
    monthly_expenses: float
    three_month_target: float
    six_month_target: float
    custom_target: float
    assumptions: dict
