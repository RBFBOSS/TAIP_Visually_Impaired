 import { useId, useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import { useLocation, useNavigate } from 'react-router'
import { useAuth } from '../auth/useAuth'
import SuccessBanner from '../components/SuccessBanner'
import { usePageTitle } from '../hooks/usePageTitle'
import { useRouteFocus } from '../hooks/useRouteFocus'

const MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024 // 25 MB
const DEFAULT_UPLOAD_ERROR = 'The PDF could not be uploaded. Try again.'

interface UploadedDocument {
  id: string
  title: string
  originalFilename: string
  sizeBytes: number
  uploadedAt: string
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`
  }
  const kilobytes = bytes / 1024
  if (kilobytes < 1024) {
    return `${kilobytes.toFixed(1)} KB`
  }
  return `${(kilobytes / 1024).toFixed(1)} MB`
}

function stripPdfExtension(filename: string): string {
  return filename.replace(/\.pdf$/i, '')
}

function validatePdfFile(file: File | null): string | null {
  if (!file) {
    return 'Choose a PDF file before uploading.'
  }
  const isPdfMime = file.type === 'application/pdf'
  const isPdfExtension = file.name.toLowerCase().endsWith('.pdf')
  if (!isPdfMime && !isPdfExtension) {
    return 'The selected file must be a PDF (.pdf).'
  }
  if (file.size === 0) {
    return 'The selected PDF file is empty.'
  }
  if (file.size > MAX_FILE_SIZE_BYTES) {
    return 'The selected PDF file must be 25 MB or smaller.'
  }
  return null
}

function focusAfterRender(element: HTMLElement | null) {
  requestAnimationFrame(() => {
    element?.focus()
  })
}

export default function DocumentsPage() {
  const { session, signOut, busy } = useAuth()
  const navigate = useNavigate()
  const { search } = useLocation()
  const signedIn = new URLSearchParams(search).get('signed-in') === '1'

  usePageTitle('Your documents – EVIS')
  useRouteFocus(signedIn ? 'success-banner' : 'documents-heading')

  const fileInputId = useId()
  const fileHintId = useId()
  const fileErrorId = useId()
  const selectedFileStatusId = useId()

  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const triggerButtonRef = useRef<HTMLButtonElement | null>(null)
  const errorSummaryRef = useRef<HTMLDivElement | null>(null)

  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [fileError, setFileError] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [statusAnnouncement, setStatusAnnouncement] = useState('')
  const [uploadSuccessMessage, setUploadSuccessMessage] = useState<string | null>(null)
  const [documents, setDocuments] = useState<UploadedDocument[]>([])

  const isInteractionDisabled = uploading || busy

  function reportFileError(message: string, clearSelection = false) {
    if (clearSelection) {
      setSelectedFile(null)
    }
    setFileError(message)
    setStatusAnnouncement(`Error: ${message}`)
    focusAfterRender(errorSummaryRef.current)
  }

  function handleChooseFileClick() {
    if (isInteractionDisabled) {
      return
    }
    fileInputRef.current?.click()
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const nextFile = event.target.files?.[0] ?? null
    setUploadSuccessMessage(null)

    if (!nextFile) {
      setSelectedFile(null)
      setFileError(null)
      setStatusAnnouncement('No file selected.')
      return
    }

    const validationError = validatePdfFile(nextFile)
    if (validationError) {
      event.target.value = ''
      reportFileError(validationError, true)
      return
    }

    setFileError(null)
    setSelectedFile(nextFile)
    setStatusAnnouncement(
      `Selected PDF file ${nextFile.name}, size ${formatFileSize(nextFile.size)}.`,
    )
  }

  async function handleUploadSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (isInteractionDisabled) {
      return
    }

    const validationError = validatePdfFile(selectedFile)
    if (validationError || !selectedFile) {
      reportFileError(validationError ?? 'Choose a PDF file before uploading.')
      return
    }

    setFileError(null)
    setUploadSuccessMessage(null)
    setUploading(true)
    setStatusAnnouncement(`Uploading ${selectedFile.name}. Please wait.`)

    try {
      const defaultTitle = stripPdfExtension(selectedFile.name)
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('title', defaultTitle)

      const apiBaseUrl =
        import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') ?? 'http://localhost:8000'

      const response = await fetch(`${apiBaseUrl}/pdf_upload/upload`, {
        method: 'POST',
        credentials: 'include',
        body: formData,
      })

      if (!response.ok) {
        const body = await response.json().catch(() => null)
        const message = typeof body?.detail === 'string' ? body.detail : DEFAULT_UPLOAD_ERROR
        throw new Error(message)
      }

      const uploaded = (await response.json()) as {
        id?: string
        title?: string
        original_filename?: string
        size_bytes?: number
        created_at?: string
      }

      const newDoc: UploadedDocument = {
        id: uploaded.id ?? crypto.randomUUID(),
        title: uploaded.title ?? defaultTitle,
        originalFilename: uploaded.original_filename ?? selectedFile.name,
        sizeBytes: uploaded.size_bytes ?? selectedFile.size,
        uploadedAt: uploaded.created_at ?? new Date().toISOString(),
      }

      setDocuments((prev) => [newDoc, ...prev])
      const successText = `${newDoc.originalFilename} has been uploaded.`
      setUploadSuccessMessage(successText)
      setStatusAnnouncement(successText)
      setSelectedFile(null)

      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      focusAfterRender(triggerButtonRef.current)
    } catch (error) {
      const message = error instanceof Error ? error.message : DEFAULT_UPLOAD_ERROR
      reportFileError(message)
    } finally {
      setUploading(false)
    }
  }

  async function handleSignOut() {
    if (isInteractionDisabled) {
      return
    }
    await signOut()
    navigate('/sign-in?signed-out=1')
  }

  if (session === null) {
    return null
  }

  const describedByIds = [
    fileHintId,
    selectedFile ? selectedFileStatusId : null,
    fileError ? fileErrorId : null,
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <>
      <div className="visually-hidden" role="status" aria-live="polite" aria-atomic="true">
        {statusAnnouncement}
      </div>

      {signedIn ? (
        <SuccessBanner heading="Success">
          <p>You are now signed in.</p>
        </SuccessBanner>
      ) : null}

      {uploadSuccessMessage ? (
        <SuccessBanner heading="Upload complete">
          <p>{uploadSuccessMessage}</p>
        </SuccessBanner>
      ) : null}

      {fileError ? (
        <div
          ref={errorSummaryRef}
          className="error-summary"
          role="alert"
          tabIndex={-1}
          aria-labelledby="upload-error-summary-heading"
        >
          <h2 id="upload-error-summary-heading">There is a problem with your upload</h2>
          <ul>
            <li>
              <a
                href={`#${fileInputId}`}
                onClick={(e) => {
                  e.preventDefault()
                  triggerButtonRef.current?.focus()
                }}
              >
                {fileError}
              </a>
            </li>
          </ul>
        </div>
      ) : null}

      <h1 id="documents-heading" tabIndex={-1}>
        Your documents
      </h1>
      <p>
        Signed in as {session.fullName} ({session.email}).
      </p>

      <section aria-labelledby="upload-section-heading" className="document-section">
        <h2 id="upload-section-heading">Upload a PDF document</h2>

        <form onSubmit={handleUploadSubmit} noValidate>
          <div className={`form-group${fileError ? ' form-group--error' : ''}`}>
            <label htmlFor={fileInputId}>PDF file</label>
            <p id={fileHintId} className="hint">
              Select a single PDF file (.pdf), up to 25 MB.
            </p>

            {fileError ? (
              <p id={fileErrorId} className="error-message">
                <span className="visually-hidden">Error: </span>
                {fileError}
              </p>
            ) : null}

            <input
              ref={fileInputRef}
              id={fileInputId}
              name="file"
              type="file"
              accept="application/pdf,.pdf"
              className="visually-hidden"
              tabIndex={-1}
              aria-invalid={fileError ? true : undefined}
              aria-describedby={describedByIds}
              onChange={handleFileChange}
            />

            <div className="button-group">
              <button
                ref={triggerButtonRef}
                type="button"
                className="button button--secondary"
                aria-describedby={describedByIds}
                aria-disabled={isInteractionDisabled || undefined}
                onClick={handleChooseFileClick}
              >
                {selectedFile ? 'Choose a different PDF file' : 'Choose PDF file'}
              </button>

              <button
                type="submit"
                className="button button--primary"
                aria-disabled={!selectedFile || isInteractionDisabled || undefined}
              >
                {uploading ? 'Uploading PDF…' : 'Upload PDF'}
              </button>
            </div>

            <p id={selectedFileStatusId} className="selected-file-status">
              {selectedFile
                ? `Selected file: ${selectedFile.name} (${formatFileSize(selectedFile.size)})`
                : 'No PDF file selected.'}
            </p>
          </div>
        </form>
      </section>

      <section aria-labelledby="uploaded-list-heading" className="document-section">
        <h2 id="uploaded-list-heading">Uploaded documents</h2>
        {documents.length === 0 ? (
          <p>You have not uploaded any PDF documents yet.</p>
        ) : (
          <ul className="document-list">
            {documents.map((doc) => (
              <li key={doc.id} className="document-list__item">
                <strong>{doc.title}</strong>
                <span className="hint">
                  {' '}
                  ({doc.originalFilename}, {formatFileSize(doc.sizeBytes)})
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <button
        type="button"
        className="button button--secondary"
        aria-disabled={isInteractionDisabled || undefined}
        onClick={handleSignOut}
      >
        Sign out
      </button>
    </>
  )
}