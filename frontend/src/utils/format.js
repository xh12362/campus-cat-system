export function formatDateTime(value) {
  if (!value) {
    return "--";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export function formatText(value, fallback = "--") {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }

  return value;
}

export function formatScore(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "--";
  }

  return `${(Number(value) * 100).toFixed(1)}%`;
}

export function formatPathTail(value) {
  if (!value) {
    return "--";
  }

  const normalized = value.replaceAll("\\", "/");
  return normalized.split("/").filter(Boolean).slice(-3).join("/");
}

export function detectionSummary(detection) {
  if (!detection) {
    return "未返回检测结果";
  }

  if (!detection.model_loaded) {
    return detection.message || "检测服务未加载";
  }

  return detection.has_cat ? "检测到猫" : "未检测到猫";
}
