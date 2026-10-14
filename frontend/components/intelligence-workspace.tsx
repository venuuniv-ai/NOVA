"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { Check, Cpu, GitBranch, LoaderCircle, Play, RefreshCw, ShieldCheck } from "lucide-react";
import { api, ApiError, type Task } from "@/lib/api";
import type { AgentRun, Execution, Intelligence } from "@/lib/intelligence";

const STAGES = [
  { stage: "context", name: "Context", role: "Discover requirements", group: "context" },
  { stage: "planner", name: "Planner", role: "Initial plan", group: "planner" },
  { stage: "calendar", name: "Calendar", role: "Meeting evidence", group: "specialists" },
  { stage: "memory", name: "Memory", role: "Explicit preferences", group: "specialists" },
  { stage: "planner_revision", name: "Planner revision", role: "Combine evidence", group: "revision" },
  { stage: "critic", name: "Critic", role: "Check the proposal", group: "critic" },
];

function elapsed(run: AgentRun) {
  if (!run.started_at || !run.completed_at) return "—";
  return `${Math.max(0, Date.parse(run.completed_at) - Date.parse(run.started_at))} ms`;
}

function displayTime(time: string) {
  const [hour, minute] = time.split(":").map(Number);
  return `${hour % 12 || 12}:${minute.toString().padStart(2, "0")} ${hour >= 12 ? "PM" : "AM"}`;
}

export default function IntelligenceWorkspace({ task, canMutate, disabled }: { task: Task; canMutate: () => boolean; disabled: boolean }) {
  const [data, setData] = useState<Intelligence | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [selectedStage, setSelectedStage] = useState("context");
  const [pendingKey, setPendingKey] = useState<string | null>(null);
  const mounted = useRef(false);
  const generation = useRef(0);
  const activeRead = useRef<AbortController | null>(null);
  const posting = useRef(false);
  const storageKey = `nova.intelligence.${task.id}`;

  const load = useCallback(async () => {
    const version = ++generation.current;
    activeRead.current?.abort();
    const controller = new AbortController();
    activeRead.current = controller;
    try {
      const next = await api<Intelligence>(`/tasks/${task.id}/plan`, { signal: controller.signal });
      if (!mounted.current || controller.signal.aborted || generation.current !== version) return;
      if (next.task_id !== task.id) throw new Error("Intelligence does not belong to the selected task.");
      setData(next);
      setError(null);
    } catch (cause) {
      if (mounted.current && !controller.signal.aborted && generation.current === version) {
        setError(cause instanceof Error ? cause.message : "Unable to load intelligence.");
      }
    }
  }, [task.id]);

  useEffect(() => {
    const reads = activeRead;
    const versions = generation;
    const alive = mounted;
    alive.current = true;
    const initial = setTimeout(() => {
      try { setPendingKey(localStorage.getItem(storageKey)); } catch { /* Optional request-intent storage. */ }
      void load();
    }, 0);
    const interval = setInterval(() => { if (!document.hidden) void load(); }, 2000);
    return () => {
      alive.current = false;
      ++versions.current;
      reads.current?.abort();
      clearTimeout(initial);
      clearInterval(interval);
    };
  }, [load, storageKey]);

  async function runIntelligence() {
    // Parent ownership guard protects the selection before navigation commits.
    if (!mounted.current || posting.current || !data || data.task_id !== task.id || !canMutate()) return;
    posting.current = true;
    setBusy(true);
    setNotice("");
    let key = pendingKey ?? crypto.randomUUID();
    try {
      key = localStorage.getItem(storageKey) ?? key;
      localStorage.setItem(storageKey, key);
    } catch { /* Server-side idempotency still applies to this request key. */ }
    setPendingKey(key);
    try {
      const result = await api<{ execution: Execution; replayed: boolean }>(`/tasks/${task.id}/run-agents`, {
        method: "POST", body: JSON.stringify({ idempotency_key: key }),
      });
      if (!mounted.current || !canMutate()) return;
      if (result.execution.task_id !== task.id) throw new Error("Execution task identity did not match.");
      if (result.execution.status !== "RUNNING") {
        try { localStorage.removeItem(storageKey); } catch { /* Optional storage. */ }
        setPendingKey(null);
      }
      setNotice(result.replayed ? "Original execution acknowledged; no duplicate agents were created."
        : result.execution.status === "FAILED" ? "Execution failed. Inspect the recorded failure below."
        : "Deterministic execution completed. No LLM or external personal data was used.");
      await load();
    } catch (cause) {
      if (mounted.current && canMutate()) setError(cause instanceof ApiError ? cause.message : "Execution could not be confirmed. Retry with the original key.");
    } finally {
      posting.current = false;
      if (mounted.current) setBusy(false);
    }
  }

  const routed = data?.execution?.provider === "NOVA ModelRouter";
  const runs = data?.agent_runs ?? [];
  const selected = runs.find(run => run.stage === selectedStage);
  const running = data?.execution?.status === "RUNNING";
  const blocked = busy || disabled || !data || (running && !pendingKey);
  const nodes = [...STAGES, ...runs.filter(run => !STAGES.some(node => node.stage === run.stage)).map(run => ({
    stage: run.stage, name: run.agent_name === "PLANNER" ? "Planner correction" : "Critic recheck", role: "Critique feedback", group: "correction",
  }))];

  return <section className="intelligence-workspace" aria-label="NOVA Intelligence" data-testid="intelligence" data-task-id={task.id}>
    <div className="intelligence-heading"><div><span className="eyebrow"><GitBranch size={13} /> INTELLIGENCE / EXECUTION GRAPH</span><h2>Evidence becomes a plan.</h2><p>Specialized agents, bounded plugins, and a shared persistent task.</p></div>
      <button className="button primary" onClick={() => void runIntelligence()} disabled={blocked} aria-label="Run NOVA Intelligence">{busy || running ? <LoaderCircle size={16} className="spin" /> : <Play size={15} />}{busy ? "Awaiting response…" : pendingKey ? "Retry original execution" : running ? "Execution running" : data?.execution ? "Run again" : "Run NOVA Intelligence"}</button>
    </div>
    <div className="intelligence-disclosure"><Cpu size={16} /><div><strong>{routed ? "ROUTED / APPLICATION POLICY" : "FIXTURE / DETERMINISTIC"}</strong><span>DEMO CONTEXT · Synthetic calendar, preferences, and location. No real personal-data access.</span></div><span className="tag">{routed ? "INSPECT RECORDED PROVIDERS" : "NOT AN LLM"}</span></div>
    {routed && <Link className="button ghost" href={`/models?task=${task.id}`}>Recorded model providers</Link>}
    <div className="intelligence-goal"><span className="eyebrow">TASK GOAL</span><p>{task.title}</p><code>{task.id}</code></div>
    {notice && <div className="success-notice" role="status"><Check size={15} />{notice}</div>}
    {error && <div className="error-notice" role="alert" aria-label="Intelligence error"><span>{error}</span><button className="button ghost small" onClick={() => void load()}><RefreshCw size={13} />Reload intelligence</button></div>}
    {!data ? <div className="loading-state" role="status"><LoaderCircle size={20} className="spin" /><p>Loading intelligence attached to this task…</p></div> : <>
      <div className="execution-caption"><span className="mono">{data.execution ? `EXECUTION ${data.execution.status}` : "NO EXECUTION YET / WORKFLOW BLUEPRINT"}</span>{data.execution && <code data-testid="trace-id">TRACE {data.execution.trace_id}</code>}</div>
      <div className="agent-graph" aria-label="Agent execution graph">{nodes.map(node => {
        const run = runs.find(item => item.stage === node.stage);
        const status = run?.status ?? "WAITING";
        return <button key={node.stage} className={`agent-node ${status.toLowerCase()} ${selectedStage === node.stage ? "selected" : ""}`} style={{ gridArea: node.group === "correction" ? undefined : node.group }} onClick={() => setSelectedStage(node.stage)} aria-label={`Inspect ${node.name} agent`} aria-pressed={selectedStage === node.stage} data-stage={node.stage} data-status={status}>
          <span className="mono node-sequence">{run ? run.sequence.toString().padStart(2, "0") : "—"}</span><span className="agent-node-name">{node.name}</span><span className="agent-node-role">{node.role}</span><span className="agent-status">{status === "RUNNING" && <LoaderCircle size={11} className="spin" />}{status === "DONE" && <Check size={11} />}{status}</span>
        </button>;
      })}<div className="graph-fork" aria-hidden="true" /><div className="graph-join" aria-hidden="true" /></div>
      <section className="panel agent-inspector" aria-label="Agent execution detail"><div className="panel-heading"><h2>{nodes.find(node => node.stage === selectedStage)?.name ?? selectedStage}</h2><span className="tag">{routed ? "ROUTED / SEE MODEL HISTORY" : "FIXTURE / DETERMINISTIC"}</span></div>
        {selected ? <div className="inspector-body"><p>{selected.summary || "Waiting for this stage to execute."}</p><div className="inspector-meta"><span>STATUS <b>{selected.status}</b></span><span>DURATION <b>{elapsed(selected)}</b></span><span>PROVIDER <b>{selected.provider}</b></span></div>
          {selected.error && <p className="form-error">Failure: {selected.error}</p>}
          {selected.evidence.length > 0 && <div className="agent-evidence"><span className="eyebrow">EVIDENCE / DEMO CONTEXT</span>{selected.evidence.map((item, index) => <div key={`${item.provenance.reference}-${index}`}><strong>{item.fact}</strong><span className="mono">{item.provenance.source} · {item.provenance.reference}</span></div>)}</div>}
          <div className="agent-tools"><span className="eyebrow">TOOLS USED THROUGH SEMANTIC KERNEL</span>{selected.tool_calls.length ? selected.tool_calls.map(tool => <div className="tool-record" key={tool.id}><strong>{tool.plugin}.{tool.function}</strong><span className="tag">{tool.status}</span><code>TRACE {tool.trace_id}</code><details><summary>Inspect bounded tool record</summary><pre>{JSON.stringify({ input: tool.input, output: tool.output, error: tool.error }, null, 2)}</pre></details></div>) : <p>No tool was invoked by this stage.</p>}</div>
          {selected.structured_output && <details className="structured-output"><summary>Structured output</summary><pre>{JSON.stringify(selected.structured_output, null, 2)}</pre></details>}
          {selected.warnings.map(warning => <p className="agent-warning" key={warning}>{warning}</p>)}
        </div> : <div className="inspector-body"><p>No execution record exists yet. Run Intelligence to produce real persisted fixture traces.</p></div>}
      </section>
      {data.context && <section className="panel discovered-context"><div className="panel-heading"><h2>Context discovered</h2><span className="tag">DEMO CONTEXT</span></div><div className="context-facts">{data.context.calendar.map((event, index) => <div key={index}><span className="eyebrow">SYNTHETIC CALENDAR</span><strong>{event.title}</strong><p>{event.date_label} · {displayTime(event.starts_at)}–{displayTime(event.ends_at)} · {event.location}</p></div>)}{data.context.preferences.map(preference => <div key={preference.provenance.reference}><span className="eyebrow">EXPLICIT SYNTHETIC PREFERENCE</span><strong>{preference.preference}</strong><p>{preference.provenance.source} · {preference.provenance.memory_type}</p></div>)}{data.context.location && <div><span className="eyebrow">SIMULATED LOCATION</span><strong>{data.context.location.description}</strong></div>}</div></section>}
      <section className="panel final-plan" aria-label="Final plan"><div className="panel-heading"><div><span className="eyebrow">{data.plan ? "PERSISTED / APPROVED BY CRITIC" : "AWAITING VERIFIED EXECUTION"}</span><h2>Final plan</h2></div><span className="critic-verdict"><ShieldCheck size={15} />{data.critic?.verdict ?? "NOT REVIEWED"}</span></div>
        {data.plan ? <div className="plan-body"><p>{data.plan.goal}</p><span className="eyebrow">FACTUAL CONSTRAINTS / DEMO CONTEXT</span><ul className="plan-constraints">{data.plan.constraints.map((constraint, index) => <li key={index}><Check size={14} /><span>{constraint.fact}</span></li>)}</ul><span className="eyebrow">PROPOSED STEPS</span><ol className="plan-steps">{data.plan.steps.map((step, index) => <li key={index}>{step.title}{step.requires_approval && <span className="tag">APPROVAL REQUIRED / NOT EXECUTED</span>}</li>)}</ol><div className="missing-information"><span className="eyebrow">STILL UNKNOWN</span>{data.plan.missing_information.map(item => <p key={item}>{item}</p>)}</div></div>
          : <div className="plan-body"><p>{data.execution?.status === "FAILED" ? `Execution failed (${data.execution.error}). No final plan was published.` : "No final plan has been published for this task."}</p>{data.critic?.reasons.map(reason => <p className="form-error" key={reason.code}>{reason.code}: {reason.message}</p>)}</div>}
      </section>
    </>}
  </section>;
}
