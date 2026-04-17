import { request } from "./http";

export function fetchDiscoveryRecords() {
  return request("/sightings");
}
