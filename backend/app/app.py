from fastapi import FastAPI
from app.flashcards.api.routes import router as flashcards_router

app = FastAPI()

app.include_router(flashcards_router)