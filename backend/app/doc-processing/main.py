import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

SERVICE_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = SERVICE_DIR.parents[1]

# GROQ_KEY lives in this folder's .env; the database settings live in backend/.env.
load_dotenv(SERVICE_DIR / ".env")
load_dotenv(BACKEND_ROOT / ".env")

# This folder is the import root of the service; the backend root is appended so
# the flashcard repository can import the ORM models (app.models).
sys.path.append(str(BACKEND_ROOT))

from api.routes import router as documents_router

app = FastAPI(title="Document Processing Service")

app.include_router(documents_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
