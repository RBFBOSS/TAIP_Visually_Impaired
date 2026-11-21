## Endpoint testing using Swagger UI
- În `backend/`: python main.py
- În browser:    http://127.0.0.1:8000/docs

## venv activation on Windows
- cd backend
- .venv\Scripts\Activate.ps1

## Test Driven Development
- `python -m pytest tests/unit/test_flashcard.py -v`

## Local PostgreSQL setup
Generated summaries and flashcards are stored in PostgreSQL.

1. Create a login role and a database (once, as a PostgreSQL superuser):
   ```bash
   psql -d postgres -c "CREATE ROLE taip_flashcards LOGIN PASSWORD 'choose-a-password';"
   createdb -O taip_flashcards taip_flashcards_dev
   ```
2. Create the tables:
   ```bash
   PGPASSWORD='choose-a-password' psql -h 127.0.0.1 -U taip_flashcards \
       -d taip_flashcards_dev -f app/database/create_database.sql
   ```
3. Put the connection settings in `backend/.env` (gitignored):
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=taip_flashcards_dev
   DB_USER=taip_flashcards
   DB_PASSWORD=choose-a-password
   ```
