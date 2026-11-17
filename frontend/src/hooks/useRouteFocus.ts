import { useEffect } from 'react'
import { useLocation, useNavigationType } from 'react-router'

/* Module scope on purpose: this is per document, not per component. Every page
   calls this hook, and each one mounts fresh on arrival, so a ref inside the
   hook would treat every arrival as a first load. It resets when the document
   reloads, which is exactly the lifetime "first load" has. */
let previousKey: string | null = null

/* Moves focus to the new page's banner, or to its heading when there is no
   banner, so a screen reader announces the navigation (rule R43).

   Two cases are left alone. The entry the document was loaded with keeps focus
   at the top, so Tab reaches the skip link first (R15) — but only until the
   student navigates away, because pressing Back to that entry is a navigation
   like any other and has to be announced. A redirect is skipped too: the
   student did not ask for it and the skip link must stay reachable. */
export function useRouteFocus(elementId: string) {
  const { key } = useLocation()
  const navigationType = useNavigationType()

  useEffect(() => {
    const firstRender = previousKey === null
    const navigated = previousKey !== key
    previousKey = key
    if (firstRender || !navigated || navigationType === 'REPLACE') {
      return
    }
    document.getElementById(elementId)?.focus()
  }, [elementId, key, navigationType])
}
