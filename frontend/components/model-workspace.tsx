"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { api, type Task } from "@/lib/api";
import type { Budget, ModelCall, ModelResponse, Providers } from "@/lib/models";

type Scenario = "SIMPLE" | "REASONING" | "PRIVACY" | "BUDGET" | "FAILURE";
type Intent = { task_id: string; request_id: string; scenario: Scenario };
type Snapshot = { calls: ModelCall[]; providers: Providers; budget: Budget };

export default function ModelWorkspace({ task, disabled, canMutate, compact = false }: {
  task: Task; disabled: boolean; canMutate: () => boolean; compact?: boolean;
}) {
  const [data, setData] = useState<Snapshot | null>(null);
  const [result, setResult] = useState<ModelResponse | null>(null);
  const [scenario, setScenario] = useState<Scenario>("SIMPLE");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [pending, setPending] = useState<Intent | null>(null);
  const mounted = useRef(false), posting = useRef(false), generation = useRef(0);
  const active = useRef<AbortController | null>(null);
  const owner = useRef(canMutate);
  useEffect(() => { owner.current = canMutate; }, [canMutate]);
  const storageKey = `nova.model-intent.${task.id}`;

  const load = useCallback(async () => {
    const version = ++generation.current;
    active.current?.abort(); const controller = new AbortController(); active.current = controller;
    try {
      const [calls, providers, budget] = await Promise.all([
        api<ModelCall[]>(`/tasks/${task.id}/model-calls`, { signal: controller.signal }),
        api<Providers>("/model-router/providers", { signal: controller.signal }),
        api<Budget>("/model-router/budget", { signal: controller.signal }),
      ]);
      if (!mounted.current || controller.signal.aborted || generation.current !== version) return;
      if (calls.some(call => call.task_id !== task.id)) throw new Error("Model history task identity mismatch.");
      setData({ calls, providers, budget }); setError("");
    } catch (cause) { if (mounted.current && !controller.signal.aborted && generation.current === version)
      setError(cause instanceof Error ? cause.message : "Unable to load model state."); }
  }, [task.id]);

  useEffect(() => {
    const alive = mounted, reads = active, versions = generation;
    alive.current = true;
    const timer = setTimeout(() => {
      try { const value = localStorage.getItem(storageKey); if (value) {
        const intent = JSON.parse(value) as Intent;
        if (intent.task_id === task.id && typeof intent.request_id === "string") setPending(intent);
      } } catch { /* Request intent storage is optional. */ }
      void load();
    }, 0);
    const interval = setInterval(() => { if (!document.hidden) void load(); }, 5000);
    return () => { alive.current = false; ++versions.current; reads.current?.abort(); clearTimeout(timer); clearInterval(interval); };
  }, [load, storageKey, task.id]);

  async function evaluate(intent: Intent) {
    if (!mounted.current || posting.current || !data || disabled || !owner.current() || intent.task_id !== task.id) return;
    posting.current = true; setBusy(true); setPending(intent); setResult(null);
    try { localStorage.setItem(storageKey, JSON.stringify(intent)); } catch { /* Optional storage. */ }
    try {
      const next = await api<ModelResponse>("/model-router/evaluate", { method: "POST", body: JSON.stringify(intent) });
      if (!mounted.current || !owner.current()) return;
      if (next.task_id !== task.id) throw new Error("Model result task identity mismatch.");
      setResult(next); setPending(null);
      try { localStorage.removeItem(storageKey); } catch { /* Optional storage. */ }
      await load();
    } catch (cause) { if (mounted.current && owner.current()) setError(cause instanceof Error ? cause.message : "Model request was not confirmed."); }
    finally { posting.current = false; if (mounted.current) setBusy(false); }
  }
  const decision = result?.decision ?? data?.calls[0]?.decision;
  const blocked = disabled || busy || !data;

  return <section className="model-workspace panel" data-testid="model-workspace" data-task-id={task.id} aria-label="Model Intelligence">
    <div className="panel-heading"><div><span className="eyebrow">MODEL INTELLIGENCE / ROUTING POLICY</span><h2>{compact ? "Model Router" : "Routing control plane"}</h2></div><span className="tag">{data?.providers.local_runtime ?? "LOADING PROVIDERS"}</span></div>
    {error && <div className="error-notice" role="alert"><p>{error}</p><button className="button ghost" onClick={() => void load()} disabled={busy}>Reload model state</button></div>}
    {!data ? <p role="status">Loading persisted model calls and routing policy…</p> : compact ? <div className="model-summary"><p>Mode: {data.providers.providers.some(p => p.kind === "LOCAL" && p.health.state === "AVAILABLE") ? "Optional local / fixture fallback" : "Fixture / deterministic"}</p><p>Last route: {decision?.reason_codes.join(" → ") ?? "No model request recorded for this task."}</p><p>NO PAID PROVIDERS ENABLED</p><Link className="button ghost" href={`/models?task=${task.id}`}>Open Model Router</Link></div> : <>
      <div className="model-disclosure"><strong>NO PAID PROVIDERS ENABLED</strong><p>Fixture responses are deterministic replay, not an LLM. Optional local inference executes on the developer host; device eligibility is a routing simulation. Local compute/electricity is not priced.</p><p>BUDGET and FAILURE scenarios use explicit TEST POLICY FIXTURES, not production benchmarks.</p></div>
      <div className="provider-grid" aria-label="Configured providers">{data.providers.providers.map(provider => <article className="provider-card" key={provider.provider}>
        <span className="eyebrow">{provider.kind}</span><h3>{provider.provider}</h3><code>{provider.model}</code><p className="provider-health">{provider.health.state} · CIRCUIT {provider.circuit}</p><p>{provider.capabilities.join(" / ")}</p><p>{provider.disclosure}</p><span className="mono">CONSECUTIVE FAILURES {provider.consecutive_failures} · CHECKED {provider.health.last_checked ?? "NO ENDPOINT CHECK REQUIRED"}</span>
      </article>)}</div>
      <div className="model-controls"><label>Routing scenario<select aria-label="Routing scenario" value={scenario} disabled={busy || !!pending} onChange={event => setScenario(event.target.value as Scenario)}>{["SIMPLE", "REASONING", "PRIVACY", "BUDGET", "FAILURE"].map(value => <option value={value} key={value}>{value}</option>)}</select></label>
        <button className="button primary" disabled={blocked} onClick={() => void evaluate(pending ?? { task_id: task.id, request_id: crypto.randomUUID(), scenario })}>{busy ? "Awaiting model response…" : pending ? "Retry original model request" : "Evaluate route"}</button>
      </div>
      <p className="requested-model-input"><span className="eyebrow">SCENARIO REQUEST / SYNTHETIC INPUT</span><br />{data.providers.scenarios[scenario]}</p>
      {pending && <p role="status">Request acknowledgment pending. Retrying keeps the original request ID.</p>}
      {decision ? <div className="routing-decision" data-testid="routing-decision"><span className="eyebrow">EXPLAINABLE ROUTING DECISION</span><div className="route-path"><span>REQUEST</span><span>{decision.privacy_class}</span><span>{decision.complexity}</span><span>{decision.device_context} / SIMULATED ELIGIBILITY</span><span>{decision.selected_tier ?? "NO ELIGIBLE PROVIDER"}</span><span>{decision.selected_provider ?? "CONTROLLED FAILURE"}</span></div><p className="route-reasons">{decision.reason_codes.join(" → ")}</p><p>Privacy: {decision.privacy_decision} · Budget: {decision.budget_decision} · Classification: {decision.classification_reason}</p>
        <details><summary>Candidate eligibility / fallback chain</summary>{decision.candidates.map(candidate => <p key={candidate.provider}>{candidate.provider}: {candidate.eligible ? "ELIGIBLE" : candidate.reasons.join(" / ")}</p>)}<p>{decision.fallback_chain.join(" → ")}</p></details>
        {result?.output && <p className="model-output">{typeof result.output.summary === "string" ? result.output.summary : "Validated structured output returned; generated content is not retained in call history."}</p>}
        {result?.replayed && <p>Original request metadata replayed; no new provider invocation. Output is not retained in PostgreSQL.</p>}
        {result?.status === "FAILED" && <p role="alert">Controlled failure: {result.safe_error}</p>}
      </div> : <p>No model route evaluated yet.</p>}
      <div className="budget-panel"><span className="eyebrow">BUDGET / {data.budget.day} UTC</span><div className="budget-values"><span>Daily cap <b>${data.budget.daily_budget_usd}</b></span><span>Request cap <b>${data.budget.per_request_cap_usd}</b></span><span>Accounted exposure <b>${data.budget.consumed_usd}</b></span><span>Reserved <b>${data.budget.reserved_usd}</b></span><span>Remaining <b>${data.budget.remaining_usd}</b></span></div><p>{data.budget.disclosure}</p></div>
      <div className="model-history"><div className="panel-heading"><h3>Task model calls</h3><span className="mono">{data.calls.length} PERSISTED REQUESTS</span></div>{!data.calls.length ? <p>No model calls for this task. Choose a scenario to evaluate routing.</p> : data.calls.map(call => <article className="model-call" key={call.id} data-request-id={call.request_id}>
        <div><strong>{call.response?.provider ?? "Unselected"} / {call.response?.model ?? "—"}</strong><span className="tag">{call.status} / {call.response?.mode}</span></div><p>{call.decision.complexity} · {call.decision.privacy_class} · {call.response?.route_tier}</p><dl><div><dt>LATENCY / PROVIDER</dt><dd>{call.response?.latency_ms == null ? "— / NO FRESH INVOCATION" : `${call.response.latency_ms} ms`}</dd></div><div><dt>TOKENS</dt><dd>{call.response?.total_tokens ?? "UNKNOWN"} / {call.response?.usage_source ?? "UNKNOWN"}</dd></div><div><dt>COST</dt><dd>{call.response?.cost_status} {call.response?.estimated_cost_usd == null ? "" : `/ $${call.response.estimated_cost_usd}`}</dd></div><div><dt>CACHE</dt><dd>{call.response?.cache_status}</dd></div><div><dt>FALLBACK</dt><dd>{call.response?.fallback_used ? "YES / POLICY CHECKED" : "NO"}</dd></div></dl><code>TRACE {call.trace_id}</code><p>{call.decision.reason_codes.join(" / ")}</p><details><summary>Recorded attempts</summary>{call.attempts.map((attempt, index) => <p key={index}>{attempt.provider} · {attempt.error ?? attempt.status} · {attempt.invoked ? "INVOKED" : "NOT INVOKED"}</p>)}</details>
      </article>)}</div>
    </>}
  </section>;
}
