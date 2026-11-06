from uuid import UUID

from app.flashcards.domain import Citation, Flashcard


class InvalidCitationError(Exception):
    """Raised when citation validation fails against business rules."""
    pass


class CitationValidator:
    """
    Domain service responsible for verifying citation integrity and source references.
    Ensures that flashcards are reliably linked to specific PDF sections and pages.
    """

    def verifySource(self, citation: Citation) -> bool:
        """
        Verifies that an individual citation points to a valid page and section,
        and contains non-empty source excerpt text.
        """
        if citation.pageNumber <= 0:
            return False

        if not isinstance(citation.sectionId, UUID):
            return False

        if not citation.sourceExcerpt or not citation.sourceExcerpt.strip():
            return False

        return True

    def validateCitation(self, card: Flashcard) -> bool:
        """
        Validates all citations owned by a flashcard.
        Enforces domain invariants (e.g., minimum 1 valid citation per flashcard).
        Raises InvalidCitationError if any citation is invalid or missing.
        """
        if not card.citations:
            raise InvalidCitationError(
                f"Flashcard {card.id} must have at least one citation."
            )

        for index, citation in enumerate(card.citations):
            if not self.verifySource(citation):
                raise InvalidCitationError(
                    f"Invalid citation at index {index} for flashcard {card.id}: "
                    f"page={citation.pageNumber}, sectionId={citation.sectionId}."
                )

        return True