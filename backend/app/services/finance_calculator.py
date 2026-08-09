import math

def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    years: float,
    compounding_frequency: int = 12
) -> dict:
    """
    A = P * (1 + r/n)**(n*t)
    """
    r = annual_rate / 100.0
    n = compounding_frequency
    t = years
    future_value = principal * ((1 + r / n) ** (n * t))
    interest_earned = future_value - principal
    
    return {
        "principal": round(principal, 2),
        "future_value": round(future_value, 2),
        "interest_earned": round(interest_earned, 2),
        "assumptions": {
            "annual_rate": annual_rate,
            "compounding_frequency_per_year": compounding_frequency,
            "years": years
        }
    }

def calculate_sip(
    monthly_investment: float,
    annual_return: float,
    years: float
) -> dict:
    """
    FV = P * [((1 + i)**n - 1) / i] * (1 + i)
    """
    i = (annual_return / 100.0) / 12.0
    n = years * 12
    
    if i == 0:
        future_value = monthly_investment * n
    else:
        future_value = monthly_investment * (((1 + i) ** n - 1) / i) * (1 + i)
        
    estimated_investment = monthly_investment * n
    estimated_returns = future_value - estimated_investment
    
    return {
        "monthly_investment": round(monthly_investment, 2),
        "estimated_investment": round(estimated_investment, 2),
        "estimated_returns": round(estimated_returns, 2),
        "estimated_total_value": round(future_value, 2),
        "assumptions": {
            "annual_return": annual_return,
            "years": years
        }
    }

def calculate_emi(
    principal: float,
    annual_interest_rate: float,
    tenure_months: int
) -> dict:
    """
    EMI = P * r * (1+r)**n / ((1+r)**n - 1)
    """
    r = (annual_interest_rate / 100.0) / 12.0
    n = tenure_months
    
    if r == 0:
        emi = principal / n
    else:
        emi = principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
        
    total_payment = emi * n
    total_interest_paid = total_payment - principal
    
    return {
        "principal": round(principal, 2),
        "monthly_emi": round(emi, 2),
        "total_payment": round(total_payment, 2),
        "total_interest_paid": round(total_interest_paid, 2),
        "assumptions": {
            "annual_interest_rate": annual_interest_rate,
            "tenure_months": tenure_months
        }
    }

def calculate_loan_interest(
    principal: float,
    annual_interest_rate: float,
    tenure_years: float,
    compounding_frequency: int = 12
) -> dict:
    """
    Calculates Simple Interest and Compound Interest for comparison.
    """
    simple_interest = principal * (annual_interest_rate / 100.0) * tenure_years
    
    r = annual_interest_rate / 100.0
    n = compounding_frequency
    t = tenure_years
    compound_amount = principal * ((1 + r / n) ** (n * t))
    compound_interest = compound_amount - principal
    
    return {
        "principal": round(principal, 2),
        "simple_interest": round(simple_interest, 2),
        "compound_interest": round(compound_interest, 2),
        "assumptions": {
            "annual_interest_rate": annual_interest_rate,
            "tenure_years": tenure_years,
            "compounding_frequency": compounding_frequency
        }
    }

def calculate_inflation(
    current_amount: float,
    inflation_rate: float,
    years: float
) -> dict:
    """
    Future cost: FV = PV * (1 + r)**t
    Reduced purchasing power: PV = FV / (1 + r)**t
    """
    r = inflation_rate / 100.0
    t = years
    future_cost = current_amount * ((1 + r) ** t)
    reduced_purchasing_power = current_amount / ((1 + r) ** t)
    
    return {
        "current_amount": round(current_amount, 2),
        "future_cost": round(future_cost, 2),
        "reduced_purchasing_power": round(reduced_purchasing_power, 2),
        "assumptions": {
            "inflation_rate": inflation_rate,
            "years": years
        }
    }

def calculate_future_value(
    present_value: float,
    annual_rate: float,
    years: float
) -> dict:
    """
    FV = PV * (1 + r)**t
    """
    r = annual_rate / 100.0
    t = years
    future_value = present_value * ((1 + r) ** t)
    interest_earned = future_value - present_value
    
    return {
        "present_value": round(present_value, 2),
        "future_value": round(future_value, 2),
        "interest_earned": round(interest_earned, 2),
        "assumptions": {
            "annual_rate": annual_rate,
            "years": years
        }
    }

def calculate_retirement_corpus(
    current_age: int,
    retirement_age: int,
    life_expectancy: int,
    current_monthly_expenses: float,
    annual_inflation: float,
    post_retirement_return: float
) -> dict:
    """
    Retirement corpus calculation taking inflation and post-retirement returns into account.
    """
    years_to_retire = retirement_age - current_age
    years_in_retirement = life_expectancy - retirement_age
    
    if years_to_retire < 0 or years_in_retirement <= 0:
        return {
            "current_monthly_expenses": current_monthly_expenses,
            "inflated_monthly_expenses_at_retirement": 0,
            "retirement_corpus": 0,
            "assumptions": {
                "current_age": current_age,
                "retirement_age": retirement_age,
                "life_expectancy": life_expectancy,
                "annual_inflation": annual_inflation,
                "post_retirement_return": post_retirement_return,
                "years_to_retire": max(0, years_to_retire),
                "years_in_retirement": max(0, years_in_retirement)
            }
        }
        
    inflated_monthly_expenses = current_monthly_expenses * ((1 + annual_inflation / 100.0) ** years_to_retire)
    inflated_annual_expenses = inflated_monthly_expenses * 12
    
    r_post = post_retirement_return / 100.0
    inf = annual_inflation / 100.0
    real_rate = ((1 + r_post) / (1 + inf)) - 1
    
    if real_rate == 0:
        retirement_corpus = inflated_annual_expenses * years_in_retirement
    else:
        retirement_corpus = inflated_annual_expenses * ((1 - (1 + real_rate) ** (-years_in_retirement)) / real_rate)
        
    return {
        "current_monthly_expenses": round(current_monthly_expenses, 2),
        "inflated_monthly_expenses_at_retirement": round(inflated_monthly_expenses, 2),
        "retirement_corpus": round(retirement_corpus, 2),
        "assumptions": {
            "current_age": current_age,
            "retirement_age": retirement_age,
            "life_expectancy": life_expectancy,
            "annual_inflation": annual_inflation,
            "post_retirement_return": post_retirement_return,
            "years_to_retire": years_to_retire,
            "years_in_retirement": years_in_retirement
        }
    }

def calculate_emergency_fund(
    monthly_expenses: float,
    custom_months: int = 6
) -> dict:
    three_month_target = monthly_expenses * 3
    six_month_target = monthly_expenses * 6
    custom_target = monthly_expenses * custom_months
    
    return {
        "monthly_expenses": round(monthly_expenses, 2),
        "three_month_target": round(three_month_target, 2),
        "six_month_target": round(six_month_target, 2),
        "custom_target": round(custom_target, 2),
        "assumptions": {
            "custom_months": custom_months
        }
    }
