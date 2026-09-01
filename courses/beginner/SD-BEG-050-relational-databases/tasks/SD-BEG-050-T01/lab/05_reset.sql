\set ON_ERROR_STOP on

SELECT CASE
         WHEN current_database() = 'sd_beg_050_t01' THEN 'true'
         ELSE 'false'
       END AS safe_database \gset

\if :safe_database
  \echo 'RESET_TARGET database=sd_beg_050_t01 schema=sd_beg_050_t01'
  DROP SCHEMA IF EXISTS sd_beg_050_t01 CASCADE;
\else
  \echo 'REFUSING_RESET expected database sd_beg_050_t01'
  \quit 3
\endif
