import type { ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router'
import { useAuth } from './auth/useAuth'
import Layout from './components/Layout'
import AccountCreatedPage from './pages/AccountCreatedPage'
import CreateAccountPage from './pages/CreateAccountPage'
import DocumentsPage from './pages/DocumentsPage'
import NotFoundPage from './pages/NotFoundPage'
import SignInPage from './pages/SignInPage'

/* Both guards stand down while an auth call is in flight, so they cannot
   redirect in the middle of the navigation the page is about to make. */
function RequireSignedOut({ children }: { children: ReactNode }) {
  const { session, busy } = useAuth()
  if (session !== null && !busy) {
    return <Navigate to="/documents" replace />
  }
  return <>{children}</>
}

function RequireSignedIn({ children }: { children: ReactNode }) {
  const { session, busy } = useAuth()
  if (session === null) {
    return busy ? null : <Navigate to="/sign-in" replace />
  }
  return <>{children}</>
}

function Home() {
  const { session } = useAuth()
  return <Navigate to={session === null ? '/sign-in' : '/documents'} replace />
}

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route
          path="/sign-in"
          element={
            <RequireSignedOut>
              <SignInPage />
            </RequireSignedOut>
          }
        />
        <Route
          path="/create-account"
          element={
            <RequireSignedOut>
              <CreateAccountPage />
            </RequireSignedOut>
          }
        />
        <Route
          path="/account-created"
          element={
            <RequireSignedIn>
              <AccountCreatedPage />
            </RequireSignedIn>
          }
        />
        <Route
          path="/documents"
          element={
            <RequireSignedIn>
              <DocumentsPage />
            </RequireSignedIn>
          }
        />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Layout>
  )
}

export default App
