import { LocalStorage, getPreferenceValues } from "@raycast/api";

export type Preferences = {
  baseUrl?: string;
  timeoutSec?: string;
  defaultUseTestUrl?: boolean;
  remotePresetsUrl?: string;
  apiKey?: string;
  apiKeyHeaderName?: string;
  externalConfigPath?: string;
};

export type ExternalConfig = {
  baseUrl?: string;
  apiKey?: string;
  apiKeyHeaderName?: string;
};

export type HistoryItem = {
  url: string;
  mode: "test" | "prod";
  payload?: string;
  headers?: string;
  status?: number;
  at: number;
};

async function loadExternalConfig(): Promise<ExternalConfig | null> {
  try {
    const prefs = getPreferenceValues<Preferences>();
    const p = prefs.externalConfigPath?.trim();
    if (!p) return null;
    // Raycast 環境では Node fetch で file:// は使えないため、HTTP でなければ中止
    if (/^https?:\/\//i.test(p)) {
      const res = await fetch(p);
      if (!res.ok) return null;
      return (await res.json()) as ExternalConfig;
    }
    return null;
  } catch {
    return null;
  }
}

export async function resolveConnection(): Promise<{ baseUrl: string; apiKey?: string; apiKeyHeaderName: string; timeoutMs: number }>{
  const prefs = getPreferenceValues<Preferences>();
  const ext = await loadExternalConfig();
  const baseUrl = (ext?.baseUrl || prefs.baseUrl || "http://localhost:5678").replace(/\/$/, "");
  const apiKey = ext?.apiKey || prefs.apiKey || undefined;
  const apiKeyHeaderName = (ext?.apiKeyHeaderName || prefs.apiKeyHeaderName || "X-API-Key").trim();
  const timeoutMs = Number(prefs.timeoutSec || "10") * 1000;
  return { baseUrl, apiKey, apiKeyHeaderName, timeoutMs };
}

export function normalizeUrl(input: string, baseUrl: string, useTest: boolean): string {
  const trimmed = input.trim();
  const isFull = /^https?:\/\//i.test(trimmed);
  if (isFull) return trimmed;
  const path = trimmed.replace(/^\/+/, "");
  const suffix = useTest ? "/webhook-test/" : "/webhook/";
  const base = baseUrl.replace(/\/$/, "");
  return `${base}${suffix}${path}`;
}

export function withApiKeyHeaders(raw?: Record<string, string>): Record<string, string> | undefined {
  const prefs = getPreferenceValues<Preferences>();
  const apiKey = prefs.apiKey?.trim();
  if (!apiKey) return raw;
  const headerName = (prefs.apiKeyHeaderName || "X-API-Key").trim();
  return { ...(raw || {}), [headerName]: apiKey };
}

export async function postJson(url: string, body: string | undefined, headers: Record<string, string> | undefined, timeoutMs: number, override?: { apiKey?: string; apiKeyHeaderName?: string }): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const preferences = getPreferenceValues<Preferences>();
    const apiKey = override?.apiKey ?? preferences.apiKey?.trim();
    const headerName = (override?.apiKeyHeaderName ?? preferences.apiKeyHeaderName ?? "X-API-Key").trim();
    const mergedHeaders = apiKey ? { ...(headers || {}), [headerName]: apiKey } : headers;
    const res = await fetch(url, {
      method: "POST",
      headers: mergedHeaders,
      body: body || undefined,
      signal: controller.signal,
    });
    return res;
  } finally {
    clearTimeout(id);
  }
}

const HISTORY_KEY = "raycast-n8n-history";

export async function loadHistory(): Promise<HistoryItem[]> {
  const raw = await LocalStorage.getItem<string>(HISTORY_KEY);
  if (!raw) return [];
  try {
    const arr = JSON.parse(raw) as HistoryItem[];
    if (!Array.isArray(arr)) return [];
    return arr;
  } catch {
    return [];
  }
}

export async function saveHistoryItem(item: HistoryItem): Promise<void> {
  const arr = await loadHistory();
  const merged = [item, ...arr].slice(0, 50);
  await LocalStorage.setItem(HISTORY_KEY, JSON.stringify(merged));
}
