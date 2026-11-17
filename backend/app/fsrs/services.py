"""Study session lifecycle and progress reporting."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from .models import (
    FeedbackLevel, Flashcard, LearningFeedback, ProgressReport,
    RecallRating, ReviewLog, ReviewSession, SessionStatus,
)
from .scheduling import FSRSService


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
