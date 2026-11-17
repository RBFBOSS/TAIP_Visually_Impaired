import { useEffect, useRef, useState } from 'react'

type ThemeChoice = 'light' | 'dark' | 'system'
type TextSizeChoice = '100' | '125' | '150'

const THEME_KEY = 'evis-theme'
const TEXT_SIZE_KEY = 'evis-textsize'

/* The root size is a percentage rather than the reference's fixed 20px, so
   the browser's own font-size preference still applies. 125% of the browser
   default is that 20px base (R37). */
const ROOT_FONT_SIZE = 125

const THEME_VALUES: ThemeChoice[] = ['light', 'dark', 'system']
const TEXT_SIZE_VALUES: TextSizeChoice[] = ['100', '125', '150']

const THEMES: { id: string; value: ThemeChoice; label: string }[] = [
  { id: 'theme-light', value: 'light', label: 'Light' },
  { id: 'theme-dark', value: 'dark', label: 'Dark' },
  { id: 'theme-system', value: 'system', label: 'System' },
]

const TEXT_SIZES: { id: string; value: TextSizeChoice; label: string }[] = [
  { id: 'size-100', value: '100', label: '100%' },
  { id: 'size-125', value: '125', label: '125%' },
  { id: 'size-150', value: '150', label: '150%' },
]

function readChoice<T extends string>(
  key: string,
  allowed: T[],
  fallback: T,
): T {
  try {
    const stored = window.localStorage.getItem(key)
    return allowed.find((value) => value === stored) ?? fallback
  } catch {
    return fallback
  }
}

function saveChoice(key: string, value: string) {
  try {
    window.localStorage.setItem(key, value)
  } catch {
    /* Storage blocked: the choice still applies for this visit. */
  }
}

/* "System" removes the override and lets the CSS media query decide, so the
   theme is never inferred from anything but the OS preference (R32). */
function applyTheme(theme: ThemeChoice) {
  if (theme === 'light' || theme === 'dark') {
    document.documentElement.setAttribute('data-theme', theme)
  } else {
    document.documentElement.removeAttribute('data-theme')
  }
}

function applyTextSize(size: TextSizeChoice) {
  document.documentElement.style.fontSize = `${(ROOT_FONT_SIZE * Number(size)) / 100}%`
}

export default function DisplaySettings() {
  const [open, setOpen] = useState(false)
  const [theme, setTheme] = useState<ThemeChoice>(() =>
    readChoice(THEME_KEY, THEME_VALUES, 'system'),
  )
  const [textSize, setTextSize] = useState<TextSizeChoice>(() =>
    readChoice(TEXT_SIZE_KEY, TEXT_SIZE_VALUES, '100'),
  )
  const toggleRef = useRef<HTMLButtonElement>(null)
  const panelRef = useRef<HTMLDivElement>(null)

  /* The inline script in index.html already applied both settings before the
     first paint; these keep the document in step from then on. */
  useEffect(() => {
    applyTheme(theme)
  }, [theme])

  useEffect(() => {
    applyTextSize(textSize)
  }, [textSize])

  /* Opening moves focus into the panel, to the choice already selected.
     Closing returns it to the disclosure button (R57). */
  useEffect(() => {
    if (!open) {
      return
    }
    const panel = panelRef.current
    if (panel === null) {
      return
    }
    const selected =
      panel.querySelector<HTMLInputElement>('input:checked') ??
      panel.querySelector<HTMLInputElement>('input')
    selected?.focus()
  }, [open])

  function handleToggle() {
    if (open) {
      setOpen(false)
      toggleRef.current?.focus()
    } else {
      setOpen(true)
    }
  }

  function chooseTheme(value: ThemeChoice) {
    setTheme(value)
    saveChoice(THEME_KEY, value)
  }

  function chooseTextSize(value: TextSizeChoice) {
    setTextSize(value)
    saveChoice(TEXT_SIZE_KEY, value)
  }

  return (
    <div className="display-settings">
      <button
        type="button"
        ref={toggleRef}
        className="button button--secondary display-settings__toggle"
        aria-expanded={open}
        aria-controls="display-panel"
        onClick={handleToggle}
      >
        Display settings
      </button>
      {/* The panel stays in the document while collapsed so aria-controls
          always resolves, and hidden keeps it out of the Tab order: one stop
          before the form. */}
      <div
        className="display-settings__panel"
        id="display-panel"
        ref={panelRef}
        hidden={!open}
      >
        <fieldset>
          <legend>Theme</legend>
          <div className="choice-row">
            {THEMES.map((choice) => (
              <div className="choice" key={choice.id}>
                <input
                  id={choice.id}
                  name="evis-theme"
                  type="radio"
                  value={choice.value}
                  checked={theme === choice.value}
                  onChange={() => chooseTheme(choice.value)}
                />
                <label htmlFor={choice.id}>{choice.label}</label>
              </div>
            ))}
          </div>
        </fieldset>
        <fieldset>
          <legend>Text size</legend>
          <div className="choice-row">
            {TEXT_SIZES.map((choice) => (
              <div className="choice" key={choice.id}>
                <input
                  id={choice.id}
                  name="evis-textsize"
                  type="radio"
                  value={choice.value}
                  checked={textSize === choice.value}
                  onChange={() => chooseTextSize(choice.value)}
                />
                <label htmlFor={choice.id}>{choice.label}</label>
              </div>
            ))}
          </div>
        </fieldset>
      </div>
    </div>
  )
}
