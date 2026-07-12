-- ============================================================================
-- Module 6: Restaurant Members
-- PostgreSQL 17
-- ============================================================================

CREATE TABLE restaurant_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    restaurant_id UUID NOT NULL,

    user_id UUID NOT NULL,

    -- Role within this restaurant only.
    role VARCHAR(20) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_restaurant_members_restaurant
        FOREIGN KEY (restaurant_id)
        REFERENCES restaurants(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_restaurant_members_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_restaurant_member
        UNIQUE (restaurant_id, user_id),

    CONSTRAINT chk_restaurant_member_role
        CHECK (role IN ('owner', 'manager', 'staff'))
);

-- Indexes
CREATE INDEX idx_restaurant_members_restaurant
ON restaurant_members (restaurant_id);

CREATE INDEX idx_restaurant_members_user
ON restaurant_members (user_id);

CREATE INDEX idx_restaurant_members_role
ON restaurant_members (role);

-- Automatically maintain updated_at
CREATE TRIGGER trg_restaurant_members_updated_at
BEFORE UPDATE
ON restaurant_members
FOR EACH ROW
EXECUTE FUNCTION trigger_set_updated_at();

COMMENT ON TABLE restaurant_members IS
'Maps users to restaurants with restaurant-specific roles.';