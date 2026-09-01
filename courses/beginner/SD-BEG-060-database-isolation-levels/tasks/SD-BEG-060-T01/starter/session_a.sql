\set ON_ERROR_STOP on
\set VERBOSITY verbose

-- Complete one schedule at a time. Reset the task schema between schedules.
-- Set the transaction isolation before the first data statement.

BEGIN ISOLATION LEVEL /* TODO */;
SHOW transaction_isolation;

-- TODO: first read of sd_beg_060_t01.users where id = 1.
-- Pause here and execute the required Session B step.
-- TODO: second read or locking-read variation.

-- TODO: COMMIT or ROLLBACK intentionally and record the outcome.
