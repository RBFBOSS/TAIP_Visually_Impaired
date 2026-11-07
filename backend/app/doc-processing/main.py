from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv(Path(__file__).resolve().parent / ".env")

from api.routes import router as documents_router

app = FastAPI(title="Document Processing Service")

app.include_router(documents_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
