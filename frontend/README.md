# EVIS frontend

The student-facing web app for EVIS (Education for Visually Impaired Students).

What is here now is the first slice of the interface: **Sign in**, **Create an account**, and the documents page they lead to. It is built to the rules in [`01_Documentation/05_Accessible_UIUX_Research.md`](../01_Documentation/05_Accessible_UIUX_Research.md) and ports the validated reference pages from section 8.7 of that document, with the same wording, markup and behaviour.

## Running it

```bash
npm install
npm run dev
```

Open the address Vite prints, `http://localhost:5173` by default.

| Command | What it does |
|---|---|
| `npm run dev` | Dev server with hot reload |
| `npm run build` | Type-check, then build into `dist/` |
| `npm run lint` | ESLint |
| `npm run preview` | Serve the built app |

## Test account

Sign-in runs against a mock in the browser. No backend is involved, so nothing you do here touches the database.

| Field | Value |
|---|---|
| Email | `student@example.com` |
| Password | `test` |

Accounts you create on the Create an account page work for the rest of that page session, and disappear when you reload.

## Routes

| URL | Page |
|---|---|
| `/` | Redirects to `/documents` when signed in, otherwise to `/sign-in` |
| `/sign-in` | Sign in |
| `/create-account` | Create an account |
| `/account-created` | Registration success |
| `/documents` | Your documents: PDF upload, the read-only study material viewer, and Sign out |
| anything else | Page not found |

There is no reset-password page yet, so the sign-in page has no "Forgot your password?" link. A link that goes nowhere costs a blind student more than no link at all.

## Study material viewer

The **Study material** section on *Your documents* reads the summary and flashcards the document-processing service saved for a document. Paste the `documentId` from a `POST /documents/{id}/generate` response and choose **Load study material**. The ids in the uploaded-documents list come from a different service and will not work here.

The dev server proxies `/documents/summary` and `/documents/flashcards` to the processing service on port 8001, so start it before loading anything:

```bash
cd backend/app/doc-processing
uv run python main.py
```

If the service is not running, the viewer says so for each part separately.

## What is mocked

`src/auth/mockAuthService.ts` is the only thing standing in for a server. It implements the `AuthService` interface in `src/auth/types.ts`:

- the one seeded account above
- accounts created in the browser, held in memory only
- about 300 ms of delay on sign-in, registration and sign-out
- `Check your email address and password` for any wrong combination, which never says which of the two was wrong (rule R25)
- `An account with this email address already exists` for a duplicate email

When the FastAPI backend is ready, write a real `AuthService` and change the one marked line at the top of `src/auth/AuthProvider.tsx`. Nothing else in the app talks to the sign-in server.

A session holds only the name and the email. "Keep me signed in" puts it in `localStorage`; leaving the box unchecked uses `sessionStorage`, so it goes when the tab closes (rule R41). An account created on the registration page is always tab-scoped, because that page never asks.

## Rules implemented

| Rules | Where they show up |
|---|---|
| R1–R5, R7 | Unique titles ending in "– EVIS", `lang="en"`, a skip link into `<main>`, one `h1` per page, the form first in `<main>`, and one set of words everywhere: "Sign in", "Create an account", "Sign out" |
| R8–R15 | Labels above fields, hints and errors tied on with `aria-describedby`, the right `autocomplete` tokens, `noValidate`, no `required` / `maxlength` / `autofocus` anywhere, validation on submit only, entered values kept, `spellcheck="false"` on email |
| R16–R19 | One password field, the minimum-length rule stated before it, Show/Hide with `aria-controls` and a hidden status region, re-masked on submit, paste never blocked |
| R20–R25 | The "Error: " title prefix, a focused error summary with one link per problem, each link moving focus to its field, the same message inline above the field with a visually-hidden "Error: ", `aria-invalid`, the left border on the group, and the one generic sign-in message |
| R26–R28 | Focused `role="alert"` success banners, no toasts, "Signed in as …" next to an explicit Sign out |
| R29–R31 | A 4px outline plus an 8px yellow halo on focus, yellow background and black text on focused links, focus order matching DOM order |
| R32–R36 | Light, dark and system themes at 7:1 contrast or better, forced-colors support, links underlined as well as coloured |
| R37–R40 | 20px base text and 25px controls through a 125% root, all sizing in `rem`, one 40rem column, reflow at 320px |
| R41 | "Keep me signed in", unchecked by default, with the shared-computer hint |
| R43 | Every route change updates the title and moves focus to the banner, or to the heading when there is no banner |
| R57 | Display settings in the header of every page, before sign-in, saved and re-applied before first paint |

Two deliberate changes from the reference stylesheet: the root size is a percentage rather than a fixed `20px`, so the browser's own font-size setting still applies, and `color-scheme` is set per theme so native controls and autofill colours match it.

## Not done yet

- Voice commands (deferred, section 12.1)
- Reset your password (section 8.3)
- Study sessions (section 9.2): reviewing and grading flashcards. The read-only study material viewer on `/documents` is the first slice
- An automated accessibility suite in CI. The checks in section 11 were run against this branch with a throwaway script that is not committed; see the pull request for what they covered and what they found
