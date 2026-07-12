-- ============================================================================
-- Module 7: Refresh Tokens
-- PostgreSQL 17
-- ============================================================================

CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,

    restaurant_id UUID NOT NULL,

    token_hash TEXT NOT NULL,

    expires_at TIMESTAMPTZ NOT NULL,

    revoked_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_refresh_tokens_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_refresh_tokens_restaurant
        FOREIGN KEY (restaurant_id)
        REFERENCES restaurants(id)
        ON DELETE CASCADE
);

-- Indexes
CREATE UNIQUE INDEX idx_refresh_tokens_hash
ON refresh_tokens(token_hash);

CREATE INDEX idx_refresh_tokens_user
ON refresh_tokens(user_id);

CREATE INDEX idx_refresh_tokens_restaurant
ON refresh_tokens(restaurant_id);

CREATE INDEX idx_refresh_tokens_expires_at
ON refresh_tokens(expires_at);

-- Automatically maintain updated_at
CREATE TRIGGER trg_refresh_tokens_updated_at
BEFORE UPDATE
ON refresh_tokens
FOR EACH ROW
EXECUTE FUNCTION trigger_set_updated_at();

COMMENT ON TABLE refresh_tokens IS
'Stores hashed JWT refresh tokens for authenticated sessions.';