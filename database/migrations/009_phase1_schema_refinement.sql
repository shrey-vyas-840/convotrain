-- ============================================================================
-- Migration: phase1_schema_refinement
-- Restaurant Knowledge OS
-- PostgreSQL 17
-- ============================================================================

BEGIN;

-- ============================================================================
-- USERS
-- ============================================================================

-- Remove old global role.
ALTER TABLE users
DROP CONSTRAINT IF EXISTS chk_users_role;

ALTER TABLE users
DROP COLUMN IF EXISTS role;

-- Platform-wide role.
ALTER TABLE users
ADD COLUMN platform_role VARCHAR(20) NOT NULL DEFAULT 'user';

ALTER TABLE users
ADD COLUMN is_email_verified BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE users
ADD COLUMN last_login_at TIMESTAMPTZ;

ALTER TABLE users
ADD CONSTRAINT chk_users_platform_role
CHECK (
    platform_role IN (
        'user',
        'support',
        'admin',
        'super_admin'
    )
);

CREATE INDEX IF NOT EXISTS idx_users_platform_role
ON users(platform_role);

-- ============================================================================
-- RESTAURANTS
-- ============================================================================

-- Replace JSON language preferences with TEXT[].
ALTER TABLE restaurants
DROP COLUMN IF EXISTS language_preferences;

ALTER TABLE restaurants
ADD COLUMN supported_languages TEXT[] NOT NULL
DEFAULT ARRAY['en'];

-- Rename lifecycle column.
ALTER TABLE restaurants
RENAME COLUMN status TO lifecycle_status;

ALTER TABLE restaurants
RENAME CONSTRAINT chk_restaurant_status
TO chk_restaurant_lifecycle_status;

ALTER TABLE restaurants
DROP CONSTRAINT chk_restaurant_lifecycle_status;

ALTER TABLE restaurants
ADD CONSTRAINT chk_restaurant_lifecycle_status
CHECK (
    lifecycle_status IN (
        'draft',
        'active',
        'suspended',
        'archived'
    )
);

ALTER TABLE restaurants
ADD COLUMN created_by UUID;

ALTER TABLE restaurants
ADD COLUMN updated_by UUID;

ALTER TABLE restaurants
ADD CONSTRAINT fk_restaurants_created_by
FOREIGN KEY (created_by)
REFERENCES users(id)
ON DELETE SET NULL;

ALTER TABLE restaurants
ADD CONSTRAINT fk_restaurants_updated_by
FOREIGN KEY (updated_by)
REFERENCES users(id)
ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_restaurants_created_by
ON restaurants(created_by);

CREATE INDEX IF NOT EXISTS idx_restaurants_updated_by
ON restaurants(updated_by);

-- ============================================================================
-- RESTAURANT MEMBERS
-- ============================================================================

ALTER TABLE restaurant_members
ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active';

ALTER TABLE restaurant_members
ADD COLUMN joined_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE restaurant_members
ADD COLUMN invited_by UUID;

ALTER TABLE restaurant_members
ADD CONSTRAINT fk_restaurant_members_invited_by
FOREIGN KEY (invited_by)
REFERENCES users(id)
ON DELETE SET NULL;

ALTER TABLE restaurant_members
ADD CONSTRAINT chk_restaurant_member_status
CHECK (
    status IN (
        'active',
        'invited',
        'suspended',
        'removed'
    )
);

CREATE INDEX IF NOT EXISTS idx_restaurant_members_status
ON restaurant_members(status);

-- ============================================================================
-- REFRESH TOKENS
-- ============================================================================

ALTER TABLE refresh_tokens
ADD COLUMN device_info TEXT;

ALTER TABLE refresh_tokens
ADD COLUMN user_agent TEXT;

ALTER TABLE refresh_tokens
ADD COLUMN ip_address INET;

-- ============================================================================
-- AUDIT LOGS
-- ============================================================================

ALTER TABLE audit_logs
ADD COLUMN request_id UUID;

CREATE INDEX IF NOT EXISTS idx_audit_logs_request_id
ON audit_logs(request_id);

COMMIT;