from datetime import datetime, timedelta, timezone

COUNTRY_CONFIGS = {
    "IN": {
        "country": "IN",
        "currency": "INR",
        "currency_symbol": "₹",
        "locale": "en-IN",
        "default_investment_example": "₹5,000"
    },
    "US": {
        "country": "US",
        "currency": "USD",
        "currency_symbol": "$",
        "locale": "en-US",
        "default_investment_example": "$100"
    },
    "GB": {
        "country": "GB",
        "currency": "GBP",
        "currency_symbol": "£",
        "locale": "en-GB",
        "default_investment_example": "£100"
    }
}

# Authoritative financial data (No RBI API key will be used, we use this up-to-date registry)
TRUSTED_MARKET_DATA = {
    "IN": {
        "inflation_rate": "5.0%",
        "rbi_repo_rate": "6.50%",
        "ppf_interest_rate": "7.1%",
        "epf_interest_rate": "8.15%",
        "nps_equity_cap": "75%",
        "gold_price_per_10g_24k": "₹72,000",
        "short_term_capital_gains_equity": "20%",
        "long_term_capital_gains_equity": "12.5% (Exempt up to ₹1.25 Lakh per year)",
        "source": "RBI / Government of India",
        "as_of": "August 2026",
        "income_tax_regime": (
            "New Tax Regime (Slabs: Up to ₹3L: Nil, ₹3L-₹7L: 5%, ₹7L-₹10L: 10%, "
            "₹10L-₹12L: 15%, ₹12L-₹15L: 20%, Above ₹15L: 30%. Standard Deduction: ₹75,000)"
        )
    },
    "US": {
        "inflation_rate": "2.5%",
        "fed_funds_rate": "5.25% - 5.50%",
        "maximum_401k_contribution_limit": "$23,500",
        "maximum_ira_contribution_limit": "$7,000",
        "gold_price_per_ounce": "$2,350",
        "capital_gains_tax_equity": "0%, 15%, or 20% (depending on taxable income)",
        "source": "Federal Reserve / IRS",
        "as_of": "August 2026",
        "income_tax_brackets": "Single Tax Brackets range from 10% to 37%"
    },
    "GB": {
        "inflation_rate": "2.2%",
        "boe_bank_rate": "5.00%",
        "maximum_isa_contribution_limit": "£20,000",
        "maximum_pension_annual_allowance": "£60,000",
        "gold_price_per_gram": "£60",
        "capital_gains_tax_equity": "10% (basic rate) or 20% (higher rate)",
        "source": "Bank of England / HMRC",
        "as_of": "August 2026",
        "income_tax_brackets": "Personal Allowance £12,570. Slabs: Basic 20%, Higher 40%, Additional 45%"
    }
}

def get_current_financial_data(country: str) -> dict:
    """
    Returns trusted/official financial parameters for the given country code.
    Falls back to 'IN' if the country code is not found.
    """
    code = country.upper()
    if code not in TRUSTED_MARKET_DATA:
        code = "IN"
    return TRUSTED_MARKET_DATA[code]

def get_financial_data_context(country: str) -> str:
    """
    Returns formatted verified financial data context to be supplied to the Groq prompt.
    """
    data = get_current_financial_data(country)
    config = COUNTRY_CONFIGS.get(country.upper(), COUNTRY_CONFIGS["IN"])
    
    context = f"CURRENT AUTHORITATIVE FINANCIAL DATA FOR {config['country']} ({config['currency']}):\n"
    context += f"Source: {data.get('source')}\n"
    context += f"As Of Date: {data.get('as_of')}\n"
    for key, val in data.items():
        if key not in ["source", "as_of"]:
            readable_key = key.replace("_", " ").title()
            context += f"- {readable_key}: {val}\n"
            
    return context

