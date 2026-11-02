const API_BASE = "http://127.0.0.1:8000/api";

export interface SystemStatus {
  has_key: boolean;
  model: string;
  preferred_models: string[];
  privacy: string;
  disclaimer: string;
}

export interface ValidationMetrics {
  width: number;
  height: number;
  hand_fraction: number;
  segmentation: string;
  edge_width_px: number;
  texture: number;
  brightness: number;
  clipped: number;
}

export interface PalmSlot {
  name: string;
  raw_b64: string;
  preview_url: string;
  ok: boolean;
  metrics?: ValidationMetrics;
  errors?: string[];
  warnings?: string[];
}

export interface LineFeature {
  name: string;
  status: "detected" | "uncertain" | "not_detected";
  confidence: number;
  relative_length?: number;
  curvature?: string;
  prominence?: string;
  start_region?: string;
  end_region?: string;
  crease_depth?: number;
}

export interface HandFeatureData {
  palm: {
    palm_shape: string;
    finger_length: string;
    palmistry_hand_type: string;
    palm_length_to_width: number;
    finger_to_palm_length: number;
    note: string;
  };
  lines: Record<string, LineFeature>;
  notes: string[];
}

export interface AnalysisResult {
  stages: {
    Left: Record<string, string>;
    Right: Record<string, string>;
  };
  annotated: {
    Left: string;
    Right: string;
  };
  features: {
    Left: HandFeatureData;
    Right: HandFeatureData;
  };
  metrics: {
    Left: ValidationMetrics;
    Right: ValidationMetrics;
  };
  comparisons: Array<{
    title: string;
    panels: string[];
    why: string;
  }>;
}

export interface ReadingResult {
  language: string;
  report: Record<string, string>;
  passages: Array<{ id: string; text: string }>;
  titles: Record<string, string>;
  disclaimer: string;
}

export async function fetchStatus(): Promise<SystemStatus> {
  const res = await fetch(`${API_BASE}/status`);
  if (!res.ok) throw new Error("Backend server unreachable");
  return res.json();
}

export async function fetchSample(pairName: string) {
  const res = await fetch(`${API_BASE}/sample/${pairName}`);
  if (!res.ok) throw new Error(`Could not load sample ${pairName}`);
  return res.json();
}

export async function validateUpload(side: string, file: File): Promise<any> {
  const fd = new FormData();
  fd.append("side", side);
  fd.append("file", file);
  const res = await fetch(`${API_BASE}/validate`, {
    method: "POST",
    body: fd,
  });
  if (!res.ok) throw new Error("Validation request failed");
  return res.json();
}

export async function runAnalysis(
  left: { name: string; raw_b64: string },
  right: { name: string; raw_b64: string }
): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: jsonStringify({
      left_name: left.name,
      left_b64: left.raw_b64,
      right_name: right.name,
      right_b64: right.raw_b64,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Image analysis pipeline failed");
  }
  return res.json();
}

export async function fetchReading(
  features: Record<string, HandFeatureData>,
  language: "en" | "si" | "ta"
): Promise<ReadingResult> {
  const res = await fetch(`${API_BASE}/generate-reading`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: jsonStringify({ features, language }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to generate reading");
  }
  return res.json();
}

export async function sendChat(
  query: string,
  features: any,
  report: any,
  language: "en" | "si" | "ta",
  history: Array<{ role: string; text: string }>
): Promise<{ reply: string }> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: jsonStringify({
      query,
      features,
      report,
      language,
      history,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Chat response failed");
  }
  return res.json();
}

function jsonStringify(obj: any) {
  return JSON.stringify(obj);
}
