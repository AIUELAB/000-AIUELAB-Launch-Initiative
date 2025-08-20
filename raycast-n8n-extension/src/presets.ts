export type Preset = {
  id: string;            // unique id
  title: string;         // display name
  path: string;          // webhook path (without prefix or with, both accepted)
  description?: string;  // optional description
  category?: string;     // category (task/notification/automation)
  icon?: string;         // optional icon
  defaultPayload?: string; // JSON string
  headers?: string;        // JSON string
  requiredFields?: string[];
  optionalFields?: string[];
};

export type RemotePresets = {
  version?: string;
  updated?: string;
  presets: Array<
    Omit<Preset, "defaultPayload" | "headers"> & {
      defaultPayload?: Record<string, unknown> | string;
      headers?: Record<string, string> | string;
    }
  >;
};

// 初期プリセット（ローカル定義）
export const PRESETS: Preset[] = [
  {
    id: "quick-test",
    title: "Quick Test",
    path: "/webhook/test",
    description: "動作確認用",
    category: "automation",
    icon: "⚡"
  }
];

export function normalizePreset(p: Preset): Preset {
  // 先頭スラッシュや /webhook[-test]/ を外してパス正規化（UI 側で prefix を付与）
  const path = p.path.replace(/^https?:\/\/[^/]+\//, "").replace(/^\/?(webhook|webhook-test)\//, "").replace(/^\//, "");
  return { ...p, path };
}

export function mergeRemotePresets(localPresets: Preset[], remote: RemotePresets | null): Preset[] {
  if (!remote || !Array.isArray(remote.presets)) return localPresets.map(normalizePreset);
  const normalizedRemote: Preset[] = remote.presets.map((r) => {
    let defaultPayloadStr: string | undefined;
    if (typeof r.defaultPayload === "string") {
      defaultPayloadStr = r.defaultPayload;
    } else if (r.defaultPayload) {
      defaultPayloadStr = JSON.stringify(r.defaultPayload);
    }

    let headersStr: string | undefined;
    if (typeof r.headers === "string") {
      headersStr = r.headers;
    } else if (r.headers) {
      headersStr = JSON.stringify(r.headers);
    }

    return normalizePreset({
      id: r.id || r.path,
      title: r.title || r.path,
      path: r.path,
      description: r.description,
      category: (r as any).category,
      icon: (r as any).icon,
      defaultPayload: defaultPayloadStr,
      headers: headersStr,
      requiredFields: (r as any).requiredFields,
      optionalFields: (r as any).optionalFields,
    });
  });
  // 重複は remote 優先で path/id で上書き
  const byId = new Map<string, Preset>();
  [...localPresets.map(normalizePreset), ...normalizedRemote].forEach((p) => {
    byId.set(p.id || p.path, p);
  });
  return Array.from(byId.values());
}
