"use client";

import Link from "next/link";
import OwnedDraftWorkspace from "@/components/owned-draft-workspace";
import { useCallback, useEffect, useRef, useState } from "react";
import { api, type Task } from "@/lib/api";
import type { Audit, Proposal, ProposalDetail, Trigger } from "@/lib/proactive";

type Intent = { proposalId: string; operation: string; body: { idempotency_key: string; content?: string; recipient?: string } };
type Snapshot = { proposals: Proposal[]; triggers: Trigger[]; audit: Audit[] };

export default function ApprovalWorkspace({ task, disabled, canMutate, isCurrentTask, compact = false }: {
  task: Task; disabled: boolean; canMutate: () => boolean; isCurrentTask?: () => boolean; compact?: boolean;
}) {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [pending, setPending] = useState<Intent | null>(null);
  const [edit, setEdit] = useState<{ id: string; content: string; recipient: string } | null>(null);
  const [notice, setNotice] = useState("");
  const alive = useRef(false);
  const posting = useRef(false);
  const generation = useRef(0);
  const active = useRef<AbortController | null>(null);
  const ownership = useRef(canMutate);
  useEffect(() => { ownership.current = canMutate; }, [canMutate]);
  const selection = useRef(isCurrentTask ?? canMutate);
  useEffect(() => { selection.current = isCurrentTask ?? canMutate; }, [isCurrentTask, canMutate]);
  const storageKey = `nova.action-intent.${task.id}`;

  const load = useCallback(async () => {
    const version = ++generation.current;
    active.current?.abort();
    const controller = new AbortController(); active.current = controller;
    try {
      const [proposals, triggers, audit] = await Promise.all([
        api<Proposal[]>(`/tasks/${task.id}/proposals`, { signal: controller.signal }),
        api<Trigger[]>(`/tasks/${task.id}/proactive`, { signal: controller.signal }),
        api<Audit[]>(`/tasks/${task.id}/audit-events`, { signal: controller.signal }),
      ]);
      if (!alive.current || controller.signal.aborted || version !== generation.current) return;
      if (proposals.some(item => item.task_id !== task.id)) throw new Error("Proposal task identity mismatch.");
      setSnapshot({ proposals, triggers, audit }); setError("");
    } catch (cause) {
      if (alive.current && !controller.signal.aborted && version === generation.current)
        setError(cause instanceof Error ? cause.message : "Unable to load approvals.");
    }
  }, [task.id]);

  useEffect(() => {
    const mounted = alive, requests = active, versions = generation;
    mounted.current = true;
    const timer = setTimeout(async () => {
      try { const value = localStorage.getItem(storageKey); if (value) setPending(JSON.parse(value)); } catch { /* Optional intent storage. */ }
      // Receive a synthetic TIME_TICK; the user has not asked for lateness analysis.
      try {
        if (ownership.current()) await api("/proactive/evaluate", { method: "POST", body: JSON.stringify({
          task_id: task.id, event_type: "TIME_TICK", scenario: "MEETING_TRAVEL_RISK", idempotency_key: `fixture-context-${task.id}`,
        }) });
        if (mounted.current) await load();
      } catch (cause) {
        if (mounted.current) setError(cause instanceof Error ? cause.message : "Context evaluation failed.");
      }
    }, 0);
    const interval = setInterval(() => { if (!document.hidden) void load(); }, 5000);
    return () => { mounted.current = false; ++versions.current; requests.current?.abort(); clearTimeout(timer); clearInterval(interval); };
  }, [load, storageKey, task.id]);

  async function mutate(intent: Intent) {
    if (!alive.current || posting.current || !snapshot || !ownership.current() || disabled) return;
    if (!snapshot.proposals.some(item => item.id === intent.proposalId && item.task_id === task.id)) return;
    posting.current = true; setBusy(true); setPending(intent); setNotice("");
    // Contains request intent only. Authoritative proposal/approval state always comes from PostgreSQL.
    try { localStorage.setItem(storageKey, JSON.stringify(intent)); } catch { /* Optional intent storage. */ }
    try {
      const result = await api<ProposalDetail>(`/proposals/${intent.proposalId}/${intent.operation}`, {
        method: "POST", body: JSON.stringify(intent.body),
      });
      if (!alive.current || !selection.current()) return;
      if (result.proposal.task_id !== task.id) throw new Error("Approval task identity mismatch.");
      try { localStorage.removeItem(storageKey); } catch { /* Optional intent storage. */ }
      setPending(null); setEdit(null);
      setNotice(result.execution?.status === "DONE" ? "SIMULATED DELIVERY COMPLETE — NO EXTERNAL MESSAGE WAS SENT"
        : intent.operation === "edit" ? "New proposal created. New approval is required."
        : `Decision recorded: ${result.proposal.status}.`);
      await load();
    } catch (cause) {
      if (alive.current && selection.current()) setError(cause instanceof Error ? cause.message : "Decision was not confirmed. Retry the original request.");
    } finally { posting.current = false; if (alive.current) setBusy(false); }
  }

  async function evaluateNewContext() {
    if (posting.current || disabled || !ownership.current()) return;
    posting.current = true; setBusy(true);
    const contextKey = `nova.context-intent.${task.id}`;
    let key = crypto.randomUUID();
    try { key = localStorage.getItem(contextKey) ?? key; localStorage.setItem(contextKey, key); } catch { /* Optional intent storage. */ }
    try {
      await api("/proactive/evaluate", { method: "POST", body: JSON.stringify({ task_id: task.id,
        event_type: "TIME_TICK", idempotency_key: key }) });
      if (!alive.current || !selection.current()) return;
      try { localStorage.removeItem(contextKey); } catch { /* Optional intent storage. */ }
      await load();
    } catch (cause) { if (alive.current && selection.current()) setError(cause instanceof Error ? cause.message : "Context event was not confirmed."); }
    finally { posting.current = false; if (alive.current) setBusy(false); }
  }

  function request(proposal: Proposal, operation: string, changes = {}) {
    void mutate({ proposalId: proposal.id, operation, body: { idempotency_key: crypto.randomUUID(), ...changes } });
  }
  const blocked = disabled || busy || !!pending;
  const surfaced = snapshot?.triggers.find(item => item.status === "SURFACED" && item.reason !== "OWNED_SUPPORTED_DRAFT");

  return <section className="approval-workspace" data-testid="approvals" data-task-id={task.id} aria-label="Proactive intelligence and approval control">
    <div className="panel-heading"><div><span className="eyebrow">PROACTIVE INTELLIGENCE / HUMAN APPROVAL</span><h2>{compact ? "Context worth your attention." : "Approval Center"}</h2></div><span className="tag">DEMO CONTEXT / FIXTURE CLOCK</span></div>
    {error && <div className="error-notice" role="alert"><p>{error}</p><button className="button ghost" onClick={() => void load()} disabled={busy}>Reload proposals</button></div>}
    {!compact && <OwnedDraftWorkspace taskId={task.id} disabled={disabled} canMutate={canMutate} isCurrentTask={isCurrentTask ?? canMutate} />}
    {notice && <div className="success-notice" role="status">{notice}</div>}
    {pending && <div className="phase-notice"><p>{busy ? "Awaiting response. No decision is assumed." : "An action request is unacknowledged. Retry with its original key."}</p><button className="button ghost" disabled={busy || disabled || !snapshot} onClick={() => void mutate(pending)}>Retry original request</button></div>}
    {!snapshot ? <p role="status">Loading persisted proactive context…</p> : <>
      {surfaced && <div className="risk-summary"><span className="eyebrow">TRAVEL RISK DETECTED · 13:31 FIXTURE TIME</span><h3>{surfaced.situation.meeting.title} · 2:00 PM</h3><div className="risk-numbers"><span><b>{surfaced.situation.minutes_available}m</b> available</span><span><b>{surfaced.situation.travel_minutes}m</b> travel</span><span><b>+{surfaced.situation.lateness_minutes}m</b> risk</span></div><p>You may arrive approximately {surfaced.situation.lateness_minutes} minutes late. NOVA prepared a message proposal for your review.</p><span className="mono">COMMUNICATION AGENT / {surfaced.agent_record?.status} · SEMANTIC KERNEL</span></div>}
      {compact ? <Link className="button primary" href={`/approvals?task=${task.id}`}>Review proposal</Link> : <>
        {!snapshot.proposals.length && <div className="empty-state"><h3>No action proposals</h3><p>{snapshot.triggers.at(-1)?.reason ?? "Waiting for the synthetic context event."}</p><p>Redis failure or cooldown suppresses suggestions safely. No action is authorized.</p><button className="button ghost" disabled={blocked} onClick={() => void evaluateNewContext()}>Evaluate new fixture event</button></div>}
        {snapshot.proposals.map(proposal => <article className="panel proposal-card" key={proposal.id} data-proposal-id={proposal.id}>
          <div className="panel-heading"><span className="eyebrow">PROACTIVE / {proposal.status === "PENDING_APPROVAL" ? "REQUIRES APPROVAL" : proposal.status}</span><span className="tag">{proposal.policy_decision}</span></div>
          <h3>{proposal.policy_version === "OWNED_CONTEXT_V1" ? "Suggested preference recommendation" : "Notify attendee"}</h3><p>Recipient: {proposal.recipient} · {proposal.policy_version === "OWNED_CONTEXT_V1" ? "LOCAL DRAFT / EXECUTION DISABLED" : "MESSAGE / SIMULATION ONLY"}</p><blockquote>{proposal.content}</blockquote><p>{proposal.reason}</p>
          <dl className="proposal-meta"><div><dt>PROPOSAL</dt><dd data-testid="proposal-id">{proposal.id}</dd></div><div><dt>TRACE</dt><dd>{proposal.trace_id}</dd></div><div><dt>PAYLOAD SHA-256</dt><dd>{proposal.payload_hash}</dd></div><div><dt>EXPIRES / {proposal.policy_version === "OWNED_CONTEXT_V1" ? "SYSTEM CLOCK" : "FIXTURE CLOCK"}</dt><dd>{proposal.expires_at}</dd></div></dl>
          {edit?.id === proposal.id ? <form onSubmit={event => { event.preventDefault(); request(proposal, "edit", { content: edit.content, recipient: edit.recipient }); }}><label>Recipient<input aria-label="Edit recipient" required maxLength={120} value={edit.recipient} onChange={event => setEdit({ ...edit, recipient: event.target.value })} /></label><label>Draft<textarea aria-label="Edit draft" required maxLength={1000} value={edit.content} onChange={event => setEdit({ ...edit, content: event.target.value })} /></label><p>Creates a new proposal. Previous approval cannot authorize the edited draft.</p><button className="button primary" disabled={blocked}>Save new proposal</button><button type="button" className="button ghost" disabled={busy} onClick={() => setEdit(null)}>Cancel edit</button></form> : <div className="proposal-controls">
            {proposal.policy_version !== "OWNED_CONTEXT_V1" && ["PENDING_APPROVAL", "APPROVED"].includes(proposal.status) && <button className="button ghost" disabled={blocked} onClick={() => setEdit({ id: proposal.id, content: proposal.content, recipient: proposal.recipient })}>Edit</button>}
            {proposal.status === "PENDING_APPROVAL" && <>{proposal.policy_version !== "OWNED_CONTEXT_V1" && <button className="button primary" disabled={blocked} onClick={() => request(proposal, "approve")}>Approve</button>}<button className="button ghost" disabled={blocked} onClick={() => request(proposal, "reject")}>Reject</button></>}
            {proposal.policy_version !== "OWNED_CONTEXT_V1" && proposal.status === "APPROVED" && <button className="button primary" disabled={blocked} onClick={() => request(proposal, "execute")}>Execute simulation</button>}
          </div>}
          {proposal.status === "EXECUTED" && <div className="success-notice">SIMULATED DELIVERY COMPLETE · NO EXTERNAL MESSAGE WAS SENT</div>}
          {proposal.status === "SUPERSEDED" && <p>Superseded. Any previous approval is unusable.</p>}
          <span className="mono">SIMULATED / NOT SENT · NO COMMUNICATION TRANSPORT</span>
        </article>)}
        <details className="panel"><summary>Persistent audit history ({snapshot.audit.length})</summary>{snapshot.audit.map(event => <p className="mono" key={event.id}>{event.event_type} · {event.trace_id}</p>)}</details>
      </>}
      {snapshot.triggers.some(item => item.status !== "SURFACED") && <details><summary>Suppressed context evaluations</summary>{snapshot.triggers.filter(item => item.status !== "SURFACED").map(item => <p key={item.id}>{item.status}: {item.reason}</p>)}</details>}
    </>}
  </section>;
}
