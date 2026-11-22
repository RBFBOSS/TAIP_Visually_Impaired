import { useId, useRef, useState, type FormEvent } from 'react'
import TextField from './TextField'

/* The document-processing service saves one summary and one batch of
   flashcards per document id. These mirror the JSON of its two GET
   endpoints, /documents/summary/{id} and /documents/flashcards/{id}. */
interface Citation {
  id: string
  page_number: number
  source_excerpt: string
}

interface Summary {
  documentId: string
  summary: string
  summary_citation: Citation
}

interface Flashcard {
  id: string
  documentId: string
  question: string
  answer: string
  citations: Citation[]
}

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

const ID_ERROR = 'Enter a document ID in the form 3fa85f64-5717-4562-b3fc-2c963f66afa6.'
const SUMMARY_NOT_SAVED = 'No summary has been saved for this document yet.'
const FLASHCARDS_NOT_SAVED = 'No flashcards have been saved for this document yet.'
const SUMMARY_UNAVAILABLE =
  'The summary could not be loaded. Check that the document processing service is running, then try again.'
const FLASHCARDS_UNAVAILABLE =
  'The flashcards could not be loaded. Check that the document processing service is running, then try again.'

function buildAnnouncement(
  summary: Summary | null,
  summaryProblem: string | null,
  flashcards: Flashcard[] | null,
  flashcardsProblem: string | null,
): string {
  const parts: string[] = []
  parts.push(summary !== null ? 'Summary loaded.' : (summaryProblem ?? ''))
  parts.push(
    flashcards === null
      ? (flashcardsProblem ?? '')
      : flashcards.length === 0
        ? FLASHCARDS_NOT_SAVED
        : `${flashcards.length} flashcards loaded.`,
  )
  return parts.filter(Boolean).join(' ')
}

export default function StudyMaterialViewer() {
  const documentIdFieldId = useId()
  const resultsRef = useRef<HTMLDivElement | null>(null)

  const [documentId, setDocumentId] = useState('')
  const [idError, setIdError] = useState(false)
  const [loading, setLoading] = useState(false)
  const [statusAnnouncement, setStatusAnnouncement] = useState('')
  const [summary, setSummary] = useState<Summary | null>(null)
  const [summaryProblem, setSummaryProblem] = useState<string | null>(null)
  const [flashcards, setFlashcards] = useState<Flashcard[] | null>(null)
  const [flashcardsProblem, setFlashcardsProblem] = useState<string | null>(null)

  async function handleLoadSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (loading) {
      return
    }

    const trimmedId = documentId.trim()
    if (!UUID_PATTERN.test(trimmedId)) {
      setIdError(true)
      setStatusAnnouncement(`Error: ${ID_ERROR}`)
      return
    }

    setIdError(false)
    setLoading(true)
    setSummary(null)
    setSummaryProblem(null)
    setFlashcards(null)
    setFlashcardsProblem(null)
    setStatusAnnouncement('Loading study material. Please wait.')

    const [summaryResponse, flashcardsResponse] = await Promise.all([
      fetch(`/documents/summary/${encodeURIComponent(trimmedId)}`).catch(() => null),
      fetch(`/documents/flashcards/${encodeURIComponent(trimmedId)}`).catch(() => null),
    ])

    let nextSummary: Summary | null = null
    let nextSummaryProblem: string | null = null
    let nextFlashcards: Flashcard[] | null = null
    let nextFlashcardsProblem: string | null = null

    if (summaryResponse !== null && summaryResponse.ok) {
      nextSummary = (await summaryResponse.json()) as Summary
    } else if (summaryResponse?.status === 404) {
      nextSummaryProblem = SUMMARY_NOT_SAVED
    } else {
      /* Anything else, including the dev proxy's error when the service is
         down, means the summary cannot be read right now. */
      nextSummaryProblem = SUMMARY_UNAVAILABLE
    }

    if (flashcardsResponse !== null && flashcardsResponse.ok) {
      nextFlashcards = (await flashcardsResponse.json()) as Flashcard[]
    } else {
      nextFlashcardsProblem = FLASHCARDS_UNAVAILABLE
    }

    setSummary(nextSummary)
    setSummaryProblem(nextSummaryProblem)
    setFlashcards(nextFlashcards)
    setFlashcardsProblem(nextFlashcardsProblem)
    setLoading(false)
    setStatusAnnouncement(
      buildAnnouncement(nextSummary, nextSummaryProblem, nextFlashcards, nextFlashcardsProblem),
    )
    requestAnimationFrame(() => {
      resultsRef.current?.focus()
    })
  }

  const hasResults =
    summary !== null ||
    summaryProblem !== null ||
    flashcards !== null ||
    flashcardsProblem !== null

  return (
    <section aria-labelledby="study-material-heading" className="document-section">
      <h2 id="study-material-heading">Study material</h2>
      <p>
        Paste the document ID returned when the study material was generated to read the
        summary and flashcards saved for that document.
      </p>

      <div className="visually-hidden" role="status" aria-live="polite" aria-atomic="true">
        {statusAnnouncement}
      </div>

      <form onSubmit={handleLoadSubmit} noValidate>
        <TextField
          id={documentIdFieldId}
          label="Processing document ID"
          hint="The documentId from a generation response, for example 3fa85f64-5717-4562-b3fc-2c963f66afa6."
          error={idError ? ID_ERROR : undefined}
          autoComplete="off"
          spellCheck={false}
          value={documentId}
          onChange={(value) => {
            setIdError(false)
            setDocumentId(value)
          }}
        />
        <button
          type="submit"
          className="button button--primary"
          aria-disabled={loading || undefined}
        >
          {loading ? 'Loading study material…' : 'Load study material'}
        </button>
      </form>

      {hasResults ? (
        <div ref={resultsRef} tabIndex={-1}>
          {summary !== null ? (
            <>
              <h3>Summary</h3>
              <p>{summary.summary}</p>
              <p className="hint">
                Source: page {summary.summary_citation.page_number}, “{summary.summary_citation.source_excerpt}”
              </p>
            </>
          ) : null}
          {summaryProblem !== null ? <p>{summaryProblem}</p> : null}

          {flashcards !== null ? (
            <>
              <h3>{flashcards.length > 0 ? `Flashcards (${flashcards.length})` : 'Flashcards'}</h3>
              {flashcards.length === 0 ? (
                <p>{FLASHCARDS_NOT_SAVED}</p>
              ) : (
                <ol className="document-list">
                  {flashcards.map((card, index) => (
                    <li key={card.id} className="document-list__item">
                      <h4>
                        Card {index + 1} of {flashcards.length}
                      </h4>
                      <p>
                        <strong>Question:</strong> {card.question}
                      </p>
                      <p>
                        <strong>Answer:</strong> {card.answer}
                      </p>
                      {card.citations.map((citation) => (
                        <p key={citation.id} className="hint">
                          Source: page {citation.page_number}, “{citation.source_excerpt}”
                        </p>
                      ))}
                    </li>
                  ))}
                </ol>
              )}
            </>
          ) : null}
          {flashcardsProblem !== null ? <p>{flashcardsProblem}</p> : null}
        </div>
      ) : null}
    </section>
  )
}
