import { request } from "./http";

export function fetchCatArchives() {
  return request("/cats");
}

export function fetchCatArchiveDetail(catId) {
  return request(`/cats/${catId}`);
}
