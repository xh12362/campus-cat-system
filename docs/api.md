# API Documentation

## Base Rules

- Base URL: `http://localhost:8000`
- API prefix: `/api`
- Content type:
  - `application/json` for regular create/query APIs
  - `multipart/form-data` for `/api/upload`

## POST /api/upload

Uploads one image, runs AI detection, stores image/sighting records, and may auto-create a cat profile.

### Request

- Method: `POST`
- Content type: `multipart/form-data`

### Form Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `photo` | file | yes | Original uploaded image. Saved to `uploads/original/`. |
| `location_text` | string | yes | Human-readable sighting location. |
| `sighted_at` | datetime | no | Sighting time in ISO 8601 format. If omitted, backend uses current UTC time. |
| `notes` | string | no | Notes for this upload and sighting. |
| `cat_profile_id` | integer | no | Existing cat profile id. If present, image and sighting bind to this profile. |
| `uploaded_by` | integer | no | User id for uploader/reporter. |

### Auto Profile Creation Rule

When `cat_profile_id` is not provided, the backend treats the upload as not yet confirmed to match an existing cat and automatically creates a new `cat_profile`.

- New profile name format: `Cat-0001`, `Cat-0002`, ...
- `cat_profile.first_seen_at` comes from `sighted_at` or current time
- `cat_profile.first_seen_location` comes from `location_text`
- `cat_profile.notes` comes from `notes`
- The created `cat_image` and `cat_sighting` both point to the new profile

### Response

```json
{
  "message": "Upload completed successfully.",
  "cat_profile_id": 12,
  "profile_created": true,
  "image": {
    "id": 35,
    "created_at": "2026-04-18T09:30:00",
    "cat_profile_id": 12,
    "file_path": "/workspace/uploads/original/example.jpg",
    "original_filename": "example.jpg",
    "mime_type": "image/jpeg",
    "file_size": 182736,
    "ai_feature_path": "/workspace/uploads/cropped/example_crop.jpg",
    "ai_match_status": "detected",
    "notes": "near canteen",
    "uploaded_by": null
  },
  "sighting": {
    "id": 48,
    "created_at": "2026-04-18T09:30:00",
    "cat_profile_id": 12,
    "image_id": 35,
    "sighted_at": "2026-04-18T09:29:50",
    "location_text": "North Gate",
    "notes": "near canteen",
    "reported_by": null
  },
  "recommendations": [
    {
      "cat_profile_id": 7,
      "cat_name": "Cat-0007",
      "similarity_score": null,
      "reason": "AI matching placeholder."
    }
  ],
  "detection": {
    "model_loaded": true,
    "has_cat": true,
    "confidence": 0.97,
    "detections": [
      {
        "label": "cat",
        "score": 0.97,
        "bbox": [15, 22, 188, 210]
      }
    ],
    "cropped_image_path": "/workspace/uploads/cropped/example_crop.jpg",
    "message": "Detection completed."
  }
}
```

### Response Fields

| Field | Type | Description |
| --- | --- | --- |
| `message` | string | Fixed success message. |
| `cat_profile_id` | integer | Final profile id used for this upload. |
| `profile_created` | boolean | `true` when backend auto-created a new profile. |
| `image` | object | Saved image record. |
| `sighting` | object | Saved sighting record. |
| `recommendations` | array | Current placeholder recommendation list. |
| `detection` | object | Existing AI detection result. This structure is kept unchanged for frontend compatibility. |

## GET /api/cats

Returns all cat profiles ordered by creation time descending.

### Response

```json
[
  {
    "id": 12,
    "created_at": "2026-04-18T09:30:00",
    "updated_at": "2026-04-18T09:30:00",
    "name": "Cat-0012",
    "gender": null,
    "coat_color": null,
    "age_stage": null,
    "sterilization_status": null,
    "health_status": null,
    "distinguishing_features": null,
    "first_seen_at": "2026-04-18T09:29:50",
    "first_seen_location": "North Gate",
    "notes": "near canteen",
    "created_by": null
  }
]
```

## GET /api/cats/{id}

Returns one cat profile with related images and sightings.

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `id` | integer | Cat profile id |

### Response Notes

- `images` contains all uploaded images for this cat
- `sightings` contains all discovery records for this cat
- Returns `404` if the profile does not exist

## POST /api/cats

Creates a cat profile manually.

### Request Body

```json
{
  "name": "Campus Tabby",
  "gender": "female",
  "coat_color": "brown tabby",
  "age_stage": "adult",
  "first_seen_location": "Library Gate",
  "notes": "friendly"
}
```

### Response

Returns the created profile in the same shape as `GET /api/cats/{id}`.

## GET /api/sightings

Returns all sighting records ordered by `sighted_at` descending.

### Response

```json
[
  {
    "id": 48,
    "created_at": "2026-04-18T09:30:00",
    "cat_profile_id": 12,
    "image_id": 35,
    "sighted_at": "2026-04-18T09:29:50",
    "location_text": "North Gate",
    "notes": "near canteen",
    "reported_by": null
  }
]
```
