"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { api, type Task } from "@/lib/api";

type Media = { id: string; task_id: string; device_id: string; sha256: string; width: number; height: number; source: string; metadata_removed: boolean };
type Observation = { id: string; label: string; description: string; processor: string; model: string; simulation: boolean; score: number | null; score_type: string; source: string; device: string; sha256: string; region: { x: number; y: number; width: number; height: number } | null; mask_reference: string | null };
type Perception = { simulation: boolean; id: string; task_id: string; media_id: string; trace_id: string; privacy_class: string; status: string; observations: Observation[]; processors: { processor: string; status: string; model: string; simulation: boolean; latency_ms: number | null }[]; context: { interpretation: string }[]; warnings: string[] };
type Intent = { media_id: string; idempotency_key: string; privacy_class: string };

export default function PerceptionWorkspace({ task, disabled, canMutate, compact = false }: { task: Task; disabled: boolean; canMutate: () => boolean; compact?: boolean }) {
  const [media, setMedia] = useState<Media[]>([]), [runs, setRuns] = useState<Perception[]>([]);
  const [ready, setReady] = useState(false), [busy, setBusy] = useState(false), [error, setError] = useState("");
  const [privacy, setPrivacy] = useState("PERSONAL"), [intent, setIntent] = useState<Intent | null>(null);
  const [notice, setNotice] = useState("");
  const alive = useRef(false), posting = useRef(false), version = useRef(0), reader = useRef<AbortController | null>(null), owner = useRef(canMutate);
  useEffect(() => { owner.current = canMutate; }, [canMutate]);
  const storage = `nova.perception-intent.${task.id}`;
  const load = useCallback(async () => {
    const generation = ++version.current; reader.current?.abort(); const controller = new AbortController(); reader.current = controller;
    try {
      const [images, results] = await Promise.all([api<Media[]>(`/tasks/${task.id}/media`, { signal: controller.signal }), api<Perception[]>(`/tasks/${task.id}/perception`, { signal: controller.signal })]);
      if (!alive.current || controller.signal.aborted || generation !== version.current) return;
      if (images.some(m => m.task_id !== task.id) || results.some(r => r.task_id !== task.id)) throw new Error("Visual context ownership mismatch.");
      setMedia(images); setRuns(results); setReady(true); setError("");
    } catch (cause) { if (alive.current && !controller.signal.aborted && generation === version.current) setError(cause instanceof Error ? cause.message : "Perception unavailable."); }
  }, [task.id]);
  useEffect(() => {
    alive.current = true; const lifecycle = alive, reads = reader, generations = version;
    const timer = setTimeout(() => { try { const value = localStorage.getItem(storage); if (value) setIntent(JSON.parse(value) as Intent); } catch { /* Optional request intent. */ } void load(); }, 0);
    const interval = setInterval(() => { if (!document.hidden) void load(); }, 5000);
    return () => { lifecycle.current = false; ++generations.current; reads.current?.abort(); clearTimeout(timer); clearInterval(interval); };
  }, [load, storage]);
  async function mutate(action: () => Promise<unknown>) {
    if (posting.current || disabled || !owner.current() || !alive.current) return;
    posting.current = true; setBusy(true); setNotice("");
    try { await action(); if (alive.current && owner.current()) await load(); }
    catch (cause) { if (alive.current && owner.current()) setError(cause instanceof Error ? cause.message : "Request failed."); }
    finally { posting.current = false; if (alive.current) setBusy(false); }
  }
  async function perceive() {
    const next = intent ?? { media_id: media[0].id, idempotency_key: crypto.randomUUID(), privacy_class: privacy };
    setIntent(next); try { localStorage.setItem(storage, JSON.stringify(next)); } catch { /* Optional intent. */ }
    const result = await api<Perception>(`/tasks/${task.id}/perception`, { method: "POST", body: JSON.stringify(next) });
    if (!alive.current || !owner.current()) return;
    if (result.task_id !== task.id) throw new Error("Perception ownership mismatch.");
    setIntent(null); try { localStorage.removeItem(storage); } catch { /* Optional intent. */ }
  }
  async function upload(file: File) {
    const response = await fetch(`/api/v1/tasks/${task.id}/media`, { method: "POST", headers: { "Content-Type": file.type, "Idempotency-Key": crypto.randomUUID(), "X-Correlation-ID": crypto.randomUUID() }, body: file });
    const result = await response.json(); if (!response.ok) throw new Error(result.error?.message ?? "Upload rejected.");
  }
  const image = media[0], run = runs.find(r => r.media_id === image?.id), blocked = disabled || busy || !ready;
  return <section className="panel perception-workspace" data-testid="perception-workspace" data-task-id={task.id}>
    <div className="panel-heading"><div><span className="eyebrow">VISUAL CONTEXT / EVIDENCE</span><h2>{compact ? "Visual context" : "Perception / Live Context"}</h2></div><span className="tag">{run ? run.status : "NO PERCEPTION YET"}</span></div>
    {error && <div className="error-notice" role="alert" aria-label="Perception error"><p>{error}</p><button className="button ghost" onClick={() => void load()}>Retry connection</button></div>}
    {!ready ? <p role="status">Loading persisted visual context…</p> : compact ? <div><p>{run ? `${run.observations.filter(o => o.processor === "FIXTURE_VISION").length} fixture observations · ${run.observations[0]?.device ?? "—"} · ${run.simulation ? "SIMULATED" : "MODEL / MIXED EVIDENCE"}` : "No visual evidence attached to this task."}</p><Link className="button ghost" href={`/perception?task=${task.id}`}>Open Perception</Link></div> : <>
      <p className="visual-disclosure">Visual evidence does not establish truth, grant tool permissions, approve actions or create permanent memory. Device contexts are simulated. REAL CLIP / DINOV2 / SAM / VLM NOT CONFIGURED by default.</p>
      <div className="perception-controls"><button className="button primary" disabled={blocked} onClick={() => void mutate(() => api(`/tasks/${task.id}/media/fixture`, { method: "POST", body: JSON.stringify({ idempotency_key: crypto.randomUUID() }) }))}>Attach wearable fixture</button><label className="button ghost">Upload image<input aria-label="Upload image" type="file" accept="image/jpeg,image/png,image/webp" disabled={blocked} onChange={event => { const file = event.target.files?.[0]; if (file) void mutate(() => upload(file)); event.target.value = ""; }} /></label><label>Privacy<select aria-label="Visual privacy" value={privacy} disabled={busy || !!intent} onChange={event => setPrivacy(event.target.value)}><option>PERSONAL</option><option>SENSITIVE_LOCAL_ONLY</option></select></label><button className="button primary" disabled={blocked || !media.length} onClick={() => void mutate(perceive)}>{busy ? "Awaiting response…" : intent ? "Retry original perception" : "Run perception"}</button></div>
      <p>JPEG / PNG / WEBP · max 2 MB · 2048 × 2048 · 4 million pixels. Upload validation runs on the server. The controlled fixture requires the task on Wearable.</p>
      {notice && <p role="status">{notice}</p>}
      {!image ? <p>No sanitized media. Attach the controlled scene or upload an image.</p> : <div className="visual-grid"><div className="visual-evidence"><span className="eyebrow">SANITIZED MEDIA / {image.source}</span><p>{image.source === "FIXTURE_IMAGE" ? "FIXTURE MEDIA / NO PERSONAL IMAGE DATA / metadata-free source" : image.metadata_removed ? "METADATA STRIPPED" : "NORMALIZED / no source metadata found"}</p><div className="visual-image">
        <img src={`/api/v1/tasks/${task.id}/media/${image.id}/content`} alt={image.source === "FIXTURE_IMAGE" ? "Controlled synthetic meeting scene with sign, laptop, backpack and cup" : "Sanitized uploaded evidence"} />
        {run?.observations.filter(o => o.region).map(o => <span className="actual-region" key={o.id} style={{ left: `${o.region!.x*100}%`, top: `${o.region!.y*100}%`, width: `${o.region!.width*100}%`, height: `${o.region!.height*100}%` }} />)}
      </div><code>MEDIA {image.id}<br />SHA256 {image.sha256}</code></div><div><span className="eyebrow">PERCEPTION PIPELINE</span><div className="pipeline-stage">INGEST → SANITIZE / DONE</div>{run ? run.processors.map(p => <div className="pipeline-stage" key={p.processor}>{p.processor} / {p.status}<small>{p.model} · {p.simulation ? "SIMULATED" : "REAL PROCESSOR"} · {p.latency_ms == null ? "NO INVOCATION" : `${p.latency_ms} ms`}</small></div>) : <p>Processors have not run.</p>}<p>OBSERVATIONS → BOUNDED CONTEXT</p>{run && <><code>TRACE {run.trace_id}</code><p>{run.privacy_class}</p>{run.warnings.map(w => <p key={w}>{w}</p>)}</>}</div></div>}
      {run && <><div className="observation-grid">{run.observations.map(o => <article className="observation-card" key={o.id}><span className="eyebrow">OBSERVATION / {o.simulation ? "SIMULATED / FIXTURE" : "MODEL EVIDENCE"}</span><h3>{o.label}</h3><p>{o.description}</p><p>{o.processor} / {o.model}</p><p>SCORE {o.score ?? "NONE"} / {o.score_type}</p><code>{o.source} · {o.device}<br />OBSERVATION {o.id}</code>{o.mask_reference && <Link href={`/api/v1/tasks/${task.id}/artifacts/${o.mask_reference}/content`}>View actual segmentation mask</Link>}</article>)}</div><div className="visual-interpretation"><span className="eyebrow">NOVA INTERPRETATION / NOT A VERIFIED FACT</span><p>{run.context.find(c => c.interpretation.includes("consistent"))?.interpretation ?? "Insufficient evidence for a meeting/work interpretation."}</p></div><button className="button ghost" disabled={blocked || !run.context.length} onClick={() => void mutate(async () => { const result = await api<{ task_id: string; proposal: { proposal: { status: string } } | null }>(`/tasks/${task.id}/perception/${run.id}/reason`, { method: "POST", body: JSON.stringify({ idempotency_key: `reason-${run.id}`, propose_action: true }) }); if (alive.current && owner.current() && result.task_id === task.id) setNotice(`Visual context passed to Context/Planner. Proposal: ${result.proposal?.proposal?.status ?? "not justified"}. No external message sent.`); })}>Reason with visual context</button><Link className="button ghost" href={`/models?task=${task.id}`}>Inspect VISION route</Link><Link className="button ghost" href={`/approvals?task=${task.id}`}>Review human approval</Link></>}
    </>}
  </section>;
}
