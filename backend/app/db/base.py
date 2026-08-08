# Import all the models, so that Base has them before being imported by Alembic
from app.db.base_class import Base
from app.models.core_models import User, Topic, UserTopic, Bookmark, Note, UserProgress
from app.models.vocabulary import VocabularyWord
from app.models.news import NewsArticle
from app.models.coding import CodingProblem
from app.models.lessons import FinanceLesson, HealthLesson, SpiritualLesson

# This ensures all models are registered with Base.metadata
