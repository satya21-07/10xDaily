import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.db.session import SessionLocal
from app.services.vocabulary_service import get_or_generate_daily_words
from app.services.cleanup_service import cleanup_old_daily_content

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def fetch_daily_vocabulary_job():
    """Background job to fetch the daily vocabulary."""
    logger.info("Running daily vocabulary fetch job...")
    db = SessionLocal()
    try:
        # Generate 10 words for today
        get_or_generate_daily_words(db, limit=10)
        logger.info("Successfully completed daily vocabulary fetch job.")
    except Exception as e:
        logger.error(f"Error in daily vocabulary job: {e}")
    finally:
        db.close()

def cleanup_old_daily_content_job():
    """Background job to purge daily topic/lesson content older than 7 days."""
    logger.info("Running automated 7-day database cleanup job...")
    db = SessionLocal()
    try:
        cleanup_old_daily_content(db, days_to_keep=7)
    except Exception as e:
        logger.error(f"Error in database cleanup job: {e}")
    finally:
        db.close()

def start_scheduler():
    """Start the background scheduler."""
    # Perform startup cleanup
    cleanup_old_daily_content_job()

    if not scheduler.running:
        # Run daily vocabulary fetch every day at midnight
        scheduler.add_job(
            fetch_daily_vocabulary_job,
            trigger=CronTrigger(hour=0, minute=0),
            id='daily_vocabulary_fetch',
            name='Fetch 10 Daily Vocabulary Words',
            replace_existing=True
        )
        # Run daily 7-day cleanup job every day at 00:05 UTC
        scheduler.add_job(
            cleanup_old_daily_content_job,
            trigger=CronTrigger(hour=0, minute=5),
            id='daily_database_cleanup',
            name='Purge Daily Content Older Than 7 Days',
            replace_existing=True
        )
        scheduler.start()
        logger.info("Scheduler started with daily vocabulary fetch and 7-day DB cleanup.")

def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped.")
