import os
import json
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

from app.models.lessons import DailyFinanceLesson as DailyFinanceLessonModel
from app.schemas.finance import DailyFinanceLessonContent
from app.services.financial_data_provider import get_financial_data_context, COUNTRY_CONFIGS

logger = logging.getLogger(__name__)

try:
    from groq import Groq
except ImportError:
    Groq = None

PROGRESSIVE_TOPICS = [
    # FINANCIAL BASICS
    "Income & Expenses",
    "Budgeting",
    "Emergency Fund",
    "Debt",
    "Credit Score",
    # INVESTING
    "Compounding",
    "Inflation",
    "Risk & Return",
    "Diversification",
    "Mutual Funds",
    "SIP",
    "Index Funds",
    "Asset Allocation",
    # INDIA-SPECIFIC
    "PPF",
    "EPF",
    "NPS",
    "ELSS",
    "Capital Gains",
    "Tax Planning",
    # ADVANCED
    "Retirement Planning",
    "Insurance",
    "Portfolio Allocation",
    "Long-Term Financial Planning"
]

FALLBACK_DATA = {
    "IN": {
        "topic": "Compounding",
        "why_it_matters": "Compounding is the engine of long-term wealth creation, turning small consistent savings into a substantial corpus over time.",
        "concepts": [
            {
                "title": "What is Compounding?",
                "explanation": "Compounding is earning interest on interest. When your investments generate earnings, those earnings are reinvested and start generating their own earnings."
            },
            {
                "title": "The Power of Time",
                "explanation": "The longer your money stays invested, the faster it grows. Starting early, even with a smaller amount, often outperforms starting later with larger amounts."
            }
        ],
        "example": {
            "title": "The Impact of Starting Early",
            "explanation": "If you invest ₹5,000 monthly at an assumed 12% annual return, after 10 years it grows to approximately ₹11.2 Lakh. However, keeping the same amount invested for 20 years yields approximately ₹49.9 Lakh, demonstrating how compound returns accelerate over time."
        },
        "common_mistake": "Waiting too long to start investing or withdrawing compound returns early to fund discretionary lifestyle expenses.",
        "action_item": {
            "title": "Start an Auto-Invest SIP",
            "description": "Evaluate your monthly budget and set up a small, automated Systematic Investment Plan (SIP) in an index fund matching your risk appetite."
        },
        "reflection": "How would starting your investment journey five years earlier have impacted your financial goals today?",
        "disclaimer": "For educational purposes only. This is not financial advice."
    },
    "US": {
        "topic": "Compounding",
        "why_it_matters": "Compounding is the engine of long-term wealth creation, turning small consistent savings into a substantial corpus over time.",
        "concepts": [
            {
                "title": "What is Compounding?",
                "explanation": "Compounding is earning interest on interest. When your investments generate earnings, those earnings are reinvested and start generating their own earnings."
            },
            {
                "title": "The Power of Time",
                "explanation": "The longer your money stays invested, the faster it grows. Starting early, even with a smaller amount, often outperforms starting later with larger amounts."
            }
        ],
        "example": {
            "title": "The Impact of Starting Early",
            "explanation": "If you invest $100 monthly at an assumed 10% annual return, after 10 years it grows to approximately $20,000. However, keeping the same amount invested for 20 years yields approximately $72,000, demonstrating how compound returns accelerate over time."
        },
        "common_mistake": "Waiting too long to start investing or withdrawing compound returns early to fund discretionary lifestyle expenses.",
        "action_item": {
            "title": "Start an Auto-Invest Plan",
            "description": "Evaluate your monthly budget and set up a small, automated monthly investment in an index fund matching your risk appetite."
        },
        "reflection": "How would starting your investment journey five years earlier have impacted your financial goals today?",
        "disclaimer": "For educational purposes only. This is not financial advice."
    }
}

def get_fallback_lesson(country: str, topic: str) -> dict:
    code = country.upper()
    fallback_group = FALLBACK_DATA.get(code, FALLBACK_DATA["IN"])
    res = dict(fallback_group)
    res["topic"] = topic
    return res

def generate_daily_finance_lesson(topic: str, country: str = "IN") -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        logger.warning("GROQ_API_KEY is not set or placeholder. Using fallback.")
        return get_fallback_lesson(country, topic)

    if Groq is None:
        logger.warning("groq library is not installed. Using fallback.")
        return get_fallback_lesson(country, topic)

    client = Groq(api_key=api_key)

    config = COUNTRY_CONFIGS.get(country.upper(), COUNTRY_CONFIGS["IN"])
    financial_data_ctx = get_financial_data_context(country)

    system_prompt = """You are a financial education content writer.

Your role is to explain financial concepts clearly, accurately and responsibly.
You are not a licensed financial advisor.
Do not provide personalized financial advice.
Do not guarantee returns.
Do not invent current financial data.
Do not invent tax rules, interest rates, market prices, or regulations.
Use only the supplied financial data when discussing current values.
Clearly identify assumptions in calculations.
Prefer educational explanations over specific investment recommendations.
Do not tell the user to buy or sell a particular stock, mutual fund, cryptocurrency or other financial product unless the application explicitly supplies the relevant verified information for an educational comparison.

Return ONLY valid JSON matching the requested structure."""

    user_prompt = f"""Generate a daily finance lesson focused on the topic: "{topic}".
The target audience country is: {config['country']} (Currency: {config['currency']}, Symbol: {config['currency_symbol']}).

{financial_data_ctx}

Instructions for output:
1. All monetary examples must be in {config['currency']} and use the symbol {config['currency_symbol']} (e.g., "{config['currency_symbol']}5,000 per month" or similar).
2. Do NOT tell the user to invest a fixed amount. Explain principles and allow them to determine their own amount.
3. NEVER promise guaranteed returns or profits. Use language like: "Assuming an annual return of X%, the estimated value would be..." and clearly label assumptions.
4. Keep the concepts India-relevant and avoid US-specific terms (like 401k or IRA) unless generating for the US.
5. All calculations and calculations in examples must clearly expose their assumptions.

You MUST respond with a JSON object matching this schema:
{{
  "topic": "{topic}",
  "why_it_matters": "A concise explanation of why this topic is important for daily life.",
  "concepts": [
    {{
      "title": "Concept 1 Title",
      "explanation": "Clear, plain-English educational explanation of the first concept."
    }},
    {{
      "title": "Concept 2 Title",
      "explanation": "Clear, plain-English educational explanation of the second concept."
    }}
  ],
  "example": {{
    "title": "Example Scenario Title",
    "explanation": "A concrete step-by-step example using {config['currency_symbol']} values to illustrate the topic. Clearly state all assumptions."
  }},
  "common_mistake": "A description of a common pitfall or mistake related to this topic.",
  "action_item": {{
    "title": "Action Item Title",
    "description": "One specific, non-advisory task the user can do today (e.g. calculation, review, tracking) to improve their financial understanding."
  }},
  "reflection": "A thoughtful self-reflection question or prompt to help the user relate this topic to their own situation.",
  "disclaimer": "For educational purposes only. This is not financial advice."
}}

Do NOT include any explanation or markdown formatting (e.g. ```json) outside the JSON. Return only raw JSON."""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        text_response = response.choices[0].message.content
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json", "", 1)
        if text_response.endswith("```"):
            text_response = text_response.rsplit("```", 1)[0]
        return json.loads(text_response.strip())
    except Exception as e:
        logger.error(f"Error generating Groq finance lesson: {e}")
        return get_fallback_lesson(country, topic)

def get_or_generate_daily_finance_lesson(db: Session, country: str = "IN") -> DailyFinanceLessonModel:
    today = datetime.now(timezone.utc).date()
    code = country.upper()
    config = COUNTRY_CONFIGS.get(code, COUNTRY_CONFIGS["IN"])
    country_code = config["country"]
    currency = config["currency"]
    
    # Check existing
    existing = db.query(DailyFinanceLessonModel).filter(
        DailyFinanceLessonModel.lesson_date == today,
        DailyFinanceLessonModel.country == country_code
    ).first()
    
    if existing:
        return existing

    # Topic selection
    topic_index = today.toordinal() % len(PROGRESSIVE_TOPICS)
    topic = PROGRESSIVE_TOPICS[topic_index]
    
    lesson_data = generate_daily_finance_lesson(topic, country_code)
    
    # Validate with Pydantic
    try:
        validated_content = DailyFinanceLessonContent.model_validate(lesson_data)
        content_dict = validated_content.model_dump()
    except ValidationError as e:
        logger.error(f"Pydantic validation error for daily finance lesson (topic: {topic}, country: {country_code}): {e}")
        fallback_lesson = get_fallback_lesson(country_code, topic)
        content_dict = DailyFinanceLessonContent.model_validate(fallback_lesson).model_dump()
        
    db_lesson = DailyFinanceLessonModel(
        lesson_date=today,
        country=country_code,
        currency=currency,
        topic=topic,
        content=content_dict
    )
    
    try:
        db.add(db_lesson)
        db.commit()
        db.refresh(db_lesson)
        return db_lesson
    except IntegrityError:
        db.rollback()
        # If another request/thread already inserted it
        existing = db.query(DailyFinanceLessonModel).filter(
            DailyFinanceLessonModel.lesson_date == today,
            DailyFinanceLessonModel.country == country_code
        ).first()
        if existing:
            return existing
        raise

