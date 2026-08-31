\set ON_ERROR_STOP on

DO $$
BEGIN
    IF current_database() <> 'sd_learning' THEN
        RAISE EXCEPTION 'Refusing reset in database %', current_database();
    END IF;
END
$$;

DROP SCHEMA IF EXISTS sd_beg_050_t01 CASCADE;
