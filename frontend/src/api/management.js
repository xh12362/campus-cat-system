import { getMockManagementSummary } from "./mock";
import { isMockEnabled, request } from "./http";

export function fetchManagementSummary() {
  if (isMockEnabled()) {
    return getMockManagementSummary();
  }

  return request("/management/summary");
}
