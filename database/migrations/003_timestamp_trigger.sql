-- ============================================================================
-- Module 3: Timestamp Trigger
-- PostgreSQL 17
-- ============================================================================

-- Generic trigger that updates the updated_at column automatically.
-- This trigger will be attached to tables as they are created.

CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;