\set ON_ERROR_STOP on

DO $guard$
BEGIN
  IF current_database() <> 'sd_learning' OR current_user <> 'sd_learner' THEN
    RAISE EXCEPTION
      'Refusing reset: expected database sd_learning and user sd_learner, got % and %',
      current_database(), current_user;
  END IF;
END
$guard$;

SELECT current_database() AS reset_database,
       current_user AS reset_user,
       'sd_beg_060_t01' AS reset_schema;

DROP SCHEMA IF EXISTS sd_beg_060_t01 CASCADE;

SELECT to_regnamespace('sd_beg_060_t01') IS NULL AS exact_schema_removed;
