import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.vocabulary import VocabularyWord
from app.services.vocabulary_service import get_word_difficulty

def main():
    db = SessionLocal()
    try:
        words = db.query(VocabularyWord).all()
        updated_count = 0
        for word_obj in words:
            word = word_obj.word
            difficulty = get_word_difficulty(word)
                
            if word_obj.difficulty != difficulty:
                word_obj.difficulty = difficulty
                updated_count += 1
                
        db.commit()
        print(f"Updated {updated_count} words.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
