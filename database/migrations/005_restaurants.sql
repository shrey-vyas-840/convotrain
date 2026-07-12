-- ============================================================================
-- Module 5: Restaurants
-- PostgreSQL 17
-- ============================================================================

CREATE TABLE restaurants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    owner_id UUID NOT NULL,

    name VARCHAR(200) NOT NULL,

    cuisine_type VARCHAR(100),

    language_preferences JSONB NOT NULL DEFAULT '["en"]'::jsonb,

    timezone VARCHAR(100) NOT NULL DEFAULT 'UTC',

    location TEXT,

    phone_number VARCHAR(20),

    status VARCHAR(20) NOT NULL DEFAULT 'active',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    deleted_at TIMESTAMPTZ,

    CONSTRAINT fk_restaurants_owner
        FOREIGN KEY (owner_id)
        REFERENCES users(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_restaurant_status
        CHECK (status IN ('active', 'inactive', 'suspended'))
);

-- Indexes
CREATE INDEX idx_restaurants_owner
ON restaurants(owner_id);

CREATE INDEX idx_restaurants_status
ON restaurants(status);

-- Automatically update updated_at
CREATE TRIGGER trg_restaurants_updated_at
BEFORE UPDATE
ON restaurants
FOR EACH ROW
EXECUTE FUNCTION trigger_set_updated_at();

COMMENT ON TABLE restaurants IS
'Each record represents one tenant (restaurant).';