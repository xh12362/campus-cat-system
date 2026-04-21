import { request } from "./http";

export function submitCatUpload(payload) {
  const formData = new FormData();
  formData.append("photo", payload.photo);
  formData.append("location_text", payload.locationText);

  if (payload.sightedAt) {
    formData.append("sighted_at", payload.sightedAt);
  }

  if (payload.notes) {
    formData.append("notes", payload.notes);
  }

  if (payload.catProfileId) {
    formData.append("cat_profile_id", String(payload.catProfileId));
  }

  if (payload.uploadedBy) {
    formData.append("uploaded_by", String(payload.uploadedBy));
  }

  return request("/upload", {
    method: "POST",
    body: formData,
  });
}

export function createProfileFromUpload(payload) {
  return request("/upload/create-profile", {
    method: "POST",
    body: JSON.stringify({
      image_id: payload.imageId,
      sighting_id: payload.sightingId,
    }),
  });
}
