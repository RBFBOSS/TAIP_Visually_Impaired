import { useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { useLocation } from 'react-router'
import { AuthContext } from './AuthContext'
import type { AuthContextValue } from './AuthContext'
import { mockAuthService } from './mockAuthService'
import type { AuthService, Session } from './types'

/* Swap this one line for the real API client when the backend is ready. */
const authService: AuthService = mockAuthService

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(() =>
    authService.getSession(),
  )
  /* The history key the current call started on. A successful call leaves it
     set, so the guard on the page cannot redirect before the caller's own
     navigation runs; arriving on the new route changes the key and clears
     `busy` without any extra state. */
  const [callKey, setCallKey] = useState<string | null>(null)
  const { key } = useLocation()
  const busy = callKey !== null && callKey === key

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      busy,
      async signIn(email, password, keepSignedIn) {
        setCallKey(key)
        const result = await authService.signIn(
          email,
          password,
          keepSignedIn ? 'device' : 'tab',
        )
        if (result.status === 'success') {
          setSession(result.session)
          return result
        }
        setCallKey(null)
        return result
      },
      async createAccount(fullName, email, password) {
        setCallKey(key)
        const result = await authService.createAccount(
          fullName,
          email,
          password,
        )
        if (result.status === 'success') {
          setSession(result.session)
          return result
        }
        setCallKey(null)
        return result
      },
      async signOut() {
        setCallKey(key)
        await authService.signOut()
        setSession(null)
      },
    }),
    [session, busy, key],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
