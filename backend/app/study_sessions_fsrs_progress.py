"""
Minimal flashcard study feed with FSRS-inspired spaced repetition.

Mock-data-only implementation. No database or external packages required.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4


# ============================================================
# 1. STUDY DOMAIN
# ============================================================

class RecallRating(Enum):
    HARD = "HARD"   # Student remembered, but struggled.
    GOOD = "GOOD"   # Student remembered correctly.
    EASY = "EASY"   # Student remembered immediately.


class SessionStatus(Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    INTERRUPTED = "INTERRUPTED"


class FSRSCardState(Enum):
    NEW = "NEW"
    LEARNING = "LEARNING"
    REVIEW = "REVIEW"
    RELEARNING = "RELEARNING"


class FeedbackLevel(Enum):
    TASK = "TASK"
    PROCESS = "PROCESS"
    SELF_REGULATION = "SELF_REGULATION"


@dataclass
class User:
    id: UUID
    role: str


@dataclass
class Flashcard:
    id: UUID
    question: str
    answer: str
    approval_status: str = "APPROVED"


@dataclass
class ReviewLog:
    id: UUID
    flashcard_id: UUID
    rating: RecallRating
    response_latency_ms: int
    reviewed_at: datetime


@dataclass
class ReviewSession:
    id: UUID
    user_id: UUID
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: SessionStatus = SessionStatus.ACTIVE
    review_logs: List[ReviewLog] = field(default_factory=list)

    def end_session(self):
        self.ended_at = datetime.now()
        self.status = SessionStatus.COMPLETED


# ============================================================
# 2. FSRS SCHEDULING
# ============================================================

@dataclass
class FSRSState:
    id: UUID
    user_id: UUID
    flashcard_id: UUID
    state: FSRSCardState = FSRSCardState.NEW
    stability: float = 0.0
    difficulty: float = 5.0
    due_at: Optional[datetime] = None
    last_review: Optional[datetime] = None
    repetitions: int = 0
    lapses: int = 0


class FSRSScheduler:
    """Interface-like base class for a scheduling algorithm."""

    def calculate_next_review(
        self, state: FSRSState, rating: RecallRating
    ) -> FSRSState:
        raise NotImplementedError


class FSRSAdapter(FSRSScheduler):
    """
    Simplified FSRS-inspired scheduler.

    HARD: short interval; the card needs more practice.
    GOOD: medium interval; the student knows the card.
    EASY: long interval; the student knows it very well.

    Successful reviews increase stability and gradually increase intervals.
    Difficulty is kept between 1 and 10.
    """

    def calculate_next_review(
        self, state: FSRSState, rating: RecallRating
    ) -> FSRSState:
        now = datetime.now()
        state.last_review = now
        state.repetitions += 1

        if rating == RecallRating.HARD:
            state.state = FSRSCardState.LEARNING
            state.difficulty = min(10.0, state.difficulty + 0.7)
            state.stability = max(0.5, state.stability * 1.25)

            # Short intervals make difficult cards return frequently.
            interval_days = min(
                2.0, 0.25 * (1.5 ** (state.repetitions - 1))
            )

        elif rating == RecallRating.GOOD:
            state.state = FSRSCardState.REVIEW
            state.difficulty = max(1.0, state.difficulty - 0.2)
            state.stability = max(1.0, state.stability * 2.0)

            interval_days = (
                2.0 * (1.8 ** (state.repetitions - 1))
            )

        else:  # EASY
            state.state = FSRSCardState.REVIEW
            state.difficulty = max(1.0, state.difficulty - 0.5)
            state.stability = max(1.0, state.stability * 2.5)

            interval_days = (
                5.0 * (2.2 ** (state.repetitions - 1))
            )

        # Keep intervals bounded in this small demonstration.
        interval_days = min(interval_days, 90.0)

        state.due_at = now + timedelta(days=interval_days)

        return state


class FSRSService:
    def __init__(
        self,
        states: List[FSRSState],
        scheduler: FSRSScheduler
    ):
        self.states = states
        self.scheduler = scheduler

    def get_state(
        self, user_id: UUID, card_id: UUID
    ) -> FSRSState:
        return next(
            state for state in self.states
            if state.user_id == user_id
            and state.flashcard_id == card_id
        )

    def get_new_cards(
        self,
        user_id: UUID,
        cards: List[Flashcard]
    ) -> List[Flashcard]:
        """Return approved cards that this user has never reviewed."""

        reviewed_ids = {
            state.flashcard_id
            for state in self.states
            if state.user_id == user_id
            and state.repetitions > 0
        }

        return [
            card for card in cards
            if card.approval_status == "APPROVED"
            and card.id not in reviewed_ids
        ]

    def get_due_cards(
        self,
        user_id: UUID,
        cards: List[Flashcard]
    ) -> List[Flashcard]:

        now = datetime.now()
        card_by_id = {card.id: card for card in cards}
        due = []

        for state in self.states:
            if (
                state.user_id == user_id
                and state.repetitions > 0
                and state.due_at is not None
                and state.due_at <= now
            ):
                card = card_by_id.get(state.flashcard_id)

                if card and card.approval_status == "APPROVED":
                    due.append(card)

        # Most overdue cards appear first.
        due.sort(
            key=lambda card: self.get_state(
                user_id, card.id
            ).due_at
        )

        return due

    def get_next_scheduled_cards(
        self,
        user_id: UUID,
        cards: List[Flashcard]
    ) -> List[Flashcard]:
        """
        Return previously reviewed cards ordered by their next review date.

        This is the fallback feed: if no card is due yet, the feed can still
        continue by showing the card whose scheduled date is closest.
        Showing it early is an intentional feed choice, not strict FSRS timing.
        """

        card_by_id = {card.id: card for card in cards}

        scheduled_states = [
            state for state in self.states
            if state.user_id == user_id
            and state.repetitions > 0
            and state.due_at is not None
            and state.flashcard_id in card_by_id
            and card_by_id[
                state.flashcard_id
            ].approval_status == "APPROVED"
        ]

        scheduled_states.sort(
            key=lambda state: state.due_at
        )

        return [
            card_by_id[state.flashcard_id]
            for state in scheduled_states
        ]

    def schedule_review(
        self,
        user_id: UUID,
        card_id: UUID,
        rating: RecallRating
    ) -> FSRSState:

        state = self.get_state(user_id, card_id)

        return self.scheduler.calculate_next_review(
            state, rating
        )

    def get_next_review(
        self,
        user_id: UUID,
        card_id: UUID
    ) -> Optional[datetime]:

        return self.get_state(user_id, card_id).due_at


# ============================================================
# 3. STUDY AND PROGRESS SERVICES
# ============================================================

@dataclass
class ProgressReport:
    total_reviews: int
    due_cards: int
    average_latency_ms: float
    generated_at: datetime


@dataclass
class LearningFeedback:
    level: FeedbackLevel
    message: str


class StudyService:
    def __init__(
        self,
        cards: List[Flashcard],
        sessions: List[ReviewSession],
        fsrs_service: FSRSService
    ):
        self.cards = cards
        self.sessions = sessions
        self.fsrs_service = fsrs_service

    def start_session(
        self,
        user_id: UUID
    ) -> ReviewSession:

        session = ReviewSession(
            id=uuid4(),
            user_id=user_id,
            started_at=datetime.now()
        )

        self.sessions.append(session)

        return session

    def get_next_card(
        self,
        session_id: UUID
    ) -> Optional[Flashcard]:
        """
        Feed order:
        1. Show all never-seen cards first.
        2. Then show due cards, prioritizing the most overdue.
        3. If nothing is due, show the card with the nearest due date.
        4. Avoid repeating a card until other available cards were shown
           in the current session. When all cards have appeared, start a
           new feed cycle, so the student can continue indefinitely.
        """

        session = self._get_active_session(session_id)
        user_id = session.user_id

        new_cards = self.fsrs_service.get_new_cards(
            user_id, self.cards
        )

        due_cards = self.fsrs_service.get_due_cards(
            user_id, self.cards
        )

        if new_cards:
            candidates = new_cards

        elif due_cards:
            candidates = due_cards

        else:
            candidates = (
                self.fsrs_service.get_next_scheduled_cards(
                    user_id, self.cards
                )
            )

        if not candidates:
            return None

        already_seen_this_session = {
            log.flashcard_id
            for log in session.review_logs
        }

        # Prefer cards not yet shown in this session.
        for card in candidates:
            if card.id not in already_seen_this_session:
                return card

        # All cards in this feed category have appeared during this session.
        # Start another cycle, allowing an endless study feed.
        return candidates[0]

    def submit_grade(
        self,
        session_id: UUID,
        card_id: UUID,
        rating: RecallRating,
        latency_ms: int
    ) -> ReviewLog:

        session = self._get_active_session(session_id)

        if latency_ms < 0:
            raise ValueError(
                "Response latency cannot be negative."
            )

        card = next(
            card for card in self.cards
            if card.id == card_id
            and card.approval_status == "APPROVED"
        )

        log = ReviewLog(
            id=uuid4(),
            flashcard_id=card.id,
            rating=rating,
            response_latency_ms=latency_ms,
            reviewed_at=datetime.now()
        )

        session.review_logs.append(log)

        self.fsrs_service.schedule_review(
            session.user_id,
            card_id,
            rating
        )

        return log

    def stop_session(self, session_id: UUID):

        session = self._get_active_session(session_id)

        session.ended_at = datetime.now()
        session.status = SessionStatus.INTERRUPTED

    def complete_session(self, session_id: UUID):

        self._get_active_session(session_id).end_session()

    def _get_active_session(
        self,
        session_id: UUID
    ) -> ReviewSession:

        session = next(
            s for s in self.sessions
            if s.id == session_id
        )

        if session.status != SessionStatus.ACTIVE:
            raise ValueError(
                "This study session is not active."
            )

        return session


class ProgressService:
    def __init__(
        self,
        sessions: List[ReviewSession],
        fsrs_service: FSRSService,
        cards: List[Flashcard]
    ):
        self.sessions = sessions
        self.fsrs_service = fsrs_service
        self.cards = cards

    def get_user_progress(
        self,
        user_id: UUID
    ) -> ProgressReport:

        logs = [
            log
            for session in self.sessions
            if session.user_id == user_id
            for log in session.review_logs
        ]

        average = (
            sum(
                log.response_latency_ms
                for log in logs
            ) / len(logs)
            if logs else 0.0
        )

        due_count = len(
            self.fsrs_service.get_due_cards(
                user_id, self.cards
            )
        )

        return ProgressReport(
            total_reviews=len(logs),
            due_cards=due_count,
            average_latency_ms=average,
            generated_at=datetime.now()
        )

    def calculate_recall_metrics(
        self,
        user_id: UUID
    ) -> dict:

        logs = [
            log
            for session in self.sessions
            if session.user_id == user_id
            for log in session.review_logs
        ]

        total = len(logs)

        return {
            "total": total,
            "hard": sum(
                log.rating == RecallRating.HARD
                for log in logs
            ),
            "good": sum(
                log.rating == RecallRating.GOOD
                for log in logs
            ),
            "easy": sum(
                log.rating == RecallRating.EASY
                for log in logs
            )
        }

    def generate_feedback(
        self,
        user_id: UUID
    ) -> List[LearningFeedback]:

        metrics = self.calculate_recall_metrics(user_id)
        feedback = []

        if metrics["total"] == 0:

            feedback.append(
                LearningFeedback(
                    FeedbackLevel.TASK,
                    "Start reviewing flashcards to track your progress."
                )
            )

        elif metrics["hard"] > (
            metrics["good"] + metrics["easy"]
        ):

            feedback.append(
                LearningFeedback(
                    FeedbackLevel.PROCESS,
                    "Many cards are difficult. Keep practicing them regularly."
                )
            )

        else:

            feedback.append(
                LearningFeedback(
                    FeedbackLevel.SELF_REGULATION,
                    "You are making progress. Keep following your review feed."
                )
            )

        return feedback


# ============================================================
# 4. MOCK DATA AND INFINITE-FEED DEMONSTRATION
# ============================================================

def main():

    user = User(
        id=uuid4(),
        role="STUDENT"
    )

    cards = [
        Flashcard(
            uuid4(),
            "What is Python?",
            "A high-level programming language."
        ),

        Flashcard(
            uuid4(),
            "What is a variable?",
            "A named storage location for a value."
        ),

        Flashcard(
            uuid4(),
            "What is a function?",
            "A reusable block of code."
        ),

        Flashcard(
            uuid4(),
            "What is a loop?",
            "A structure that repeats instructions."
        ),

        Flashcard(
            uuid4(),
            "What is a list?",
            "An ordered collection of items."
        )
    ]

    # Create one scheduling record for each card.
    # due_at=None and repetitions=0 mean the card is new.

    states = [
        FSRSState(
            id=uuid4(),
            user_id=user.id,
            flashcard_id=card.id
        )
        for card in cards
    ]

    sessions = []

    fsrs_service = FSRSService(
        states,
        FSRSAdapter()
    )

    study_service = StudyService(
        cards,
        sessions,
        fsrs_service
    )

    progress_service = ProgressService(
        sessions,
        fsrs_service,
        cards
    )

    session = study_service.start_session(user.id)

    print("STUDY FEED STARTED")
    print(
        "First, the student will see every new flashcard.\n"
    )

    # The first five cards are new. After that, the feed uses scheduling.
    # Ratings are mock student responses for this demonstration.

    mock_ratings = [
        RecallRating.HARD,
        RecallRating.EASY,
        RecallRating.GOOD,
        RecallRating.HARD,
        RecallRating.EASY,
        RecallRating.GOOD,
        RecallRating.HARD,
        RecallRating.EASY,
        RecallRating.GOOD,
        RecallRating.HARD,
        RecallRating.EASY,
        RecallRating.GOOD
    ]

    for index, rating in enumerate(
        mock_ratings,
        start=1
    ):

        card = study_service.get_next_card(
            session.id
        )

        if card is None:

            print(
                "No approved flashcards are available."
            )

            break

        print(f"\nFeed item {index}")
        print("Question:", card.question)
        print("Answer:", card.answer)
        print("Student rating:", rating.value)

        study_service.submit_grade(
            session_id=session.id,
            card_id=card.id,
            rating=rating,
            latency_ms=2000 + index * 150
        )

        state = fsrs_service.get_state(
            user.id,
            card.id
        )

        interval = state.due_at - state.last_review

        print(
            "Stability:",
            round(state.stability, 2)
        )

        print(
            "Difficulty:",
            round(state.difficulty, 2)
        )

        print(
            "Next scheduled review:",
            state.due_at.strftime("%Y-%m-%d %H:%M")
        )

        print(
            "Scheduled interval:",
            interval
        )

    study_service.complete_session(
        session.id
    )

    report = progress_service.get_user_progress(
        user.id
    )

    print("\n========== PROGRESS ==========")

    print(
        "Total reviews:",
        report.total_reviews
    )

    print(
        "Currently due cards:",
        report.due_cards
    )

    print(
        "Average response time (ms):",
        round(report.average_latency_ms, 2)
    )

    print(
        "Rating counts:",
        progress_service.calculate_recall_metrics(
            user.id
        )
    )

    print("\n========== FEEDBACK ==========")

    for feedback in progress_service.generate_feedback(
        user.id
    ):

        print(
            f"[{feedback.level.value}] {feedback.message}"
        )


if __name__ == "__main__":
    main()