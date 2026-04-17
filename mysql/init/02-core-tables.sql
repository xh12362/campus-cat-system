USE campus_cat;

CREATE TABLE IF NOT EXISTS `user` (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL UNIQUE,
  display_name VARCHAR(100) NULL,
  email VARCHAR(100) NULL UNIQUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS cat_profile (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NULL,
  gender VARCHAR(20) NULL,
  coat_color VARCHAR(100) NULL,
  age_stage VARCHAR(30) NULL,
  sterilization_status VARCHAR(30) NULL,
  health_status VARCHAR(100) NULL,
  distinguishing_features TEXT NULL,
  first_seen_at DATETIME NULL,
  first_seen_location VARCHAR(255) NULL,
  notes TEXT NULL,
  created_by BIGINT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_cat_profile_created_at (created_at),
  CONSTRAINT fk_cat_profile_created_by
    FOREIGN KEY (created_by) REFERENCES `user`(id)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS cat_image (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  cat_profile_id BIGINT NULL,
  file_path VARCHAR(255) NOT NULL,
  original_filename VARCHAR(255) NULL,
  mime_type VARCHAR(100) NULL,
  file_size INT NULL,
  ai_feature_path VARCHAR(255) NULL,
  ai_match_status VARCHAR(30) NOT NULL DEFAULT 'pending',
  notes TEXT NULL,
  uploaded_by BIGINT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_cat_image_cat_profile_id (cat_profile_id),
  INDEX idx_cat_image_created_at (created_at),
  CONSTRAINT fk_cat_image_profile
    FOREIGN KEY (cat_profile_id) REFERENCES cat_profile(id)
    ON DELETE SET NULL,
  CONSTRAINT fk_cat_image_uploaded_by
    FOREIGN KEY (uploaded_by) REFERENCES `user`(id)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS cat_sighting (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  cat_profile_id BIGINT NULL,
  image_id BIGINT NULL,
  sighted_at DATETIME NOT NULL,
  location_text VARCHAR(255) NOT NULL,
  notes TEXT NULL,
  reported_by BIGINT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_cat_sighting_cat_profile_id (cat_profile_id),
  INDEX idx_cat_sighting_image_id (image_id),
  INDEX idx_cat_sighting_sighted_at (sighted_at),
  CONSTRAINT fk_cat_sighting_profile
    FOREIGN KEY (cat_profile_id) REFERENCES cat_profile(id)
    ON DELETE SET NULL,
  CONSTRAINT fk_cat_sighting_image
    FOREIGN KEY (image_id) REFERENCES cat_image(id)
    ON DELETE SET NULL,
  CONSTRAINT fk_cat_sighting_reported_by
    FOREIGN KEY (reported_by) REFERENCES `user`(id)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
