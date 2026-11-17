import { useEffect, useRef } from 'react'
import type { Problem } from '../validation'

function focusField(fieldId: string) {
  const field = document.getElementById(fieldId)
  if (field === null) {
    return
  }
  /* Focus without scrolling first, then bring the whole group into view, so
     the label and the message beside it are on screen together, the way the
     GOV.UK summary behaves. */
  field.focus({ preventScroll: true })
  const target = field.closest('.form-group') ?? field
  target.scrollIntoView({ block: 'center' })
}

export default function ErrorSummary({ problems }: { problems: Problem[] }) {
  const summaryRef = useRef<HTMLDivElement>(null)

  /* The summary takes focus whenever it appears, and again when a second
     submit produces a new set of problems (R21). */
  useEffect(() => {
    if (problems.length === 0) {
      return
    }
    summaryRef.current?.focus()
  }, [problems])

  if (problems.length === 0) {
    return null
  }

  return (
    <div
      className="error-summary"
      id="error-summary"
      role="alert"
      tabIndex={-1}
      aria-labelledby="error-summary-title"
      ref={summaryRef}
    >
      <h2 className="error-summary__title" id="error-summary-title">
        There is a problem
      </h2>
      <ul className="error-summary__list">
        {problems.map((problem) => (
          <li key={problem.fieldId}>
            <a
              href={`#${problem.fieldId}`}
              onClick={(event) => {
                /* Stopped so the hash never reaches the router. */
                event.preventDefault()
                focusField(problem.fieldId)
              }}
            >
              {problem.message}
            </a>
          </li>
        ))}
      </ul>
    </div>
  )
}
