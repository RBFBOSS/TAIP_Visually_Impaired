import { Link } from 'react-router'
import SuccessBanner from '../components/SuccessBanner'
import { usePageTitle } from '../hooks/usePageTitle'
import { useRouteFocus } from '../hooks/useRouteFocus'

export default function AccountCreatedPage() {
  usePageTitle('Account created – EVIS')
  useRouteFocus('success-banner')

  return (
    <>
      <SuccessBanner heading="Success">
        <p>Your account has been created. You are now signed in.</p>
      </SuccessBanner>
      <h1 id="welcome-heading" tabIndex={-1}>
        Welcome to EVIS
      </h1>
      <p>You can now upload your first document.</p>
      <p>
        <Link to="/documents">Go to your documents</Link>
      </p>
    </>
  )
}
