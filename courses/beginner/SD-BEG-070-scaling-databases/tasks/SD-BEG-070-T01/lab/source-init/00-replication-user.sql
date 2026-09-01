CREATE USER IF NOT EXISTS 'replicator'@'%'
  IDENTIFIED WITH caching_sha2_password BY 'sd_beg_070_t01_repl_local';
GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'%';
FLUSH PRIVILEGES;
