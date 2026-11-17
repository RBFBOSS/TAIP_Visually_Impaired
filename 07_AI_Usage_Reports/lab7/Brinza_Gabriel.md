# AI Usage Report

## Flashcard Management & Approval Module

* **Architectural Planning & Task Decomposition:** Analyzed the PlantUML diagram (`flashcard_management_and_approval.txt`) and structured the module into clean-architecture layers: Domain Models, Repositories, Services, Cross-Cutting Aspects, and FastAPI Endpoints.
* **Aspect-Oriented Programming (AOP) Design:** Explored AOP patterns in Python to decouple cross-cutting concerns, specifically role-based security checks and execution audit logging—from core business logic.
* **Incremental Code Generation:**
  * **Domain & DTOs:** Generated Pydantic models (`Flashcard`, `Deck`, `Citation`, `ApprovalStatus`, `GeneratedFlashcard`, `DocumentSection`), along with `User` and `AccessibilityPreferences` entities tailored to visually impaired learners.
  * **Persistence Layer:** Implemented the abstract `FlashcardRepository` interface and an `InMemoryFlashcardRepository` to support development and testing prior to database integration.
  * **Business Logic Services:** Built `FlashcardService`, `CitationValidator`, and `DeckService`, enforcing role-based moderation rules (restricting approval and rejection actions to users with the `TEACHER` role).
  * **API Layer:** Created FastAPI routes, request/response schemas, and dependency injection setups (`app/flashcards/api/`).
* **Testing Guidance:** Outlined strategies for manual endpoint verification via FastAPI's Swagger UI (`/docs`) as well as automated integration testing using `pytest` and `TestClient`.
* **Gemini chat URL:** https://gemini.google.com/app/e18409e5f58868ce