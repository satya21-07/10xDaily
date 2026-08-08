import os
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

FALLBACK_QUIZ = {
    "questions": [
        {
            "topic": "Vocabulary",
            "question": "What does the word 'Ephemeral' mean?",
            "options": ["Lasting forever", "Short-lived", "Very heavy", "Transparent"],
            "correct_index": 1,
            "explanation": "Ephemeral means lasting for a very short time."
        },
        {
            "topic": "Vocabulary",
            "question": "Choose the synonym for 'Meticulous':",
            "options": ["Careless", "Sloppy", "Careful", "Fast"],
            "correct_index": 2,
            "explanation": "Meticulous means showing great attention to detail; very careful and precise."
        },
        {
            "topic": "Finance",
            "question": "What is compound interest?",
            "options": ["Interest only on principal", "Interest on principal and accumulated interest", "A fixed fee", "A penalty rate"],
            "correct_index": 1,
            "explanation": "Compound interest is calculated on both the initial principal and the accumulated interest from previous periods."
        },
        {
            "topic": "Finance",
            "question": "Which of these is an example of an emergency fund?",
            "options": ["A stock portfolio", "A 401(k) account", "3-6 months of expenses in savings", "A high limit credit card"],
            "correct_index": 2,
            "explanation": "An emergency fund should be highly liquid, typically 3-6 months of living expenses in a savings account."
        },
        {
            "topic": "News",
            "question": "Which organization comprises Brazil, Russia, India, China, and South Africa?",
            "options": ["NATO", "G7", "BRICS", "ASEAN"],
            "correct_index": 2,
            "explanation": "BRICS is an intergovernmental organization comprising Brazil, Russia, India, China, and South Africa."
        },
        {
            "topic": "News",
            "question": "Where is the headquarters of the United Nations located?",
            "options": ["Geneva", "New York City", "Paris", "London"],
            "correct_index": 1,
            "explanation": "The official headquarters of the United Nations is situated in New York City."
        },
        {
            "topic": "Coding",
            "question": "In Python, what is a dictionary?",
            "options": ["A list of words", "A key-value data structure", "A type of loop", "A testing framework"],
            "correct_index": 1,
            "explanation": "A dictionary in Python is a collection of key-value pairs."
        },
        {
            "topic": "Coding",
            "question": "Which of these is a widely used version control system?",
            "options": ["Docker", "Jenkins", "Git", "Kubernetes"],
            "correct_index": 2,
            "explanation": "Git is the most widely used modern version control system."
        },
        {
            "topic": "Spiritual",
            "question": "What is the core practice of mindfulness?",
            "options": ["Sleeping deeply", "Being present in the moment", "Planning for the future", "Ignoring your emotions"],
            "correct_index": 1,
            "explanation": "Mindfulness is the psychological process of purposely bringing one's attention to experiences occurring in the present moment."
        },
        {
            "topic": "Spiritual",
            "question": "In stoicism, what is the 'dichotomy of control'?",
            "options": ["Controlling others", "Understanding what is in our control and what is not", "A meditation technique", "A breathing exercise"],
            "correct_index": 1,
            "explanation": "The dichotomy of control is the Stoic principle of differentiating between what is up to us and what is not."
        }
    ]
}

def generate_daily_quiz() -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        return FALLBACK_QUIZ

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
    except ImportError:
        return FALLBACK_QUIZ
    
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday

    prompt = f"""
    You are an expert quiz master.
    Generate a 10-question mixed quiz for a self-improvement app. 
    The questions should be drawn evenly (2 questions each) from the following 5 topics: 
    Vocabulary, Finance, News (Current World Knowledge), Coding (Computer Science basics), and Spiritual (Mindfulness, Stoicism).
    
    Make the questions engaging, educational, and slightly challenging but accessible.
    
    You MUST respond with ONLY a valid JSON object matching this exact structure:
    {{
      "questions": [
        {{
          "topic": "Topic Name",
          "question": "The question text?",
          "options": ["Option A", "Option B", "Option C", "Option D"],
          "correct_index": 0, // Integer 0-3 representing the index of the correct option
          "explanation": "A brief explanation of why this is the correct answer."
        }}
        // ... 9 more questions
      ]
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
        logger.error(f"Error generating Groq quiz: {e}")
        return FALLBACK_QUIZ
