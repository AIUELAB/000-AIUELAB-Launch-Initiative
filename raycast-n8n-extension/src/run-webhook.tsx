import { Action, ActionPanel, Detail, Form, Toast, getPreferenceValues, showHUD, showToast, useNavigation } from "@raycast/api";
import { useState } from "react";
import { Preferences, normalizeUrl, postJson, saveHistoryItem } from "./lib";

type RequestParts = {
  body?: string;
  headers?: Record<string, string>;
};

function tryParseJsonObject(text: string, what: string): Record<string, string> {
  try {
    const parsed = JSON.parse(text);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      return parsed as Record<string, string>;
    }
    throw new Error(`${what} must be a JSON object`);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`${what} invalid: ${message}`);
  }
}

function buildRequestParts(payloadText: string, headersText: string): RequestParts {
  const parts: RequestParts = {};
  const hasPayload = payloadText.trim().length > 0;
  const hasHeaders = headersText.trim().length > 0;

  if (hasPayload) {
    // Validate payload JSON but keep original string body
    tryParseJsonObject(`{"_": null, "__payload_validation_only__": null}`.replace("{\"_\": null, \"__payload_validation_only__\": null}", payloadText), "Payload");
    parts.body = payloadText;
  }

  if (hasHeaders) {
    parts.headers = tryParseJsonObject(headersText, "Headers");
  }

  if (parts.body && (!parts.headers || !parts.headers["Content-Type"])) {
    parts.headers = { ...(parts.headers || {}), "Content-Type": "application/json" };
  }

  return parts;
}

export default function Command() {
  const prefs = getPreferenceValues<Preferences>();
  const [urlOrPath, setUrlOrPath] = useState("");
  const [payload, setPayload] = useState("");
  // defaultUseTestUrl が true でも、要件により prod(/webhook) を既定化
  const [useTest, setUseTest] = useState<boolean>(false);
  const [headers, setHeaders] = useState<string>("");
  const { push } = useNavigation();

  const onSubmit = async () => {
    const baseUrl = prefs.baseUrl || "http://localhost:5678";
    const timeoutSec = Number(prefs.timeoutSec || "10");
    const url = normalizeUrl(urlOrPath, baseUrl, useTest);

    await showToast({ style: Toast.Style.Animated, title: "Triggering n8n...", message: url });

    let parts: RequestParts;
    try {
      parts = buildRequestParts(payload, headers);
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      await showToast({ style: Toast.Style.Failure, title: "Invalid input", message });
      return;
    }

    try {
      const res = await postJson(url, parts.body, parts.headers, timeoutSec * 1000);
      const text = await res.text();
      const short = text.length > 5000 ? text.slice(0, 5000) + "\n…(truncated)" : text;
      if (res.ok) {
        await showHUD("✅ n8n triggered");
        push(<Detail markdown={`**URL**: ${url}\n\n**Status**: ${res.status}\n\n\n\n\n**Response**:\n\n\n\n${"```"}\n${short}\n${"```"}`} />);
        await saveHistoryItem({ url, mode: useTest ? "test" : "prod", payload: parts.body, headers, status: res.status, at: Date.now() });
      } else {
        await showToast({ style: Toast.Style.Failure, title: `Failed: ${res.status}`, message: url });
        push(<Detail markdown={`**URL**: ${url}\n\n**Status**: ${res.status}\n\n\n\n\n**Response**:\n\n\n\n${"```"}\n${short}\n${"```"}`} />);
        await saveHistoryItem({ url, mode: useTest ? "test" : "prod", payload: parts.body, headers, status: res.status, at: Date.now() });
      }
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      await showToast({ style: Toast.Style.Failure, title: "Request error", message });
    }
  };

  return (
    <Form
      actions={
        <ActionPanel>
          <Action.SubmitForm title="Run Webhook" onSubmit={onSubmit} shortcut={{ modifiers: ["cmd"], key: "enter" }} />
          <Action
            title="Use Production (/webhook)"
            onAction={() => setUseTest(false)}
            shortcut={{ modifiers: ["shift"], key: "p" }}
          />
          <Action
            title="Use Test (/webhook-test)"
            onAction={() => setUseTest(true)}
            shortcut={{ modifiers: ["shift"], key: "t" }}
          />
        </ActionPanel>
      }
    >
      <Form.Description title="Mode" text={useTest ? "/webhook-test" : "/webhook"} />
      <Form.TextField id="urlOrPath" title="URL or Path" placeholder="Full URL or path (e.g. raycast-cli)" value={urlOrPath} onChange={setUrlOrPath} />
      <Form.TextArea id="payload" title="JSON Payload (optional)" placeholder='{"key":"value"}' value={payload} onChange={setPayload} />
      <Form.TextArea id="headers" title="Headers (JSON, optional)" placeholder='{"X-Token":"abc123"}' value={headers} onChange={setHeaders} />
    </Form>
  );
}
