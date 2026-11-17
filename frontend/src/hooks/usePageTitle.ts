import { useEffect } from 'react'

/* Keeps <title> in step with the page. Callers add the "Error: " prefix that
   rule R20 requires after a failed submit. */
export function usePageTitle(title: string) {
  useEffect(() => {
    document.title = title
  }, [title])
}
