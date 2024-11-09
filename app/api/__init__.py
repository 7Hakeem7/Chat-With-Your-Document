
from fastapi import APIRouter
from app.api.endpoints import document, user , nlp

api_router = APIRouter()
api_router.include_router(document.router, prefix="/documents", tags=["documents"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(nlp.router, prefix="/nlp", tags=["nlp"])