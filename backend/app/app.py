from contextlib import asynccontextmanager
import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client

from app.database.base import check_database_connection
from app.modules.flashcards.api.routes import router as flashcards_router
from app.modules.pdf_upload.api.routes import router as pdf_upload_router
from app.modules.pdf_upload.repositories.supabase_storage import SupabasePdfStorageRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not check_database_connection():
        raise RuntimeError("Database connection check failed on startup.")

    supabase_client = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    app.state.supabase_storage = SupabasePdfStorageRepository(
        client=supabase_client,
        bucket_name=os.environ.get("SUPABASE_PDF_BUCKET", "pdf_files"),
    )
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flashcards_router)
app.include_router(pdf_upload_router)