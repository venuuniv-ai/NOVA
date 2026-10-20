"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";

type Draft = {
  id: string; task_id: string; state: string; error: string | null;
  content: string | null; expires_at: string; proposal_id: string | null;
  verification: string; simulation: boolean; execution_enabled: boolean;
  evidence: { id: string; text: string; origin: string; binding: string }[];
};

export default function OwnedDraftWorkspace({ taskId, disabled, canMutate, isCurrentTask }: {
  taskId: string; disabled: boolean; canMutate: () => boolean; isCurrentTask: () => boolean;
}) {
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [query, setQuery] = useState("");
  const [memoryId, setMemoryId] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const alive = useRef(false);
  const posting = useRef(false);
  const intent = useRef<{ signature: string; key: string } | null>(null);
  const current = useRef(isCurrentTask);
  useEffect(() => { current.current = isCurrentTask; }, [isCurrentTask]);
  const load = useCallback(async (signal?: AbortSignal) => {
    try {
      const rows = await api<Draft[]>(`/tasks/${taskId}/drafts`, { signal });
      if (alive.current && current.current() && !signal?.aborted) {
        if (rows.some(row => row.task_id !== taskId)) throw new Error("Draft task identity mismatch.");
        setDrafts(rows);
      }
    } catch (cause) {
      if (alive.current && !signal?.aborted) setError(cause instanceof Error ? cause.message : "Unable to load drafts.");
    }
  }, [taskId]);
  useEffect(() => {
    alive.current = true;
    const controller = new AbortController();
    const initial = setTimeout(() => void load(controller.signal), 0);
    const interval = setInterval(() => { if (!document.hidden) void load(controller.signal); }, 5000);
    return () => { alive.current = false; controller.abort(); clearTimeout(initial); clearInterval(interval); };
  }, [load]);

  async function send(path: string, body: object) {
    if (posting.current || disabled || !canMutate()) return;
    posting.current = true; setBusy(true); setError("");
    try {
      await api(path, { method: "POST", body: JSON.stringify(body) });
      if (alive.current && current.current()) await load();
    } catch (cause) {
      if (alive.current && current.current()) setError(cause instanceof Error ? cause.message : "Draft request failed.");
    } finally { posting.current = false; if (alive.current) setBusy(false); }
  }

  async function prepare() {
    const signature = JSON.stringify({ taskId, query, memoryId });
    if (intent.current?.signature !== signature) intent.current = { signature, key: crypto.randomUUID() };
    const key = intent.current.key;
    // Keep the original key until acknowledgment, including a lost HTTP response.
    if (posting.current || disabled || !canMutate()) return;
    posting.current = true; setBusy(true); setError("");
    try {
      await api("/proactive/drafts", { method: "POST", body: JSON.stringify({
        task_id: taskId, query, memory_ids: memoryId.trim() ? [memoryId.trim()] : [], idempotency_key: key,
      }) });
      intent.current = null;
      if (alive.current && current.current()) await load();
    } catch (cause) {
      if (alive.current && current.current()) setError(cause instanceof Error ? cause.message : "Draft request failed.");
    } finally { posting.current = false; if (alive.current) setBusy(false); }
  }

  return <section className="panel" aria-label="Owned evidence drafts">
    <h3>Owned evidence drafts</h3>
    <p>Prepare a preference recommendation from an eligible memory. Fixture generation is the default; no action will execute.</p>
    <form onSubmit={event => { event.preventDefault(); void prepare(); }}>
      <label>Preference question<input aria-label="Preference question" required maxLength={200} value={query} onChange={event => setQuery(event.target.value)} placeholder="Which cuisine does named_subject prefer?" /></label>
      <label>Supporting memory UUID (optional)<input aria-label="Supporting memory UUID" value={memoryId} onChange={event => setMemoryId(event.target.value)} /></label>
      <p>Leave the UUID empty to find matching owned cuisine or beverage facts, or choose a memory from Memory Center. Each request opts into one bounded draft.</p>
      <button className="button primary" disabled={disabled || busy}>Prepare owned draft</button>
    </form>
    {error && <p role="alert">{error}</p>}
    <button className="button ghost" disabled={busy} onClick={() => void load()}>Refresh owned drafts</button>
    {drafts.map(draft => <article className="panel" key={draft.id} data-draft-id={draft.id}>
      <h4>Suggested recommendation · {draft.state}</h4>
      <p>{draft.simulation ? "FIXTURE" : "LOCAL_REAL"} · Approval required · Execution disabled</p>
      {draft.content && <blockquote>{draft.content}</blockquote>}
      {draft.error && <p role="status">{draft.error}</p>}
      <p>Verification: {draft.verification}</p>
      <p>Expires: {draft.expires_at}</p>
      {draft.evidence.map(item => <p key={item.id}><span className="mono">{item.id} · {item.origin}</span><br />{item.text}</p>)}
      {["QUEUED", "RUNNING", "PENDING_APPROVAL"].includes(draft.state) && <button className="button ghost" disabled={disabled || busy} onClick={() => void send(`/proactive/drafts/${draft.id}/cancel`, {})}>Cancel owned draft</button>}
      {draft.state === "PENDING_APPROVAL" && draft.proposal_id && <button className="button ghost" disabled={disabled || busy} onClick={() => void send(`/proposals/${draft.proposal_id}/reject`, { idempotency_key: crypto.randomUUID() })}>Reject owned draft</button>}
    </article>)}
  </section>;
}
