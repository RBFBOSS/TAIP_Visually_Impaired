"""FSRS-inspired scheduler and card selection helpers."""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from .models import Flashcard, FSRSCardState, FSRSState, RecallRating


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
