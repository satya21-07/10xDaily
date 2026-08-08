import os
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

FALLBACK_DATA = {
    "topic": "The Power of Compound Interest",
    "daily_tip": "Automate your investments. Set up a direct deposit into your brokerage account so you invest before you have the chance to spend.",
    "concepts": [
        {
            "title": "What is Compound Interest?",
            "explanation": "Compound interest is the interest on savings calculated on both the initial principal and the accumulated interest from previous periods. It's 'interest on interest'."
        },
        {
            "title": "The Rule of 72",
            "explanation": "A quick formula to estimate the number of years required to double your investment at a given annual rate of return. Just divide 72 by the annual interest rate."
        }
    ],
    "action_item": "Log into your bank or brokerage today and set up an automatic weekly or monthly transfer of at least $50 into an index fund."
}

def generate_daily_finance_lesson() -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        return FALLBACK_DATA

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
    except ImportError:
        return FALLBACK_DATA
    
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    topics = [
        "Index Funds vs Individual Stocks", "Emergency Funds", 
        "Tax Advantaged Accounts (401k/IRA)", "Understanding Credit Scores", 
        "Budgeting Rules (50/30/20)", "Dollar Cost Averaging", "Inflation and Purchasing Power"
    ]
    topic_seed = topics[day_of_year % len(topics)]

    prompt = f"""
    You are an expert financial advisor and wealth coach.
    Generate a daily finance lesson focused on the topic: {topic_seed}.
    
    You MUST respond with ONLY a valid JSON object matching this exact structure:
    {{
      "topic": "{topic_seed}",
      "daily_tip": "A quick, highly actionable financial tip.",
      "concepts": [
        {{ "title": "Concept 1", "explanation": "Clear explanation..." }},
        {{ "title": "Concept 2", "explanation": "Clear explanation..." }}
      ],
      "action_item": "One specific task the user should do today to improve their finances."
    }}
    
    Ensure the JSON is perfectly formatted and contains no markdown code blocks outside of the raw JSON itself.
    """

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that strictly outputs JSON."},
                {"role": "user", "content": prompt}
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
        return FALLBACK_DATA
