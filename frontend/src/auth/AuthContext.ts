import { createContext } from 'react'
import type { CreateAccountResult, Session, SignInResult } from './types'

export type AuthContextValue = {
  session: Session | null
  /* True while a sign-in, registration or sign-out call is in flight. Route
     guards stand down during it so they cannot redirect underneath a
     navigation the page is about to make. */
  busy: boolean
  signIn(
    email: string,
    password: string,
    keepSignedIn: boolean,
  ): Promise<SignInResult>
  createAccount(
    fullName: string,
    email: string,
    password: string,
  ): Promise<CreateAccountResult>
  signOut(): Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)
