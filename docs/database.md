# Database Documentation

## Database

- Database name: `campus_cat`
- Engine: MySQL 8
- Character set: `utf8mb4`

## Tables

### user

Stores simple uploader or operator information. First version does not implement a complex auth system.

| Field | Type | Null | Description |
| --- | --- | --- | --- |
| `id` | BIGINT | no | Primary key |
| `username` | VARCHAR(50) | no | Unique username |
| `display_name` | VARCHAR(100) | yes | Display name |
| `email` | VARCHAR(100) | yes | Unique email |
| `created_at` | DATETIME | no | Record creation time |

### cat_profile

Stores the main archive for one campus cat.

| Field | Type | Null | Description |
| --- | --- | --- | --- |
| `id` | BIGINT | no | Primary key |
| `name` | VARCHAR(100) | yes | Cat archive name. Auto-created uploads use `Cat-0001` style naming. |
| `gender` | VARCHAR(20) | yes | Gender label |
| `coat_color` | VARCHAR(100) | yes | Coat color |
| `age_stage` | VARCHAR(30) | yes | Age stage such as kitten/adult |
| `sterilization_status` | VARCHAR(30) | yes | Sterilization status |
| `health_status` | VARCHAR(100) | yes | Health summary |
| `distinguishing_features` | TEXT | yes | Key visible features |
| `first_seen_at` | DATETIME | yes | First known sighting time |
| `first_seen_location` | VARCHAR(255) | yes | First known sighting location |
| `notes` | TEXT | yes | General notes |
| `created_by` | BIGINT | yes | User id of creator |
| `created_at` | DATETIME | no | Record creation time |
| `updated_at` | DATETIME | no | Last update time |

### cat_image

Stores uploaded original images and AI-related paths.

| Field | Type | Null | Description |
| --- | --- | --- | --- |
| `id` | BIGINT | no | Primary key |
| `cat_profile_id` | BIGINT | yes | Related cat profile id |
| `file_path` | VARCHAR(255) | no | Original image path under `uploads/original/` |
| `original_filename` | VARCHAR(255) | yes | Source filename from upload |
| `mime_type` | VARCHAR(100) | yes | Uploaded content type |
| `file_size` | INT | yes | File size in bytes |
| `ai_feature_path` | VARCHAR(255) | yes | Cropped image path or future AI feature file path |
| `ai_match_status` | VARCHAR(30) | no | Current AI result status such as `detected` or `pending` |
| `notes` | TEXT | yes | Notes copied from upload |
| `uploaded_by` | BIGINT | yes | User id of uploader |
| `created_at` | DATETIME | no | Record creation time |

### cat_sighting

Stores one discovery event.

| Field | Type | Null | Description |
| --- | --- | --- | --- |
| `id` | BIGINT | no | Primary key |
| `cat_profile_id` | BIGINT | yes | Related cat profile id |
| `image_id` | BIGINT | yes | Related uploaded image id |
| `sighted_at` | DATETIME | no | Time when the cat was seen |
| `location_text` | VARCHAR(255) | no | Human-readable location |
| `notes` | TEXT | yes | Discovery notes |
| `reported_by` | BIGINT | yes | User id of reporter |
| `created_at` | DATETIME | no | Record creation time |

## Relationships

- `cat_profile.id` -> `cat_image.cat_profile_id`
- `cat_profile.id` -> `cat_sighting.cat_profile_id`
- `cat_image.id` -> `cat_sighting.image_id`
- `user.id` -> `cat_profile.created_by`
- `user.id` -> `cat_image.uploaded_by`
- `user.id` -> `cat_sighting.reported_by`

## Upload-to-Archive Flow

### Case 1: Upload with `cat_profile_id`

If the client already knows the correct archive id:

1. Save original image to `uploads/original/`
2. Call AI detection and keep the existing detection response format
3. Create `cat_image` bound to the given `cat_profile_id`
4. Create `cat_sighting` bound to the same `cat_profile_id`

### Case 2: Upload without `cat_profile_id`

If the client does not confirm an existing cat archive:

1. Save original image to `uploads/original/`
2. Call AI detection
3. Auto-create a new `cat_profile`
4. Use auto name format `Cat-0001`, `Cat-0002`, ...
5. Fill `first_seen_at`, `first_seen_location`, and `notes` from upload data
6. Create `cat_image` pointing to the new profile
7. Create `cat_sighting` pointing to the new profile

This first version intentionally does not implement a complex matching strategy. `recommendations` remains a placeholder suggestion list and does not block auto profile creation.
