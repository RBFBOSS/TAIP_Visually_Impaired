# Document Processing Service

A FastAPI service that turns PDF lessons into study material for visually impaired students. It extracts the text of a PDF and uses AI (Groq) to write an easy-to-listen-to summary and flashcards that cite their source page.

## What it does

1. **Upload:** accepts one or more PDFs. Each file must have a `.pdf` name and a PDF header; one invalid file rejects the whole upload.
2. **Process:** Docling reads the text already embedded in the PDF and stores it page by page. No OCR and no local AI models are used.
3. **Generate:** sends the text of a page range to Groq (`openai/gpt-oss-120b`) and gets back strict JSON: a summary in short, spoken-style sentences and up to 10 flashcards, each with a question, an answer, and a source page.
4. **Read:** returns the saved summary, all flashcards of a document, or one flashcard by id.

Document status: `UPLOADED` → `PROCESSING` → `COMPLETED` or `FAILED`.

## Setup and run

1. Install the dependencies from `backend/`:
   ```bash
   uv sync
   ```
2. Create `backend/app/doc-processing/.env` (it is gitignored):
   ```
   GROQ_KEY=your-groq-api-key
   ```
3. Start the service from this folder. It is the import root, because `doc-processing` is not a valid Python package name.
   ```bash
   cd backend/app/doc-processing
   uv run python main.py
   ```
   The service runs on http://127.0.0.1:8001, with Swagger UI at http://127.0.0.1:8001/docs.

## Endpoints

| Method | Path | Result |
|---|---|---|
| POST | `/documents` | Upload PDFs (multipart field `files`, repeatable). |
| GET | `/documents?status=UPLOADED` | List documents; `status` is optional (`UPLOADED`, `PROCESSING`, `COMPLETED`, or `FAILED`). |
| DELETE | `/documents/{id}` | Delete a document and its generated study material. |
| GET | `/documents/{id}` | Status, page count, and the first 30 characters of text. |
| POST | `/documents/{id}/process` | Extract the text, page by page. |
| POST | `/documents/{id}/generate?fromPage=1&toPage=10` | Generate and save the summary and flashcards. |
| GET | `/documents/summary/{id}` | The saved summary. |
| GET | `/documents/flashcards/{id}` | All flashcards of the document (`[]` if none). |
| GET | `/documents/flashcard/{flashcardId}` | One flashcard. |

Errors: `400` not a PDF, `404` unknown id or nothing generated yet, `422` no readable text or too much text selected, `502` the Groq call failed.

## Example

```bash
curl -F "files=@lesson1.pdf" http://127.0.0.1:8001/documents
curl "http://127.0.0.1:8001/documents?status=COMPLETED"
curl -X POST http://127.0.0.1:8001/documents/<id>/process
curl -X POST "http://127.0.0.1:8001/documents/<id>/generate?fromPage=20&toPage=29"
curl http://127.0.0.1:8001/documents/summary/<id>
curl http://127.0.0.1:8001/documents/flashcards/<id>
curl http://127.0.0.1:8001/documents/flashcard/<flashcardId>
curl -X DELETE http://127.0.0.1:8001/documents/<id>
```

## Limitations

- **In-memory storage:** documents, summaries, and flashcards are lost when the service restarts.
- **Text-based PDFs only:** there is no OCR, so a scanned PDF without a text layer fails with "No readable text".
- **Slow, blocking processing:** the request waits until the PDF is read. A 495-page book takes about 50–60 seconds and up to about 2 GB of RAM. Only one PDF is processed at a time.
- **At most 15,000 characters per generate call** (about 10–13 pages). Groq's free tier allows 8,000 tokens per minute and 200,000 per day for this model, and one call must fit both the text and the reply. A larger range returns `422`. If `toPage` is missing, 10 pages are used.
- **Calls close together may be slow:** two generate calls in the same minute can hit the per-minute limit. The Groq SDK retries, so the second call may be slow or return `502`.
- **Results are replaced:** each generate call replaces the previous summary and flashcards (with new ids), and processing a document again clears them.
- **No review step yet:** no person checks the AI output, and flashcards are not sent to the flashcards module as drafts.

## Tests

```bash
cd backend
uv run pytest app/doc-processing/tests
```

The tests never call Groq; they use fakes. `tests/test_pdf_reader.py` runs real Docling on `tests/fixtures/sample.pdf`.
