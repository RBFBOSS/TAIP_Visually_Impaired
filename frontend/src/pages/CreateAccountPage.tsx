import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router'
import { useAuth } from '../auth/useAuth'
import ErrorSummary from '../components/ErrorSummary'
import PasswordField from '../components/PasswordField'
import TextField from '../components/TextField'
import { usePageTitle } from '../hooks/usePageTitle'
import { useRouteFocus } from '../hooks/useRouteFocus'
import { MIN_PASSWORD_LENGTH, isBlank, isValidEmail, meetsMinimumLength } from '../validation'
import type { Problem } from '../validation'

export default function CreateAccountPage() {
  const { createAccount, busy } = useAuth()
  const navigate = useNavigate()

  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [passwordRevealed, setPasswordRevealed] = useState(false)
  const [problems, setProblems] = useState<Problem[]>([])

  usePageTitle(
    problems.length > 0
      ? 'Error: Create an account – EVIS'
      : 'Create an account – EVIS',
  )
  useRouteFocus('create-account-heading')

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (busy) {
      return
    }

    /* Any submit re-masks a revealed password, including one that stops at
       validation, so the field is never left open on screen (R18). */
    setPasswordRevealed(false)

    const found: Problem[] = []
    if (isBlank(fullName)) {
      found.push({ fieldId: 'full-name', message: 'Enter your full name' })
    }
    if (isBlank(email)) {
      found.push({ fieldId: 'email', message: 'Enter an email address' })
    } else if (!isValidEmail(email)) {
      found.push({
        fieldId: 'email',
        message:
          'Enter an email address in the correct format, like name@example.com',
      })
    }
    if (isBlank(password)) {
      found.push({ fieldId: 'password', message: 'Create a password' })
    } else if (!meetsMinimumLength(password, MIN_PASSWORD_LENGTH)) {
      found.push({
        fieldId: 'password',
        message: `Create a password with at least ${MIN_PASSWORD_LENGTH} characters`,
      })
    }
    if (found.length > 0) {
      setProblems(found)
      return
    }

    const result = await createAccount(fullName, email, password)
    if (result.status === 'email-taken') {
      setProblems([
        {
          fieldId: 'email',
          message: 'An account with this email address already exists',
        },
      ])
      return
    }
    navigate('/account-created')
  }

  return (
    <>
      <ErrorSummary problems={problems} />
      <h1 id="create-account-heading" tabIndex={-1}>
        Create an account
      </h1>
      <p>
        Create one account to upload documents and study them as flashcards. If
        you already have an account, <Link to="/sign-in">sign in</Link>.
      </p>
      <form noValidate onSubmit={handleSubmit}>
        <TextField
          id="full-name"
          label="Full name"
          autoComplete="name"
          value={fullName}
          onChange={setFullName}
          error={
            problems.find((problem) => problem.fieldId === 'full-name')?.message
          }
        />
        <TextField
          id="email"
          label="Email address"
          hint="You will use this address to sign in."
          type="email"
          autoComplete="email"
          spellCheck={false}
          value={email}
          onChange={setEmail}
          error={problems.find((problem) => problem.fieldId === 'email')?.message}
        />
        <PasswordField
          id="password"
          label="Create a password"
          hint="Use at least 15 characters."
          autoComplete="new-password"
          value={password}
          onChange={setPassword}
          revealed={passwordRevealed}
          onToggleReveal={() => setPasswordRevealed((shown) => !shown)}
          error={
            problems.find((problem) => problem.fieldId === 'password')?.message
          }
        />
        <button
          type="submit"
          className="button button--primary"
          aria-disabled={busy || undefined}
        >
          Create account
        </button>
      </form>
    </>
  )
}
