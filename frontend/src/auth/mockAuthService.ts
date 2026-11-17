import type {
  AuthService,
  Session,
  SessionPersistence,
} from './types'

const SESSION_KEY = 'evis-session'
const NETWORK_DELAY_MS = 300

/* Stands in for the account the backend will seed. */
const SEEDED_ACCOUNT = {
  fullName: 'Test Student',
  email: 'student@example.com',
  password: 'evis test password',
}

type MockAccount = {
  fullName: string
  email: string
  password: string
}

/* Accounts created during a test run. In memory only: they disappear on
   reload, and only a session's name and email ever reach web storage. */
const createdAccounts: MockAccount[] = []

function normaliseEmail(email: string): string {
  return email.trim().toLowerCase()
}

function wait(): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, NETWORK_DELAY_MS)
  })
}

function findAccount(email: string): MockAccount | null {
  const wanted = normaliseEmail(email)
  if (wanted === SEEDED_ACCOUNT.email) {
    return SEEDED_ACCOUNT
  }
  return createdAccounts.find((account) => account.email === wanted) ?? null
}

function isSession(value: unknown): value is Session {
  if (typeof value !== 'object' || value === null) {
    return false
  }
  const candidate = value as Partial<Session>
  return typeof candidate.fullName === 'string' && typeof candidate.email === 'string'
}

function readSession(): Session | null {
  for (const storage of [window.localStorage, window.sessionStorage]) {
    try {
      const stored = storage.getItem(SESSION_KEY)
      if (stored === null) {
        continue
      }
      const parsed: unknown = JSON.parse(stored)
      if (isSession(parsed)) {
        return parsed
      }
    } catch {
      /* Storage blocked, or the entry is not ours: treat it as no session. */
    }
  }
  return null
}

function clearSession() {
  for (const storage of [window.localStorage, window.sessionStorage]) {
    try {
      storage.removeItem(SESSION_KEY)
    } catch {
      /* Storage blocked: there is nothing to clear. */
    }
  }
}

function saveSession(session: Session, persistence: SessionPersistence) {
  clearSession()
  const storage =
    persistence === 'device' ? window.localStorage : window.sessionStorage
  try {
    storage.setItem(SESSION_KEY, JSON.stringify(session))
  } catch {
    /* Storage blocked: the session lasts as long as this page does. */
  }
}

export const mockAuthService: AuthService = {
  /* Reading web storage is instant, so this call carries no artificial delay:
     a pause here would blank the first paint of every page. */
  getSession() {
    return readSession()
  },

  async signIn(email, password, persistence) {
    await wait()
    const account = findAccount(email)
    if (account === null || account.password !== password) {
      return { status: 'invalid-credentials' }
    }
    const session: Session = {
      fullName: account.fullName,
      email: account.email,
    }
    saveSession(session, persistence)
    return { status: 'success', session }
  },

  async createAccount(fullName, email, password) {
    await wait()
    if (findAccount(email) !== null) {
      return { status: 'email-taken' }
    }
    const account: MockAccount = {
      fullName: fullName.trim(),
      email: normaliseEmail(email),
      password,
    }
    createdAccounts.push(account)
    /* Nothing asked about keeping a brand-new account, so it is scoped to the
       tab and a shared computer keeps no trace of it. */
    const session: Session = {
      fullName: account.fullName,
      email: account.email,
    }
    saveSession(session, 'tab')
    return { status: 'success', session }
  },

  async signOut() {
    await wait()
    clearSession()
  },
}
