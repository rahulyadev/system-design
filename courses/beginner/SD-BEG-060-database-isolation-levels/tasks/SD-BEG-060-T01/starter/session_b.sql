\set ON_ERROR_STOP on
\set VERBOSITY verbose

-- Complete the writer side for the current schedule.
-- State before running whether this transaction will COMMIT, ROLLBACK, or remain open.

BEGIN ISOLATION LEVEL /* TODO */;

-- TODO: update only id = 1 in sd_beg_060_t01.users.
-- TODO: COMMIT, ROLLBACK, or wait as required by the schedule.
