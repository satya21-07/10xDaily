import logging
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.core_models import Topic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_TOPICS = [
    "Vocabulary", "India News", "World News", "Technology", "Artificial Intelligence",
    "Coding Concepts", "Coding Problems", "Finance", "Health", "Bhagavad Gita",
    "Ramayana", "Mahabharata", "Today's History", "Science Facts", "Space Facts",
    "Constitution", "Book Recommendation", "Movie Recommendation", "Language Learning",
    "Brain Teasers", "Mental Math", "Quotes", "Career Tips", "Leadership",
    "Psychology", "Communication", "Environment", "Cyber Security", "Innovation",
    "Startup Stories", "Business", "Economics", "Stock Market", "Indian Culture",
    "Astronomy", "Photography", "Music", "Cooking", "Fitness", "Meditation",
    "Life Skills", "Productivity"
]

def seed_topics(db: Session):
    for topic_name in DEFAULT_TOPICS:
        topic = db.query(Topic).filter(Topic.name == topic_name).first()
        if not topic:
            logger.info(f"Adding topic: {topic_name}")
            new_topic = Topic(name=topic_name, description=f"Daily content for {topic_name}", is_default=True)
            db.add(new_topic)
    db.commit()

def main():
    logger.info("Starting data seed...")
    db = SessionLocal()
    try:
        seed_topics(db)
        logger.info("Data seeding completed successfully.")
    except Exception as e:
        logger.error(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
