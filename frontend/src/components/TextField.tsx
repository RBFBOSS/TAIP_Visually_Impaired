type TextFieldProps = {
  id: string
  label: string
  hint?: string
  error?: string
  type?: 'text' | 'email'
  autoComplete?: string
  spellCheck?: boolean
  value: string
  onChange: (value: string) => void
}

export default function TextField({
  id,
  label,
  hint,
  error,
  type = 'text',
  autoComplete,
  spellCheck,
  value,
  onChange,
}: TextFieldProps) {
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
      <input
        id={id}
        name={id}
        type={type}
        className={error ? 'input--error' : undefined}
        autoComplete={autoComplete}
        spellCheck={spellCheck}
        aria-describedby={describedBy === '' ? undefined : describedBy}
        aria-invalid={error ? true : undefined}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  )
}
