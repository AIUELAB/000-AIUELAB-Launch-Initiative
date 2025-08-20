export type Preset = {
  id: string;            // unique id
  title: string;         // display name
  path: string;          // webhook path (without prefix)
  description?: string;  // optional description
  defaultPayload?: string; // JSON string
  headers?: string;        // JSON string
};

// プロジェクトごとに編集してください（例）
export const PRESETS: Preset[] = [
  {
    id: "raycast-cli",
    title: "Raycast CLI Trigger",
    path: "raycast-cli",
    description: "Run workflow for Raycast demo",
    defaultPayload: '{"source":"raycast","ts": "{{now}}"}'
  },
  {
    id: "daily-report",
    title: "Daily Report",
    path: "daily-report",
    description: "Generate daily report",
  }
];
