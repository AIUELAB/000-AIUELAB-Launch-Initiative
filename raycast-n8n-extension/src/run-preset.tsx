import { Action, ActionPanel, Detail, List, Toast, getPreferenceValues, showHUD, showToast, useNavigation } from "@raycast/api";
import { useEffect, useMemo, useState } from "react";
import { Preferences, postJson, saveHistoryItem } from "./lib";
import { PRESETS, Preset, RemotePresets, mergeRemotePresets } from "./presets";

export default function Command() {
  const prefs = getPreferenceValues<Preferences & { remotePresetsUrl?: string }>();
  const [query, setQuery] = useState("");
  const [useTest, setUseTest] = useState<boolean>(false); // 既定は /webhook
  const [data, setData] = useState<Preset[]>(PRESETS);
  const { push } = useNavigation();

  useEffect(() => {
    (async () => {
      const url = prefs.remotePresetsUrl?.trim();
      if (!url) {
        setData(PRESETS);
        return;
      }
      try {
        const res = await fetch(url, { method: "GET" });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = (await res.json()) as RemotePresets;
        setData(mergeRemotePresets(PRESETS, json));
      } catch (e: any) {
        await showToast({ style: Toast.Style.Failure, title: "Failed to fetch presets", message: String(e?.message || e) });
        setData(PRESETS);
      }
    })();
  }, []);

  const list = useMemo(() => data.filter(p => (p.title?.toLowerCase().includes(query.toLowerCase()) || p.path.includes(query))), [data, query]);

  async function run(preset: Preset) {
    const baseUrl = (getPreferenceValues<{ baseUrl?: string }>().baseUrl || "http://localhost:5678").replace(/\/$/, "");
    const timeoutSec = Number((getPreferenceValues<{ timeoutSec?: string }>().timeoutSec || "10"));
    const url = `${baseUrl}${useTest ? "/webhook-test/" : "/webhook/"}${preset.path}`;
    const payload = preset.defaultPayload || "";
    const headers = preset.headers ? JSON.parse(preset.headers) : undefined;

    await showToast({ style: Toast.Style.Animated, title: "Triggering preset...", message: preset.title });
    try {
      const res = await postJson(url, payload || undefined, headers, timeoutSec * 1000);
      const text = await res.text();
      const short = text.length > 5000 ? text.slice(0, 5000) + "\n…(truncated)" : text;
      if (res.ok) {
        await showHUD("✅ n8n triggered");
        push(<Detail markdown={`**Preset**: ${preset.title}\n\n**URL**: ${url}\n\n**Status**: ${res.status}\n\n\n\n\n**Response**:\n\n\n\n${"```"}\n${short}\n${"```"}`} />);
      } else {
        await showToast({ style: Toast.Style.Failure, title: `Failed: ${res.status}`, message: url });
        push(<Detail markdown={`**Preset**: ${preset.title}\n\n**URL**: ${url}\n\n**Status**: ${res.status}\n\n\n\n\n**Response**:\n\n\n\n${"```"}\n${short}\n${"```"}`} />);
      }
      await saveHistoryItem({ url, mode: useTest ? "test" : "prod", payload, headers: preset.headers, status: res.status, at: Date.now() });
    } catch (e: any) {
      await showToast({ style: Toast.Style.Failure, title: "Request error", message: String(e?.message || e) });
    }
  }

  return (
    <List
      searchBarPlaceholder="Search presets..."
      onSearchTextChange={setQuery}
      searchText={query}
      actions={
        <ActionPanel>
          <Action
            title={useTest ? "Use Production (/webhook)" : "Use Test (/webhook-test)"}
            onAction={() => setUseTest((v) => !v)}
            shortcut={{ modifiers: ["shift"], key: "m" }}
          />
        </ActionPanel>
      }
    >
      {list.map((p) => (
        <List.Item
          key={p.id}
          title={`${p.icon ? p.icon + " " : ""}${p.title}`}
          subtitle={p.path}
          accessories={[{ tag: useTest ? "test" : "prod" }, ...(p.category ? [{ tag: p.category }] : [])]}
          keywords={[p.path]}
          actions={
            <ActionPanel>
              <Action title="Run Preset" onAction={() => run(p)} shortcut={{ modifiers: ["cmd"], key: "enter" }} />
              <Action.CopyToClipboard title="Copy Path" content={p.path} />
            </ActionPanel>
          }
        />
      ))}
    </List>
  );
}
