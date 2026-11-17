import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router'
import { useAuth } from '../auth/useAuth'
import ErrorSummary from '../components/ErrorSummary'
import PasswordField from '../components/PasswordField'
import SuccessBanner from '../components/SuccessBanner'
import TextField from '../components/TextField'
import { usePageTitle } from '../hooks/usePageTitle'
import { useRouteFocus } from '../hooks/useRouteFocus'
import { isBlank, isValidEmail } from '../validation'
import type { Problem } from '../validation'

export default function SignInPage() {
  const { signIn, busy } = useAuth()
  const navigate = useNavigate()
  const { search } = useLocation()
  /* Signed-out arrives as a query parameter, the way the reference pages do
     it, so the banner is announced once after sign-out and not on every later
     visit (R26, R27). */
  const signedOut = new URLSearchParams(search).get('signed-out') === '1'

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [keepSignedIn, setKeepSignedIn] = useState(false)
  const [passwordRevealed, setPasswordRevealed] = useState(false)
  const [problems, setProblems] = useState<Problem[]>([])

  usePageTitle(
    problems.length > 0 ? 'Error: Sign in – EVIS' : 'Sign in – EVIS',
  )
  useRouteFocus(signedOut ? 'success-banner' : 'sign-in-heading')

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (busy) {
      return
    }

    /* Any submit re-masks a revealed password, including one that stops at
       validation, so the field is never left open on screen (R18). */
    setPasswordRevealed(false)

    /* Validation runs only on submit, and everything typed is kept (R11, R12). */
    const found: Problem[] = []
    if (isBlank(email)) {
      found.push({ fieldId: 'email', message: 'Enter your email address' })
    } else if (!isValidEmail(email)) {
      found.push({
        fieldId: 'email',
        message:
          'Enter an email address in the correct format, like name@example.com',
      })
    }
    if (isBlank(password)) {
      found.push({ fieldId: 'password', message: 'Enter your password' })
    }
    if (found.length > 0) {
      setProblems(found)
      return
    }

    const result = await signIn(email, password, keepSignedIn)
    if (result.status === 'invalid-credentials') {
      /* One generic message, tied to the email field: it must never say which
         of the two was wrong. The password is cleared, the email kept (R25). */
      setPassword('')
      setProblems([
        {
          fieldId: 'email',
          message: 'Check your email address and password',
        },
      ])
      return
    }
    navigate('/documents?signed-in=1')
  }

  return (
    <>
      <ErrorSummary problems={problems} />
      {signedOut ? (
        <SuccessBanner heading="Success">
          <p>You have signed out.</p>
        </SuccessBanner>
      ) : null}
      <h1 id="sign-in-heading" tabIndex={-1}>
        Sign in
      </h1>
      <form noValidate onSubmit={handleSubmit}>
        <TextField
          id="email"
          label="Email address"
          type="email"
          autoComplete="email"
          spellCheck={false}
          value={email}
          onChange={setEmail}
          error={problems.find((problem) => problem.fieldId === 'email')?.message}
        />
        <PasswordField
          id="password"
          label="Password"
          autoComplete="current-password"
          value={password}
          onChange={setPassword}
          revealed={passwordRevealed}
          onToggleReveal={() => setPasswordRevealed((shown) => !shown)}
          error={
            problems.find((problem) => problem.fieldId === 'password')?.message
          }
        />
        <div className="form-group">
          <p className="hint" id="keep-signed-in-hint">
            Stay signed in on this device. Do not use this on a shared computer.
          </p>
          <div className="checkbox-row">
            <input
              id="keep-signed-in"
              name="keep-signed-in"
              type="checkbox"
              aria-describedby="keep-signed-in-hint"
              checked={keepSignedIn}
              onChange={(event) => setKeepSignedIn(event.target.checked)}
            />
            <label htmlFor="keep-signed-in">Keep me signed in</label>
          </div>
        </div>
        <button
          type="submit"
          className="button button--primary"
          aria-disabled={busy || undefined}
        >
          Sign in
        </button>
      </form>
      {/* No "Forgot your password?" link until a reset page exists: a link
          that goes nowhere costs more than no link. */}
      <p>
        <Link to="/create-account">Create an account</Link>
      </p>
    </>
  )
}
