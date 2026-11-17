import type { ReactNode } from 'react'

/* The banner every completed action ends in (rule R26). Route focus moves
   here, so it carries the id the focus hook looks for. */
export default function SuccessBanner({
  heading,
  children,
}: {
  heading: string
  children: ReactNode
}) {
  return (
    <div
      className="success-banner"
      id="success-banner"
      role="alert"
      tabIndex={-1}
      aria-labelledby="success-banner-title"
    >
      <h2 id="success-banner-title">{heading}</h2>
      {children}
    </div>
  )
}
