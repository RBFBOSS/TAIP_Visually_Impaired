import { useLocation, useNavigate } from 'react-router'
import { useAuth } from '../auth/useAuth'
import SuccessBanner from '../components/SuccessBanner'
import { usePageTitle } from '../hooks/usePageTitle'
import { useRouteFocus } from '../hooks/useRouteFocus'

export default function DocumentsPage() {
  const { session, signOut, busy } = useAuth()
  const navigate = useNavigate()
  const { search } = useLocation()
  /* Announced once, after sign-in, and not again on every later visit. */
  const signedIn = new URLSearchParams(search).get('signed-in') === '1'

  usePageTitle('Your documents – EVIS')
  useRouteFocus(signedIn ? 'success-banner' : 'documents-heading')

  async function handleSignOut() {
    if (busy) {
      return
    }
    await signOut()
    navigate('/sign-in?signed-out=1')
  }

  /* The route guard holds this page while a sign-out is in flight, so the
     session can be gone for one render before the navigation lands. */
  if (session === null) {
    return null
  }

  return (
    <>
      {signedIn ? (
        <SuccessBanner heading="Success">
          <p>You are now signed in.</p>
        </SuccessBanner>
      ) : null}
      <h1 id="documents-heading" tabIndex={-1}>
        Your documents
      </h1>
      <p>
        Signed in as {session.fullName} ({session.email}).
      </p>
      <p>
        Uploading documents and studying flashcards are not built yet. This
        page is a placeholder, so you can test signing in and signing out.
      </p>
      <button
        type="button"
        className="button button--primary"
        aria-disabled={busy || undefined}
        onClick={handleSignOut}
      >
        Sign out
      </button>
    </>
  )
}
