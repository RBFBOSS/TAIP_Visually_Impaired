export type Session = {
  fullName: string
  email: string
}

/* Where a session lives. `device` survives closing the tab (localStorage),
   `tab` does not (sessionStorage). Rule R41 ties this to the "Keep me signed
   in" checkbox. */
export type SessionPersistence = 'device' | 'tab'

/* One result for every wrong combination of email and password, so the page
   can show the single generic message rule R25 requires. */
export type SignInResult =
  | { status: 'success'; session: Session }
  | { status: 'invalid-credentials' }

export type CreateAccountResult =
  | { status: 'success'; session: Session }
  | { status: 'email-taken' }

/* The only interface the app talks to. Replacing the mock with the FastAPI
   backend means writing another implementation of this and changing one line
   in AuthContext.tsx. */
export type AuthService = {
  /** The session already on this device or tab, if there is one. */
  getSession(): Session | null
  signIn(
    email: string,
    password: string,
    persistence: SessionPersistence,
  ): Promise<SignInResult>
  createAccount(
    fullName: string,
    email: string,
    password: string,
  ): Promise<CreateAccountResult>
  signOut(): Promise<void>
}
