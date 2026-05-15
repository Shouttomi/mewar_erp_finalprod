from fastapi import APIRouter
from app.routers.chatbot import router as chatbot_router
from app.routers.auth import router as auth_router
from app.routers.chatbot_nl2sql import router as nl2sql_router

router = APIRouter(prefix="/api/mewar")

# include everything here
router.include_router(auth_router)
router.include_router(chatbot_router)
router.include_router(nl2sql_router)
