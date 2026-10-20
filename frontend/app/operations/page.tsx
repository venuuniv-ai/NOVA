"use client";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";

type Task = { id: string; title: string };
type Event = { id: string; sequence: number; type: string; state: string; attempts: number; consumers: string[] };
type Job = { id: string; sequence: number; state: string; attempts: number; result_id: string | null; diagnostic: string | null };
type Snapshot = {
  task_id: string; events: Event[]; jobs: Job[]; projection_sequence: number | null;
  page: { through: number; next_after: number | null; next_jobs_after: number | null };
};
function Inspector({ id }: { id: string }) {
  const [data, setData] = useState<Snapshot | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const active = useRef(true);
  const request = useRef<AbortController | null>(null);
  const locked = useRef(false);
  const load = useCallback(async (kind: "refresh" | "events" | "jobs", prior: Snapshot | null) => {
    if (locked.current) return;
    locked.current = true;
    request.current?.abort();
    const controller = new AbortController(); request.current = controller;
    setBusy(true); setError("");
    const params = new URLSearchParams({ limit: "20" });
    if (kind !== "refresh" && prior) {
      params.set("through", String(prior.page.through));
      if (kind === "events") params.set("after", String(prior.page.next_after));
      else params.set("jobs_after", String(prior.page.next_jobs_after));
    }
    try {
      const next = await api<Snapshot>(`/operations/tasks/${id}?${params}`, { signal: controller.signal });
      if (!active.current || controller.signal.aborted) return;
      if (next.task_id !== id) throw new Error("Task identity mismatch.");
      setData(previous => kind === "refresh" || !previous ? next : {
        ...previous,
        events: kind === "events" ? [...previous.events, ...next.events] : previous.events,
        jobs: kind === "jobs" ? [...previous.jobs, ...next.jobs] : previous.jobs,
        page: { ...previous.page, ...(kind === "events" ? { next_after: next.page.next_after } : { next_jobs_after: next.page.next_jobs_after }) },
      });
    } catch (cause) {
      if (active.current && !controller.signal.aborted) setError(cause instanceof Error ? cause.message : "Unable to load delivery records.");
    } finally {
      locked.current = false;
      if (active.current) setBusy(false);
    }
  }, [id]);
  useEffect(() => {
    active.current = true;
    const timer = setTimeout(() => void load("refresh", null), 0);
    return () => { active.current = false; clearTimeout(timer); request.current?.abort(); };
  }, [load]);
  async function subscribe() {
    if (locked.current) return;
    locked.current = true; setBusy(true); setError("");
    try {
      await api(`/operations/tasks/${id}/subscribe`, { method: "POST" });
      if (active.current) setNotice("Subscribed to fixture review. Human approval remains required.");
    } catch (cause) {
      if (active.current) setError(cause instanceof Error ? cause.message : "Subscription failed.");
    } finally { locked.current = false; if (active.current) setBusy(false); }
  }
  return <section className="panel" aria-label="Task delivery evidence">
    <h2>Task delivery evidence</h2><code>{id}</code>
    <p>Metadata only. Terminal job status does not establish a model failure cause. Prompts and source content are excluded.</p>
    <button className="button primary" disabled={busy} onClick={() => void subscribe()}>Enable fixture proactive review</button>
    <button className="button ghost" disabled={busy} onClick={() => void load("refresh", null)}>Refresh delivery records</button>
    {notice && <p role="status">{notice}</p>}
    {error && <p role="alert">{error}</p>}
    {busy && <p role="status">Loading delivery records…</p>}
    {data && <>
      <p>Projection sequence: {data.projection_sequence ?? "UNKNOWN"}. Snapshot through sequence {data.page.through}.</p>
      <h3>Events</h3>
      {!data.events.length && <p>No delivery events.</p>}
      {data.events.map(event => <article key={event.id} data-event-id={event.id}><p>{event.sequence} · {event.type} · {event.state} · attempts {event.attempts}</p><code>{event.id}</code><p>Consumers: {event.consumers.join(", ") || "None reported"}</p></article>)}
      {data.page.next_after !== null && <button className="button ghost" disabled={busy} onClick={() => void load("events", data)}>Load more events</button>}
      <h3>Jobs</h3>
      {!data.jobs.length && <p>No durable jobs.</p>}
      {data.jobs.map(job => <article key={job.id} data-job-id={job.id}><code>{job.id}</code><p>{job.state} · attempts {job.attempts}</p><p>Diagnostic: {job.diagnostic ?? "UNKNOWN"}</p><p>Result: {job.result_id ?? "None"}</p></article>)}
      {data.page.next_jobs_after !== null && <button className="button ghost" disabled={busy} onClick={() => void load("jobs", data)}>Load more jobs</button>}
    </>}
  </section>;
}
export default function Operations() {
  const [tasks, setTasks] = useState<Task[]>([]), [id, setId] = useState("");
  const [summary, setSummary] = useState<Record<string, unknown> | null>(null), [error, setError] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    void Promise.all([api<Task[]>("/tasks", { signal: controller.signal }), api<Record<string, unknown>>("/operations/events", { signal: controller.signal })])
      .then(([t, s]) => { if (!controller.signal.aborted) { setTasks(t); setSummary(s); } })
      .catch(cause => { if (!controller.signal.aborted) setError(cause.message); });
    return () => controller.abort();
  }, []);
  return <main className="evaluation-lab"><nav><Link href="/">Command Center</Link><Link href="/auth">Authentication</Link></nav>
    <h1>Local Operations</h1><p>Operator permission required. Delivery is at least once; transactional inboxes prevent duplicate effects. Owned drafts cannot execute actions.</p>
    {error && <p role="alert">{error}</p>}<pre>{summary ? JSON.stringify(summary, null, 2) : "Loading operational state…"}</pre>
    <label>Owned task<select aria-label="Operations task" value={id} onChange={event => setId(event.target.value)}><option value="">Select a task</option>{tasks.map(task => <option key={task.id} value={task.id}>{task.title} / {task.id}</option>)}</select></label>
    {id && <Inspector key={id} id={id} />}
  </main>;
}
