import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.lessons import (
    DailyHealthLesson,
    DailyFinanceLesson,
    DailyCodingLesson,
    DailyQuiz,
)
from app.models.core_models import (
    DailySpiritualLesson,
    DailyOnThisDayEvent,
    Bookmark,
    Note,
)
from app.models.vocabulary import DailyVocabulary, VocabularyWord
from app.models.games import DailyKenKenPuzzle

logger = logging.getLogger(__name__)


def cleanup_old_daily_content(db: Session, days_to_keep: int = 7) -> dict:
    """
    Deletes daily topic/lesson records older than `days_to_keep` (default 7 days).
    All user-saved content (bookmarks, personal notes, progress) is preserved.
    """
    now_utc = datetime.now(timezone.utc)
    cutoff_date = (now_utc - timedelta(days=days_to_keep)).date()
    cutoff_str = cutoff_date.strftime("%Y-%m-%d")

    logger.info(f"Starting database cleanup for daily content older than {days_to_keep} days (Cutoff: {cutoff_str})...")

    deleted_counts = {}

    try:
        # 1. Daily Health Lessons (Date column)
        health_deleted = db.query(DailyHealthLesson).filter(
            DailyHealthLesson.lesson_date < cutoff_date
        ).delete(synchronize_session=False)
        deleted_counts["daily_health_lesson"] = health_deleted

        # 2. Daily Finance Lessons (Date column)
        finance_deleted = db.query(DailyFinanceLesson).filter(
            DailyFinanceLesson.lesson_date < cutoff_date
        ).delete(synchronize_session=False)
        deleted_counts["daily_finance_lesson"] = finance_deleted

        # 3. Daily Coding Lessons (Date column)
        coding_deleted = db.query(DailyCodingLesson).filter(
            DailyCodingLesson.lesson_date < cutoff_date
        ).delete(synchronize_session=False)
        deleted_counts["daily_coding_lesson"] = coding_deleted

        # 4. Daily Spiritual Lessons (String/Date YYYY-MM-DD column)
        spiritual_deleted = db.query(DailySpiritualLesson).filter(
            DailySpiritualLesson.lesson_date < cutoff_str
        ).delete(synchronize_session=False)
        deleted_counts["daily_spiritual_lesson"] = spiritual_deleted

        # 5. Daily Quizzes (Date column)
        quiz_deleted = db.query(DailyQuiz).filter(
            DailyQuiz.lesson_date < cutoff_date
        ).delete(synchronize_session=False)
        deleted_counts["daily_quiz"] = quiz_deleted

        # 6. Daily On This Day Events (String YYYY-MM-DD column)
        on_this_day_deleted = db.query(DailyOnThisDayEvent).filter(
            DailyOnThisDayEvent.date < cutoff_str
        ).delete(synchronize_session=False)
        deleted_counts["daily_on_this_day_event"] = on_this_day_deleted

        # 7. Daily KenKen Puzzles (String YYYY-MM-DD column)
        kenken_deleted = db.query(DailyKenKenPuzzle).filter(
            DailyKenKenPuzzle.puzzle_date < cutoff_str
        ).delete(synchronize_session=False)
        deleted_counts["daily_kenken_puzzle"] = kenken_deleted

        # 8. Daily Vocabulary Mappings (Date column)
        vocab_deleted = db.query(DailyVocabulary).filter(
            DailyVocabulary.date < cutoff_date
        ).delete(synchronize_session=False)
        deleted_counts["daily_vocabulary"] = vocab_deleted

        # 9. Clean up unreferenced VocabularyWord entries that are not bookmarked/noted
        # Find all word IDs currently in daily_vocabulary
        active_vocab_word_ids = {
            r[0] for r in db.query(DailyVocabulary.word_id).all()
        }
        # Find all bookmarked/noted reference IDs or words to protect
        bookmarked_titles = {
            r[0].lower() for r in db.query(Bookmark.title).filter(Bookmark.content_type == "vocabulary").all()
        }

        orphan_words = db.query(VocabularyWord).filter(
            ~VocabularyWord.id.in_(active_vocab_word_ids) if active_vocab_word_ids else True,
            VocabularyWord.created_at < (now_utc - timedelta(days=days_to_keep))
        ).all()

        orphan_deleted_count = 0
        for w in orphan_words:
            if w.word.lower() not in bookmarked_titles:
                db.delete(w)
                orphan_deleted_count += 1

        deleted_counts["orphan_vocabulary_words"] = orphan_deleted_count

        db.commit()

        total_cleaned = sum(deleted_counts.values())
        logger.info(f"Database cleanup complete. Cleaned {total_cleaned} old daily records: {deleted_counts}")
        return deleted_counts

    except Exception as e:
        db.rollback()
        logger.error(f"Error during database cleanup: {e}")
        return {"error": str(e)}
