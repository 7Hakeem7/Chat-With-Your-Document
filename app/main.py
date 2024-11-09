# app/main.py
from fastapi import FastAPI
from app.api.endpoints.document import router as document_router
from app.api.endpoints.user import router as user_router  # Import user router
from app.api.endpoints.nlp import router as nlp_router

app = FastAPI()

# Include existing document routes
app.include_router(document_router, prefix="/api/documents")

# Include user-related routes
app.include_router(user_router, prefix="/api/users")

# Include NLP-related routes
app.include_router(nlp_router, prefix="/api/nlp")