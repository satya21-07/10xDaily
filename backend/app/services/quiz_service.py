import os
import json
import logging
import asyncio
import httpx
import random
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

FALLBACK_QUIZ = {
    "questions": [
        {
            "id": "fallback-1",
            "topic": "Vocabulary",
            "difficulty": "Easy",
            "question": "What does the word 'Ephemeral' mean?",
            "options": ["Lasting forever", "Short-lived", "Very heavy", "Transparent"],
            "correct_index": 1,
            "explanation": "Ephemeral means lasting for a very short time."
        },
        {
            "id": "fallback-2",
            "topic": "Vocabulary",
            "difficulty": "Medium",
            "question": "Choose the synonym for 'Meticulous':",
            "options": ["Careless", "Sloppy", "Careful", "Fast"],
            "correct_index": 2,
            "explanation": "Meticulous means showing great attention to detail; very careful and precise."
        },
        {
            "id": "fallback-3",
            "topic": "Finance",
            "difficulty": "Easy",
            "question": "What is compound interest?",
            "options": ["Interest only on principal", "Interest on principal and accumulated interest", "A fixed fee", "A penalty rate"],
            "correct_index": 1,
            "explanation": "Compound interest is calculated on both the initial principal and the accumulated interest from previous periods."
        },
        {
            "id": "fallback-4",
            "topic": "Finance",
            "difficulty": "Medium",
            "question": "Which of these is an example of an emergency fund?",
            "options": ["A stock portfolio", "A 401(k) account", "3-6 months of expenses in savings", "A high limit credit card"],
            "correct_index": 2,
            "explanation": "An emergency fund should be highly liquid, typically 3-6 months of living expenses in a savings account."
        },
        {
            "id": "fallback-5",
            "topic": "News",
            "difficulty": "Medium",
            "question": "Which organization comprises Brazil, Russia, India, China, and South Africa?",
            "options": ["NATO", "G7", "BRICS", "ASEAN"],
            "correct_index": 2,
            "explanation": "BRICS is an intergovernmental organization comprising Brazil, Russia, India, China, and South Africa."
        },
        {
            "id": "fallback-6",
            "topic": "News",
            "difficulty": "Easy",
            "question": "Where is the headquarters of the United Nations located?",
            "options": ["Geneva", "New York City", "Paris", "London"],
            "correct_index": 1,
            "explanation": "The official headquarters of the United Nations is situated in New York City."
        },
        {
            "id": "fallback-7",
            "topic": "Coding",
            "difficulty": "Easy",
            "question": "In Python, what is a dictionary?",
            "options": ["A list of words", "A key-value data structure", "A type of loop", "A testing framework"],
            "correct_index": 1,
            "explanation": "A dictionary in Python is a collection of key-value pairs."
        },
        {
            "id": "fallback-8",
            "topic": "Coding",
            "difficulty": "Medium",
            "question": "Which of these is a widely used version control system?",
            "options": ["Docker", "Jenkins", "Git", "Kubernetes"],
            "correct_index": 2,
            "explanation": "Git is the most widely used modern version control system."
        },
        {
            "id": "fallback-9",
            "topic": "Spiritual",
            "difficulty": "Medium",
            "question": "What is the core practice of mindfulness?",
            "options": ["Sleeping deeply", "Being present in the moment", "Planning for the future", "Ignoring your emotions"],
            "correct_index": 1,
            "explanation": "Mindfulness is the psychological process of purposely bringing one's attention to experiences occurring in the present moment."
        },
        {
            "id": "fallback-10",
            "topic": "Spiritual",
            "difficulty": "Hard",
            "question": "In stoicism, what is the 'dichotomy of control'?",
            "options": ["Controlling others", "Understanding what is in our control and what is not", "A meditation technique", "A breathing exercise"],
            "correct_index": 1,
            "explanation": "The dichotomy of control is the Stoic principle of differentiating between what is up to us and what is not."
        }
    ]
}

# --- Pydantic Validation Models ---
class QuizQuestion(BaseModel):
    id: str = Field(..., min_length=1)
    topic: str
    difficulty: str
    question: str = Field(..., min_length=1)
    options: list[str] = Field(..., min_length=4, max_length=4)
    correct_index: int = Field(..., ge=0, le=3)
    explanation: str = Field(..., min_length=1)

class QuizResponse(BaseModel):
    questions: list[QuizQuestion] = Field(..., min_length=10, max_length=10)

# --- Memory Cache ---
_daily_quiz_cache = {
    "date": None,
    "quiz_data": None
}

# --- Context Fetchers ---
async def _fetch_single_word(client: httpx.AsyncClient, word: str) -> str:
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        resp = await client.get(url)
        if resp.status_code == 200:
            data = resp.json()[0]
            meanings = data.get("meanings", [])
            if meanings:
                first_meaning = meanings[0].get("definitions", [{}])[0].get("definition", "")
                return f"Word: {word} - Meaning: {first_meaning}"
    except Exception:
        pass
    return f"Word: {word}"

async def fetch_vocabulary_context(client: httpx.AsyncClient) -> str:
    try:
        from app.utils.curated_words import CURATED_WORDS
        words = random.sample(CURATED_WORDS, min(5, len(CURATED_WORDS)))
    except ImportError:
        words = ["ephemeral", "meticulous", "ubiquitous", "pragmatic", "esoteric"]
        
    tasks = [_fetch_single_word(client, w) for w in words]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    valid_results = [res for res in results if isinstance(res, str)]
    return "Vocabulary Context:\n" + "\n".join(valid_results)

async def fetch_news_context(client: httpx.AsyncClient) -> str:
    url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
    try:
        resp = await client.get(url, follow_redirects=True)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        items = root.findall(".//item")[:10]
        context = []
        for item in items:
            title = item.findtext("title", "")
            if title:
                context.append(f"- {title}")
        if context:
            return "Current News Headlines:\n" + "\n".join(context)
    except Exception as e:
        logger.error(f"Failed to fetch news context: {e}")
    return "No recent news available. Fall back to major universally known recent events safely, but do not invent fake news."

async def fetch_finance_context() -> str:
    try:
        from app.services.financial_data_provider import get_financial_data_context
        return get_financial_data_context("IN")
    except Exception as e:
        logger.error(f"Failed to fetch finance context: {e}")
        return "Basic Finance principles: Compounding, Emergency Funds, Asset Allocation."

async def fetch_coding_context() -> str:
    return "Coding topics to cover: Python syntax, Data Structures (Dictionaries, Lists), Version Control (Git), Algorithms."

async def fetch_spiritual_context() -> str:
    return "Spiritual topics: Mindfulness, Stoicism, emotional regulation, being present, dichotomy of control."

async def _gather_all_contexts() -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        results = await asyncio.gather(
            fetch_vocabulary_context(client),
            fetch_news_context(client),
            fetch_finance_context(),
            fetch_coding_context(),
            fetch_spiritual_context(),
            return_exceptions=True
        )
        
    # Handle possible exceptions in gather
    contexts = []
    for r in results:
        if isinstance(r, Exception):
            contexts.append(f"Context unavailable due to error: {r}")
        else:
            contexts.append(r)
            
    return {
        "vocabulary": contexts[0],
        "news": contexts[1],
        "finance": contexts[2],
        "coding": contexts[3],
        "spiritual": contexts[4]
    }

# --- Generation and Validation ---
def validate_quiz_data(data: dict) -> bool:
    try:
        validated = QuizResponse.model_validate(data)
        
        # Validate topic distribution (exactly 2 of each)
        topic_counts = {"Vocabulary": 0, "Finance": 0, "News": 0, "Coding": 0, "Spiritual": 0}
        difficulty_counts = {"Easy": 0, "Medium": 0, "Hard": 0}
        
        unique_questions = set()
        
        for q in validated.questions:
            if q.topic in topic_counts:
                topic_counts[q.topic] += 1
            if q.difficulty in difficulty_counts:
                difficulty_counts[q.difficulty] += 1
                
            # Duplicate check
            if q.question in unique_questions:
                return False
            unique_questions.add(q.question)
            
            # Simple check for forbidden words in options
            for opt in q.options:
                opt_lower = opt.lower()
                if "all of the above" in opt_lower or "none of the above" in opt_lower:
                    return False
                    
        # Check distribution rules
        if any(count != 2 for count in topic_counts.values()):
            return False
            
        return True
    except ValidationError as e:
        logger.warning(f"Quiz validation failed: {e}")
        return False
    except Exception as e:
        logger.warning(f"Unexpected validation error: {e}")
        return False

async def generate_daily_quiz(force_refresh: bool = False) -> dict:
    """
    Main function to get or generate the daily quiz.
    Uses an in-memory cache that resets daily.
    """
    global _daily_quiz_cache
    
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    if not force_refresh and _daily_quiz_cache["date"] == today_str and _daily_quiz_cache["quiz_data"]:
        return _daily_quiz_cache["quiz_data"]
        
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        return FALLBACK_QUIZ

    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=api_key)
    except ImportError:
        logger.error("Failed to import AsyncGroq")
        return FALLBACK_QUIZ
        
    contexts = await _gather_all_contexts()

    prompt = f"""You are an expert quiz master.
Generate a 10-question mixed quiz for a self-improvement app.

Topics exactly 2 questions each (TOTAL EXACTLY 10 QUESTIONS):
1. Vocabulary
2. Finance
3. News (Current World Knowledge)
4. Coding (Computer Science basics)
5. Spiritual (Mindfulness, Stoicism)

Difficulty Distribution: Exactly 3 Easy, 5 Medium, and 2 Hard questions.

---
CONTEXT TO USE FOR QUESTIONS:

{contexts['news']}
(CRITICAL: For News questions, use ONLY the supplied news context. Do not invent current events, dates, statistics, people, or claims. If the context is empty or insufficient, fallback to universally true historical facts without hallucinating recent news.)

{contexts['vocabulary']}
{contexts['finance']}
{contexts['coding']}
{contexts['spiritual']}
---

RULES:
1. Every question must contain: id (a unique string), topic (one of the 5 exact topic names), difficulty (Easy, Medium, or Hard), question, options (exactly 4), correct_index (0 to 3), and explanation.
2. EXACTLY 10 QUESTIONS TOTAL. DO NOT GENERATE 15. DO NOT GENERATE 5. EXACTLY 10.
2. Exactly one correct answer.
3. Do not use "All of the above" or "None of the above".
4. Avoid ambiguous or duplicate questions.
5. Avoid questions where the correct answer is obvious because it is significantly longer.
6. Explanations should be concise but educational.
7. Finance questions must not be personalized financial advice.
8. Spiritual questions must not fabricate quotations or scripture references.
9. Return ONLY valid JSON matching this exact structure, with no markdown formatting outside it:
{{
  "questions": [
    {{
      "id": "q1",
      "topic": "Vocabulary",
      "difficulty": "Easy",
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "correct_index": 0,
      "explanation": "..."
    }}
  ]
}}
"""

    for attempt in range(2):
        try:
            response = await client.chat.completions.create(
                model="openai/gpt-oss-120b",  # Using 70b model for strict instruction following
                messages=[
                    {"role": "system", "content": "You strictly output valid JSON. You must generate exactly 10 questions, not 15 or 5. Do not generate Markdown blocks or comments."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            text_response = response.choices[0].message.content
            if text_response.startswith("```json"):
                text_response = text_response.replace("```json", "", 1)
            if text_response.endswith("```"):
                text_response = text_response.rsplit("```", 1)[0]
                
            quiz_data = json.loads(text_response.strip())
            
            if validate_quiz_data(quiz_data):
                # Save to cache
                _daily_quiz_cache["date"] = today_str
                _daily_quiz_cache["quiz_data"] = quiz_data
                return quiz_data
            else:
                logger.warning(f"Quiz validation failed on attempt {attempt+1}")
        except Exception as e:
            logger.error(f"Error generating Groq quiz on attempt {attempt+1}: {e}")
            
    # If all attempts fail, use fallback
    return FALLBACK_QUIZ
