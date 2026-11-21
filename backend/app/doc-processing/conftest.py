import sys
from pathlib import Path

# "doc-processing" is not a valid Python package name, so this folder is the
# import root of the service and must be on sys.path wherever pytest is run from.
sys.path.insert(0, str(Path(__file__).resolve().parent))

# The flashcard repository uses the backend's ORM models (app.models) and the
# database settings from backend/.env, so the backend root must be importable
# and its environment file loaded wherever pytest is run from.
backend_root = Path(__file__).resolve().parents[2]
sys.path.append(str(backend_root))

from dotenv import load_dotenv

load_dotenv(backend_root / ".env")
