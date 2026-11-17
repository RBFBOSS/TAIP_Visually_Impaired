import { useState } from 'react'

type PasswordFieldProps = {
  id: string
  label: string
  hint?: string
  error?: string
  autoComplete: 'current-password' | 'new-password'
  revealed: boolean
  onToggleReveal: () => void
  value: string
  onChange: (value: string) => void
}

export default function PasswordField({
  id,
  label,
  hint,
  error,
  autoComplete,
  revealed,
  onToggleReveal,
  value,
  onChange,
}: PasswordFieldProps) {
  /* The status region stays empty until the button is used, so nothing about
     the password is announced on page load (R18). */
  const [announced, setAnnounced] = useState(false)
  const hintId = `${id}-hint`
  const errorId = `${id}-error`
  const describedBy = [hint ? hintId : null, error ? errorId : null]
    .filter(Boolean)
    .join(' ')

  return (
    <div className={error ? 'form-group form-group--error' : 'form-group'}>
      <label htmlFor={id}>{label}</label>
      {hint ? (
        <p className="hint" id={hintId}>
          {hint}
        </p>
      ) : null}
      {error ? (
        <p className="error-message" id={errorId}>
          <span className="visually-hidden">Error:</span> {error}
        </p>
      ) : null}
      <div className="password-wrapper">
        <input
          id={id}
          name={id}
          type={revealed ? 'text' : 'password'}
          className={error ? 'input--error' : undefined}
          autoComplete={autoComplete}
          spellCheck={false}
          autoCapitalize="none"
          aria-describedby={describedBy === '' ? undefined : describedBy}
          aria-invalid={error ? true : undefined}
          value={value}
          onChange={(event) => onChange(event.target.value)}
        />
        <button
          type="button"
          className="button button--secondary"
          aria-controls={id}
          aria-label={revealed ? 'Hide password' : 'Show password'}
          onClick={() => {
            setAnnounced(true)
            onToggleReveal()
          }}
        >
          {revealed ? 'Hide' : 'Show'}
        </button>
      </div>
      <span className="visually-hidden" role="status">
        {announced
          ? revealed
            ? 'Your password is shown'
            : 'Your password is hidden'
          : ''}
      </span>
    </div>
  )
}
