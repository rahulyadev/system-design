\set ON_ERROR_STOP on

DO $guard$
BEGIN
  IF current_database() <> 'sd_learning' OR current_user <> 'sd_learner' THEN
    RAISE EXCEPTION
      'Refusing reference setup: expected database sd_learning and user sd_learner, got % and %',
      current_database(), current_user;
  END IF;
END
$guard$;

DROP SCHEMA IF EXISTS sd_beg_060_t01 CASCADE;
CREATE SCHEMA sd_beg_060_t01 AUTHORIZATION sd_learner;

CREATE TABLE sd_beg_060_t01.users (
  id integer PRIMARY KEY,
  name text NOT NULL
);

INSERT INTO sd_beg_060_t01.users(id, name) VALUES (1, 'A');

SELECT count(*) AS reference_rows,
       min(name) AS reference_initial_name
FROM sd_beg_060_t01.users;
