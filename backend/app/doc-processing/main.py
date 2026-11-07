import uvicorn
from fastapi import FastAPI

from api.routes import router as documents_router

app = FastAPI(title="Document Processing Service")

app.include_router(documents_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
