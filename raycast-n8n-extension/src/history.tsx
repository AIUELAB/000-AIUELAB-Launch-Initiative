import { Action, ActionPanel, Detail, List, Toast, getPreferenceValues, showToast, useNavigation } from "@raycast/api";
import { useEffect, useState } from "react";
import { HistoryItem, Preferences, loadHistory, postJson, saveHistoryItem } from "./lib";

export default function Command() {
  const prefs = getPreferenceValues<Preferences>();
  const [items, setItems] = useState<HistoryItem[]>([]);
  const { push } = useNavigation();

  useEffect(() => {
    (async () => setItems(await loadHistory()))();
  }, []);

  async function rerun(item: HistoryItem) {
    const timeoutSec = Number(prefs.timeoutSec || "10");
    await showToast({ style: Toast.Style.Animated, title: "Re-running..." });
    try {
      const res = await postJson(item.url, item.payload, item.headers ? JSON.parse(item.headers) : undefined, timeoutSec * 1000);
      const text = await res.text();
      const short = text.length > 5000 ? text.slice(0, 5000) + "\n…(truncated)" : text;
      push(<Detail markdown={`**URL**: ${item.url}\n\n**Status**: ${res.status}\n\n\n\n\n**Response**:\n\n\n\n${"```"}\n${short}\n${"```"}`} />);
      await saveHistoryItem({ ...item, status: res.status, at: Date.now() });
    } catch (e: any) {
      await showToast({ style: Toast.Style.Failure, title: "Request error", message: String(e?.message || e) });
    }
  }

  return (
    <List searchBarPlaceholder="Filter by URL...">
      {items.map((it, idx) => (
        <List.Item
          key={`${it.at}-${idx}`}
          title={it.url}
          accessories={[{ tag: it.mode }, { date: new Date(it.at) }]}
          actions={
            <ActionPanel>
              <Action title="Re-run" onAction={() => rerun(it)} />
              <Action.CopyToClipboard title="Copy URL" content={it.url} />
              {it.payload && <Action.CopyToClipboard title="Copy Payload" content={it.payload} />}
            </ActionPanel>
          }
        />
      ))}
    </List>
  );
}
