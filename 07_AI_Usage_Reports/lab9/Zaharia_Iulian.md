# AI Usage Report

## Citations, Saved Study Material & Interface Display

* **Citations:** Used AI to add citations to the AI-generated study material. The summary and every flashcard now include the page number and an excerpt of the source text, returned by Groq through a strict JSON schema.
* **Persistence:** Saved the summary, flashcards, and citations in PostgreSQL with SQLAlchemy (`StudyMaterialRepository`). Added the `document_processing_summaries` table and linked flashcards to their document in `create_database.sql`. Generating again replaces the saved material, and reprocessing or deleting a document removes it.
* **Interface:** Added a **Study material** section to the Your documents page (`StudyMaterialViewer.tsx`). It loads the saved summary and flashcards for a document ID and shows the source page and excerpt under each one. It follows the lab 7 rules: the result is announced to screen readers, focus moves to the results, each card is labelled "Card 1 of 10", and the summary and the flashcards each get their own error message.
* **Testing:** The service and API tests use an in-memory fake repository instead of PostgreSQL, and fakes instead of Groq.
* **AI tool:** Factory Droid using models: GPT 6.2 Sol and GLM-5.3
