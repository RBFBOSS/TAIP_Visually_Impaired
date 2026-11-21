-- ==========================================
-- 1. ENUM TYPES
-- ==========================================

DO $$
BEGIN
    CREATE TYPE user_role AS ENUM (
        'student',
        'validator',
        'admin'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END
$$;

DO $$
BEGIN
    CREATE TYPE account_status AS ENUM (
        'PENDING',
        'ACTIVE',
        'SUSPENDED'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END
$$;

DO $$
BEGIN
    CREATE TYPE mentorship_status AS ENUM (
        'PENDING',
        'ACTIVE',
        'REJECTED',
        'REMOVED'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END
$$;

DO $$
BEGIN
    CREATE TYPE approval_status AS ENUM (
        'DRAFT',
        'APPROVED',
        'REJECTED'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END
$$;

DO $$
BEGIN
    CREATE TYPE processing_status AS ENUM (
        'UPLOADED',
        'PROCESSING',
        'COMPLETED',
        'FAILED'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END
$$;

DO $$
BEGIN
    CREATE TYPE recall_rating AS ENUM (
        'AGAIN',
        'HARD',
        'GOOD',
        'EASY'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END
$$;

DO $$
BEGIN
    CREATE TYPE session_status AS ENUM (
        'ACTIVE',
        'COMPLETED',
        'INTERRUPTED'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END
$$;

DO $$
BEGIN
    CREATE TYPE fsrs_card_state AS ENUM (
        'NEW',
        'LEARNING',
        'REVIEW',
        'RELEARNING'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END
$$;

-- ==========================================
-- 2. TABLES
-- ==========================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role user_role NOT NULL DEFAULT 'student',
    status account_status NOT NULL DEFAULT 'ACTIVE',
    verified_by UUID,
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_users_verified_by
        FOREIGN KEY (verified_by)
        REFERENCES users(id)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS student_validators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL,
    validator_id UUID NOT NULL,
    status mentorship_status NOT NULL DEFAULT 'PENDING',
    initiated_by UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_sv_student
        FOREIGN KEY (student_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_sv_validator
        FOREIGN KEY (validator_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_sv_initiated_by
        FOREIGN KEY (initiated_by)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_student_validator_pair
        UNIQUE (student_id, validator_id),

    CONSTRAINT ck_sv_different_users
        CHECK (student_id <> validator_id)
);

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL,
    managed_by_validator_id UUID,
    title VARCHAR(255) NOT NULL DEFAULT '',
    filename VARCHAR(1024) NOT NULL,
    storage_path VARCHAR(1024) NOT NULL DEFAULT '',
    content_type VARCHAR(100) NOT NULL DEFAULT 'application/pdf',
    size_bytes BIGINT NOT NULL DEFAULT 0,
    sha256 VARCHAR(64),
    status processing_status NOT NULL DEFAULT 'UPLOADED',
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_documents_student
        FOREIGN KEY (student_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_documents_validator
        FOREIGN KEY (managed_by_validator_id)
        REFERENCES users(id)
        ON DELETE SET NULL,

    CONSTRAINT ck_documents_size_bytes
        CHECK (size_bytes >= 0)
);

CREATE TABLE IF NOT EXISTS document_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    heading VARCHAR(1024),
    content TEXT NOT NULL,
    page_number INTEGER,
    chunk_index INTEGER NOT NULL,

    CONSTRAINT fk_document_sections_document
        FOREIGN KEY (document_id)
        REFERENCES documents(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_document_sections_document_chunk
        UNIQUE (document_id, chunk_index),

    CONSTRAINT ck_document_sections_page_number
        CHECK (page_number IS NULL OR page_number > 0),

    CONSTRAINT ck_document_sections_chunk_index
        CHECK (chunk_index >= 0)
);

CREATE TABLE IF NOT EXISTS global_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL UNIQUE,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_global_summaries_document
        FOREIGN KEY (document_id)
        REFERENCES documents(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS section_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    section_id UUID NOT NULL UNIQUE,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_section_summaries_section
        FOREIGN KEY (section_id)
        REFERENCES document_sections(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS decks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    title VARCHAR(500) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_decks_document
        FOREIGN KEY (document_id)
        REFERENCES documents(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS flashcards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deck_id UUID,
    document_id UUID NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    status approval_status NOT NULL DEFAULT 'DRAFT',
    validated_by UUID,
    validated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_flashcards_deck
        FOREIGN KEY (deck_id)
        REFERENCES decks(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_flashcards_validated_by
        FOREIGN KEY (validated_by)
        REFERENCES users(id)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flashcard_id UUID NOT NULL,
    section_id UUID,
    page_number INTEGER,
    source_excerpt TEXT NOT NULL,

    CONSTRAINT fk_citations_flashcard
        FOREIGN KEY (flashcard_id)
        REFERENCES flashcards(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_citations_section
        FOREIGN KEY (section_id)
        REFERENCES document_sections(id)
        ON DELETE RESTRICT,

    CONSTRAINT ck_citations_page_number
        CHECK (page_number IS NULL OR page_number > 0)
);

CREATE TABLE IF NOT EXISTS document_processing_summaries (
    document_id UUID PRIMARY KEY,
    content TEXT NOT NULL,
    citation_id UUID NOT NULL,
    citation_page_number INTEGER NOT NULL,
    citation_source_excerpt TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_document_processing_summaries_citation_page_number
        CHECK (citation_page_number > 0)
);

CREATE TABLE IF NOT EXISTS review_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMPTZ,
    status session_status NOT NULL DEFAULT 'ACTIVE',

    CONSTRAINT fk_review_sessions_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT ck_review_sessions_time_range
        CHECK (ended_at IS NULL OR ended_at >= started_at)
);

CREATE TABLE IF NOT EXISTS review_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    flashcard_id UUID NOT NULL,
    rating recall_rating NOT NULL,
    response_latency_ms INTEGER NOT NULL,
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_review_logs_session
        FOREIGN KEY (session_id)
        REFERENCES review_sessions(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_review_logs_flashcard
        FOREIGN KEY (flashcard_id)
        REFERENCES flashcards(id)
        ON DELETE RESTRICT,

    CONSTRAINT ck_review_logs_response_latency
        CHECK (response_latency_ms >= 0)
);

CREATE TABLE IF NOT EXISTS fsrs_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    flashcard_id UUID NOT NULL,
    state fsrs_card_state NOT NULL DEFAULT 'NEW',
    stability DOUBLE PRECISION,
    difficulty DOUBLE PRECISION,
    due_at TIMESTAMPTZ,
    last_review TIMESTAMPTZ,
    repetitions INTEGER NOT NULL DEFAULT 0,
    lapses INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT fk_fsrs_states_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_fsrs_states_flashcard
        FOREIGN KEY (flashcard_id)
        REFERENCES flashcards(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_fsrs_states_user_flashcard
        UNIQUE (user_id, flashcard_id),

    CONSTRAINT ck_fsrs_states_stability
        CHECK (stability IS NULL OR stability >= 0),

    CONSTRAINT ck_fsrs_states_difficulty
        CHECK (difficulty IS NULL OR (difficulty >= 0 AND difficulty <= 10)),

    CONSTRAINT ck_fsrs_states_repetitions
        CHECK (repetitions >= 0),

    CONSTRAINT ck_fsrs_states_lapses
        CHECK (lapses >= 0)
);

-- ==========================================
-- 3. INDEXES
-- ==========================================

CREATE INDEX IF NOT EXISTS ix_users_role_status
    ON users(role, status);

CREATE INDEX IF NOT EXISTS ix_student_validators_student_id
    ON student_validators(student_id);

CREATE INDEX IF NOT EXISTS ix_student_validators_validator_id
    ON student_validators(validator_id);

CREATE INDEX IF NOT EXISTS ix_documents_student_id
    ON documents(student_id);

CREATE INDEX IF NOT EXISTS ix_documents_validator_id
    ON documents(managed_by_validator_id);

CREATE INDEX IF NOT EXISTS ix_document_sections_document_id
    ON document_sections(document_id);

CREATE INDEX IF NOT EXISTS ix_decks_document_id
    ON decks(document_id);

CREATE INDEX IF NOT EXISTS ix_flashcards_deck_id
    ON flashcards(deck_id);

CREATE INDEX IF NOT EXISTS ix_flashcards_document_id
    ON flashcards(document_id);

CREATE INDEX IF NOT EXISTS ix_flashcards_status
    ON flashcards(status);

CREATE INDEX IF NOT EXISTS ix_flashcards_validated_by
    ON flashcards(validated_by);

CREATE INDEX IF NOT EXISTS ix_citations_flashcard_id
    ON citations(flashcard_id);

CREATE INDEX IF NOT EXISTS ix_citations_section_id
    ON citations(section_id);

CREATE INDEX IF NOT EXISTS ix_review_sessions_user_id
    ON review_sessions(user_id);

CREATE INDEX IF NOT EXISTS ix_review_logs_session_id
    ON review_logs(session_id);

CREATE INDEX IF NOT EXISTS ix_review_logs_flashcard_id
    ON review_logs(flashcard_id);

CREATE INDEX IF NOT EXISTS ix_review_logs_reviewed_at
    ON review_logs(reviewed_at);

CREATE INDEX IF NOT EXISTS ix_fsrs_states_user_due_at
    ON fsrs_states(user_id, due_at);

CREATE INDEX IF NOT EXISTS ix_fsrs_states_flashcard_id
    ON fsrs_states(flashcard_id);
