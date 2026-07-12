-- ============================================================================
-- Module 4: Users
-- PostgreSQL 17
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    full_name VARCHAR(150) NOT NULL,

    email CITEXT NOT NULL,

    password_hash TEXT NOT NULL,

    -- Global system role.
    -- Restaurant-specific permissions are handled in restaurant_members.
    role VARCHAR(20) NOT NULL DEFAULT 'owner',

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_users_email UNIQUE (email),

    CONSTRAINT chk_users_role
        CHECK (role IN ('owner', 'admin'))
);

-- Index for login lookups.
CREATE INDEX idx_users_email
ON users (email);

-- Automatically maintain updated_at.
CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE
ON users
FOR EACH ROW
EXECUTE FUNCTION trigger_set_updated_at();

COMMENT ON TABLE users IS
'System users. Restaurant-specific permissions are managed via restaurant_members.';