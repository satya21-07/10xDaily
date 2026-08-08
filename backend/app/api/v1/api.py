from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, vocabulary, news, coding, lessons, quote, finance, health, spiritual, bookmarks, quiz

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(vocabulary.router, prefix="/vocabulary", tags=["vocabulary"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(coding.router, prefix="/coding", tags=["coding"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
api_router.include_router(quote.router, prefix="/quote", tags=["quote"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
api_router.include_router(finance.router, prefix="/finance", tags=["finance"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(spiritual.router, prefix="/spiritual", tags=["spiritual"])
api_router.include_router(bookmarks.router, prefix="/bookmarks", tags=["bookmarks"])
