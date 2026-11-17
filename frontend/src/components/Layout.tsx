import type { MouseEvent, ReactNode } from 'react'
import DisplaySettings from './DisplaySettings'

function skipToMainContent(event: MouseEvent<HTMLAnchorElement>) {
  /* Done here rather than left to the browser: a hash change would look like
     a navigation to the router and pull focus to the page heading. */
  event.preventDefault()
  document.getElementById('main-content')?.focus()
}

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <>
      <a className="skip-link" href="#main-content" onClick={skipToMainContent}>
        Skip to main content
      </a>
      <header className="site-header">
        <div className="container">
          <p className="brand">
            EVIS <small>Education for visually impaired students</small>
          </p>
          <DisplaySettings />
        </div>
      </header>
      <main id="main-content" className="container" tabIndex={-1}>
        {children}
      </main>
      <footer className="site-footer">
        <div className="container">
          <p>EVIS team project.</p>
        </div>
      </footer>
    </>
  )
}
