import { useContext } from 'react'
import { AuthContext } from './AuthContext'
import type { AuthContextValue } from './AuthContext'

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext)
  if (value === null) {
    throw new Error('useAuth must be used inside an AuthProvider')
  }
  return value
}
