Module 1 — Extensions

-- ============================================================================
-- Module 1: Extensions
-- Restaurant Knowledge OS
-- PostgreSQL 17
--
-- Purpose:
--   Enable database extensions required by later Phase 1 modules.
--   This module is intentionally minimal and safe to run once per database.
-- ============================================================================

-- UUID generation for primary keys and public identifiers.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Case-insensitive text, useful for unique email storage and login lookups.
CREATE EXTENSION IF NOT EXISTS citext;
