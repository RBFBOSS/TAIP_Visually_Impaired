/* A problem to report after a failed submit. The error summary link and the
   message beside the field are always the same string (rule R22). */
export type Problem = {
  fieldId: string
  message: string
}

/* The test the validated reference implementation uses. */
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

/* Rule R17: EVIS asks for a passphrase, not a short password. */
export const MIN_PASSWORD_LENGTH = 15

export function isBlank(value: string): boolean {
  return value.trim() === ''
}

export function isValidEmail(value: string): boolean {
  return EMAIL_PATTERN.test(value.trim())
}

export function meetsMinimumLength(value: string, minimum: number): boolean {
  return value.length >= minimum
}
