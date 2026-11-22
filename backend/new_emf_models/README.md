# Model-Driven Development (MDD) — Study Sessions, FSRS Scheduling & Progress

This repository contains the metamodel, visual class diagrams, and Python code generation pipeline for the **Study Sessions, FSRS Scheduling & Progress** component, developed using the **Eclipse Modeling Framework (EMF)**.

---

## 1. Overview & Modeled Component

The modeled component covers the spaced-repetition study lifecycle and learner progress analytics:

* **Enumerations (`EEnum`):**
  * `RecallRating` (`AGAIN`, `HARD`, `GOOD`, `EASY`)
  * `SessionStatus` (`ACTIVE`, `COMPLETED`, `INTERRUPTED`)
  * `FSRSCardState` (`NEW`, `LEARNING`, `REVIEW`, `RELEARNING`)
  * `FeedbackLevel` (`TASK`, `PROCESS`, `SELF_REGULATION`)
* **Domain Classes (`EClass`):**
  * `User`: Represents a learner associated with study sessions and FSRS scheduling states.
  * `ReviewSession`: Tracks an active or completed study session, containing `ReviewLog` entries via composition and exposing the `endSession()` operation.
  * `ReviewLog`: Records individual flashcard review attempts, ratings, response latency, and timestamps.
  * `FSRSState`: Stores Free Spaced Repetition Scheduler (FSRS) parameters (`stability`, `difficulty`, `dueAt`, `lastReview`, `repetitions`, `lapses`, and card state) per user and flashcard.
  * `ProgressReport` & `LearningFeedback`: Aggregates review metrics (`totalReviews`, `dueCards`, `averageLatencyMs`) and structured feedback items.
  * `FlashcardRef`: Lightweight reference entity linking review logs and FSRS states to flashcards.
* **Relationships & Multiplicities:**
  * **Compositions (`containment="true"`):** `ReviewSession` $\rightarrow$ `ReviewLog` (`0..*`), `ProgressReport` $\rightarrow$ `LearningFeedback` (`0..*`).
  * **Bidirectional Associations (`eOpposite`):** `User` $\leftrightarrow$ `ReviewSession` (`0..*`), `User` $\leftrightarrow$ `FSRSState` (`0..*`), `ReviewSession` $\leftrightarrow$ `ReviewLog` (`0..*`).
  * **Unidirectional References:** `ReviewLog` $\rightarrow$ `FlashcardRef` (`1`), `FSRSState` $\rightarrow$ `FlashcardRef` (`1`), `ProgressReport` $\rightarrow$ `User` (`1`).

---

## 2. Project Structure

```text
.
├── study_session_fsrs.ecore   # EMF Ecore metamodel (XMI format)
├── gen_from_ecore.py          # Python code generator reading the .ecore metamodel
├── study_models.py            # Auto-generated Python dataclasses and Enums
├── diagrams/                  # Exported EMF / Sirius class diagrams (PNG/SVG)
└── README.md                  # Process documentation
```

---

## 3. Step-by-Step Modeling & Generation Process

### Step 1: Creating and Validating the Ecore Metamodel in Eclipse
1. Open **Eclipse Modeling Tools** and select or create a workspace.
2. Create a new project via **File $\rightarrow$ New $\rightarrow$ Project... $\rightarrow$ Modeling Project** (or **General $\rightarrow$ Project**).
3. Add `study_session_fsrs.ecore` to the project and refresh (`F5`).
4. Double-click `study_session_fsrs.ecore` to inspect the structural tree in the **Sample Ecore Model Editor**.
5. Right-click the root package `studysessionsfsrs` and select **Validate** to verify that all classifiers, data types, multiplicities, and opposite references conform to Ecore rules.

### Step 2: Generating the Class Diagram
1. Right-click `study_session_fsrs.ecore` in the **Project Explorer** and select **Initialize Ecore Diagram...** (using Sirius Ecore Tools).
2. In the diagram editor canvas, use **Existing Elements** from the right-hand **Palette** to add all `EClass` and `EEnum` classifiers onto the canvas.
3. Arrange the classes, attributes, operations, containment diamonds, and bidirectional references for readability, then export the diagram as an image (`PNG` / `SVG`).

### Step 3: Generating Python Code from the Metamodel
Since EMF's built-in `.genmodel` targets Java, a custom Python generator (`gen_from_ecore.py`) is used to transform the `.ecore` metamodel directly into typed Python structures:

1. Navigate to the directory containing `study_session_fsrs.ecore` and `gen_from_ecore.py`.
2. Run the generator from the command line:
   ```bash
   python gen_from_ecore.py study_session_fsrs.ecore study_models.py
   ```
3. The script parses all `EEnum` and `EClass` definitions, maps Ecore primitive types (`EString`, `EInt`, `EFloat`, `EDate`) to Python types (`str`, `int`, `float`, `datetime`), preserves inheritance order, and outputs `study_models.py` containing Python `Enum` classes, `@dataclass` models, typed collections, and operation stubs.