/* A problem to report after a failed submit. The error summary link and the
   message beside the field are always the same string (rule R22). */
export type Problem = {
  fieldId: string
  message: string
}

/* The test the validated reference implementation uses. */
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

/* Rule R17: 8 characters, matching the GOV.UK minimum. This sits below NIST
   SP 800-63B-4's 15-character minimum for single-factor sign-in; the research
   document records the deviation and why it was accepted. */
export const MIN_PASSWORD_LENGTH = 8

export function isBlank(value: string): boolean {
  return value.trim() === ''
}

export function isValidEmail(value: string): boolean {
  return EMAIL_PATTERN.test(value.trim())
}

export function meetsMinimumLength(value: string, minimum: number): boolean {
  return value.length >= minimum
}
