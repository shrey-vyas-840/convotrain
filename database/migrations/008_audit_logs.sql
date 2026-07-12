-- ============================================================================
-- Module 8: Audit Logs
-- PostgreSQL 17
-- ============================================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    restaurant_id UUID NOT NULL,

    actor_id UUID,

    action VARCHAR(100) NOT NULL,

    entity_type VARCHAR(100) NOT NULL,

    entity_id UUID,

    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_audit_logs_restaurant
        FOREIGN KEY (restaurant_id)
        REFERENCES restaurants(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_audit_logs_actor
        FOREIGN KEY (actor_id)
        REFERENCES users(id)
        ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_audit_logs_restaurant
ON audit_logs (restaurant_id);

CREATE INDEX idx_audit_logs_actor
ON audit_logs (actor_id);

CREATE INDEX idx_audit_logs_action
ON audit_logs (action);

CREATE INDEX idx_audit_logs_entity
ON audit_logs (entity_type, entity_id);

CREATE INDEX idx_audit_logs_created_at
ON audit_logs (created_at DESC);

COMMENT ON TABLE audit_logs IS
'Immutable audit trail for tenant activities.';