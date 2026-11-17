import { Link } from 'react-router'
import { usePageTitle } from '../hooks/usePageTitle'
import { useRouteFocus } from '../hooks/useRouteFocus'

export default function NotFoundPage() {
  usePageTitle('Page not found – EVIS')
  useRouteFocus('not-found-heading')

  return (
    <>
      <h1 id="not-found-heading" tabIndex={-1}>
        Page not found
      </h1>
      <p>We could not find the page you asked for.</p>
      <p>
        <Link to="/sign-in">Go to sign in</Link>
      </p>
    </>
  )
}
