import os
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.core_models import DailyOnThisDayEvent
from datetime import datetime
from zoneinfo import ZoneInfo

def clear_today_cache():
    INDIA_TZ = ZoneInfo("Asia/Kolkata")
    now = datetime.now(INDIA_TZ)
    current_date_str = now.strftime("%Y-%m-%d")
    
    db = SessionLocal()
    try:
        deleted = db.query(DailyOnThisDayEvent).filter(DailyOnThisDayEvent.date == current_date_str).delete()
        db.commit()
        print(f"Deleted {deleted} cache entries for {current_date_str}")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_today_cache()
