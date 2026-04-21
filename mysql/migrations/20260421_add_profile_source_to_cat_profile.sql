USE campus_cat;

ALTER TABLE cat_profile
  ADD COLUMN IF NOT EXISTS profile_source VARCHAR(16) NOT NULL DEFAULT 'real' AFTER dataset_cat_code;

SET @profile_source_index_exists = (
  SELECT COUNT(*)
  FROM information_schema.STATISTICS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'cat_profile'
    AND INDEX_NAME = 'idx_cat_profile_profile_source'
);

SET @profile_source_index_sql = IF(
  @profile_source_index_exists = 0,
  'CREATE INDEX idx_cat_profile_profile_source ON cat_profile (profile_source)',
  'SELECT 1'
);

PREPARE stmt FROM @profile_source_index_sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
