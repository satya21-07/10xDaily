from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, vocabulary, news, coding, quote, finance, health, spiritual, bookmarks, quiz, on_this_day, admin, games

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(vocabulary.router, prefix="/vocabulary", tags=["vocabulary"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(coding.router, prefix="/coding", tags=["coding"])
api_router.include_router(quote.router, prefix="/quote", tags=["quote"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
api_router.include_router(finance.router, prefix="/finance", tags=["finance"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(spiritual.router, prefix="/spiritual", tags=["spiritual"])
api_router.include_router(bookmarks.router, prefix="/bookmarks", tags=["bookmarks"])
api_router.include_router(on_this_day.router, prefix="/on-this-day", tags=["on-this-day"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
