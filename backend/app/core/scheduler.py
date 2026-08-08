import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.db.session import SessionLocal
from app.services.vocabulary_service import get_or_generate_daily_words

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

def start_scheduler():
    """Start the background scheduler."""
    if not scheduler.running:
        # Run every day at midnight
        scheduler.add_job(
            fetch_daily_vocabulary_job,
            trigger=CronTrigger(hour=0, minute=0),
            id='daily_vocabulary_fetch',
            name='Fetch 10 Daily Vocabulary Words',
            replace_existing=True
        )
        scheduler.start()
        logger.info("Scheduler started.")

def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped.")
