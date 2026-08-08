import logging
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.vocabulary import VocabularyWord
from app.models.news import NewsArticle
from app.models.coding import CodingProblem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_vocabulary(db: Session):
    words = [
        {"word": "Ephemeral", "meaning": "Lasting for a very short time.", "pronunciation": "ih-fem-er-uhl", "example": "Fashions are ephemeral.", "difficulty": "Medium"},
        {"word": "Ubiquitous", "meaning": "Present, appearing, or found everywhere.", "pronunciation": "yoo-bik-wi-tuhs", "example": "His ubiquitous influence was felt by all.", "difficulty": "Hard"},
        {"word": "Pragmatic", "meaning": "Dealing with things sensibly and realistically.", "pronunciation": "prag-mat-ik", "example": "She took a pragmatic approach to the problem.", "difficulty": "Medium"},
        {"word": "Esoteric", "meaning": "Intended for or likely to be understood by only a small number of people with a specialized knowledge or interest.", "pronunciation": "es-uh-ter-ik", "example": "Esoteric philosophical debates.", "difficulty": "Hard"},
        {"word": "Sycophant", "meaning": "A person who acts obsequiously toward someone important in order to gain advantage.", "pronunciation": "sik-uh-fuhnt", "example": "He was surrounded by sycophants.", "difficulty": "Hard"},
    ]
    for w in words:
        if not db.query(VocabularyWord).filter(VocabularyWord.word == w["word"]).first():
            db.add(VocabularyWord(**w))
    db.commit()
    logger.info("Vocabulary seeded.")

def seed_news(db: Session):
    articles = [
        {
            "title": "OpenAI announces GPT-5 release date",
            "summary": "OpenAI has officially announced the launch window for GPT-5, promising significant improvements in reasoning and multimodality.",
            "source": "TechCrunch",
            "url": "https://techcrunch.com",
            "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80&w=800",
            "category": "Artificial Intelligence",
            "ai_summary": "GPT-5 is arriving late this year with enhanced logic capabilities. It will natively support audio and video inputs alongside text."
        },
        {
            "title": "Apple Intelligence rolling out to iOS 18",
            "summary": "Apple is bringing on-device AI models to iPhones, focusing on privacy and deep app integrations.",
            "source": "The Verge",
            "url": "https://theverge.com",
            "image_url": "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?auto=format&fit=crop&q=80&w=800",
            "category": "Technology",
            "ai_summary": "Apple emphasizes privacy with its new on-device AI processing for iOS 18, handling complex requests without cloud computing."
        }
    ]
    for a in articles:
        if not db.query(NewsArticle).filter(NewsArticle.title == a["title"]).first():
            db.add(NewsArticle(**a))
    db.commit()
    logger.info("News seeded.")

def seed_coding(db: Session):
    problems = [
        {
            "title": "Two Sum",
            "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
            "difficulty": "Easy",
            "python_solution": "def twoSum(nums: List[int], target: int) -> List[int]:\n    pass",
            "ai_explanation": "Use a hash map to store the values and their indices. For each element, check if target - element exists in the map.",
            "time_complexity": "O(N)",
            "space_complexity": "O(N)",
            "hint": '["Try using a hash map", "What if you store the numbers you have seen so far?"]'
        },
        {
            "title": "Valid Parentheses",
            "description": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
            "difficulty": "Easy",
            "python_solution": "def isValid(s: str) -> bool:\n    pass",
            "ai_explanation": "Use a stack to keep track of open brackets. When you encounter a close bracket, it must match the top of the stack.",
            "time_complexity": "O(N)",
            "space_complexity": "O(N)",
            "hint": '["Use a stack data structure", "Map closing brackets to opening brackets"]'
        }
    ]
    for p in problems:
        if not db.query(CodingProblem).filter(CodingProblem.title == p["title"]).first():
            db.add(CodingProblem(**p))
    db.commit()
    logger.info("Coding problems seeded.")

def main():
    logger.info("Starting content seed...")
    db = SessionLocal()
    try:
        seed_vocabulary(db)
        seed_news(db)
        seed_coding(db)
        logger.info("Content seeding completed successfully.")
    except Exception as e:
        logger.error(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
