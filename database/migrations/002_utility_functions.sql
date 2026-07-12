-- ============================================================================
-- Module 2: Utility Functions
-- PostgreSQL 17
-- ============================================================================

-- Updates the updated_at column before UPDATE operations.
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;