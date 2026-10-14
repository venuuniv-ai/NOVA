"use client";

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowDownLeft, ArrowRight, ArrowUpRight, Check, ChevronRight, CircleDot,
  Command, Cpu, FileText, Layers3, LoaderCircle, Monitor, Plus, Radio,
  RefreshCw, Smartphone, Watch, WifiOff, X,
} from "lucide-react";
import { api, ApiError, DEMO_TITLE, type Device, type DeviceType, type Handoff,
  type HandoffResult, type Task, type TaskEvent } from "@/lib/api";
import ModelWorkspace from "@/components/model-workspace";
import ApprovalWorkspace from "@/components/approval-workspace";
import IntelligenceWorkspace from "@/components/intelligence-workspace";

type View = "command" | "continuity" | "detail" | "intelligence" | "approvals" | "models";
type Snapshot = { selectionId?: string; devices: Device[]; tasks: Task[]; task: Task | null; events: TaskEvent[] };
const ORDER: DeviceType[] = ["DESKTOP", "WEARABLE", "MOBILE"];
const ICONS = { DESKTOP: Monitor, WEARABLE: Watch, MOBILE: Smartphone };
const TITLES = { command: "Command center", continuity: "Device continuity", detail: "Task detail", intelligence: "NOVA Intelligence", approvals: "Approval Center", models: "Model Router" };

function timestamp(value: string) {
  return new Date(value).toLocaleString("en-US", {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit",
  });
}

function eventLabel(type: string) {
  if (type === "TASK_CREATED") return "Task created on Desktop";
  if (type === "HANDOFF_DESKTOP_TO_WEARABLE") return "Desktop → Wearable";
  if (type === "HANDOFF_WEARABLE_TO_MOBILE") return "Wearable → Mobile";
  return type;
}

function asError(error: unknown) {
  return error instanceof ApiError ? error : new ApiError("Something went wrong. Retry your request.", "REQUEST_FAILED");
}

export default function NovaWorkspace({ view, taskId }: { view: View; taskId?: string }) {
  const router = useRouter();
  const [loadedSnapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [selection, setSelection] = useState({ routeId: taskId, requestedId: taskId });
  // Reconcile URL navigation (including browser Back) before rendering task controls.
  if (selection.routeId !== taskId) {
    setSelection({ routeId: taskId, requestedId: taskId });
  }
  const requestedTaskId = selection.routeId === taskId ? selection.requestedId : taskId;
  const snapshot = loadedSnapshot?.selectionId === requestedTaskId ? loadedSnapshot : null;
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [online, setOnline] = useState(true);
  const [notice, setNotice] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState(DEMO_TITLE);
  const [description, setDescription] = useState("Dinner with Sarah after tomorrow’s meeting. Continue this task across Desktop, Wearable, and Mobile.");
  const loadGeneration = useRef(0);
  const activeLoad = useRef<AbortController | null>(null);
  const selectionOwner = useRef({ id: taskId, version: 0 });
  const mutationPending = useRef(false);
  const mounted = useRef(false);
  const titleRef = useRef<HTMLTextAreaElement>(null);
  const createButtonRef = useRef<HTMLButtonElement>(null);

  useLayoutEffect(() => {
    mounted.current = true;
    return () => { mounted.current = false; };
  }, []);

  const invalidateSelection = useCallback((id: string | undefined) => {
    if (selectionOwner.current.id === id) return;
    selectionOwner.current = { id, version: selectionOwner.current.version + 1 };
    ++loadGeneration.current;
    activeLoad.current?.abort();
  }, []);

  useLayoutEffect(() => {
    invalidateSelection(requestedTaskId);
  }, [invalidateSelection, requestedTaskId]);

  const load = useCallback(async () => {
    const owner = selectionOwner.current;
    if (owner.id !== requestedTaskId) return;
    activeLoad.current?.abort();
    const controller = new AbortController();
    activeLoad.current = controller;
    const generation = ++loadGeneration.current;
    const isCurrent = () => !controller.signal.aborted
      && generation === loadGeneration.current
      && owner.version === selectionOwner.current.version
      && owner.id === selectionOwner.current.id;
    setLoading(true);
    try {
      // All visible task state comes from FastAPI, including after refresh.
      const options = { signal: controller.signal };
      const [devices, tasks] = await Promise.all([api<Device[]>("/devices", options), api<Task[]>("/tasks", options)]);
      const selectedId = owner.id ?? tasks[0]?.id;
      const [task, events] = selectedId
        ? await Promise.all([api<Task>(`/tasks/${selectedId}`, options), api<TaskEvent[]>(`/tasks/${selectedId}/events`, options)])
        : [null, []] as const;
      if (!isCurrent()) return;
      const next = { selectionId: owner.id, devices, tasks, task, events: [...events] };
      setSnapshot(next);
      setError(null);
    } catch (cause) {
      if (isCurrent()) setError(asError(cause));
    } finally {
      if (isCurrent()) setLoading(false);
    }
  }, [requestedTaskId]);

  useEffect(() => {
    const generationTracker = loadGeneration;
    const loadController = activeLoad;
    const initial = setTimeout(() => void load(), 0);
    const onOnline = () => { setOnline(true); void load(); };
    const onOffline = () => setOnline(false);
    const onFocus = () => { if (!document.hidden) void load(); };
    const interval = setInterval(() => { if (!document.hidden) void load(); }, 15000);
    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    window.addEventListener("focus", onFocus);
    return () => {
      ++generationTracker.current;
      loadController.current?.abort();
      clearTimeout(initial);
      clearInterval(interval);
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
      window.removeEventListener("focus", onFocus);
    };
  }, [load]);

  useEffect(() => {
    if (showCreate) titleRef.current?.focus();
  }, [showCreate]);

  const task = snapshot?.task;
  // An implicit landing-page selection resolves to its confirmed backend task.
  const selectedTaskId = requestedTaskId ?? task?.id;
  const selectionLoading = loading || !snapshot;
  const current = snapshot?.devices.find(device => device.id === task?.current_device_id);
  const origin = snapshot?.devices.find(device => device.id === task?.origin_device_id);
  const deviceName = (id: string | null) => snapshot?.devices.find(device => device.id === id)?.name ?? "—";
  const currentIndex = current ? ORDER.indexOf(current.type) : -1;
  const nextDevice = snapshot?.devices.find(device => device.type === ORDER[currentIndex + 1]);
  const offline = !online || error?.code === "BACKEND_OFFLINE" || error?.code === "DATABASE_UNAVAILABLE";
  const disabled = busy || selectionLoading || offline || !!error;
  const suffix = selectedTaskId ? `?task=${selectedTaskId}` : "";

  function selectTask(id: string, href: string) {
    // Invalidate old handlers/requests synchronously, before router navigation.
    invalidateSelection(id);
    setSelection({ routeId: taskId, requestedId: id });
    setNotice("");
    setError(null);
    router.push(href);
  }

  function ownsSelection(owner: { id: string | undefined; version: number }) {
    return mounted.current && owner.id === selectionOwner.current.id && owner.version === selectionOwner.current.version;
  }

  function canRunIntelligence() {
    return !disabled && !!task && task.id === selectedTaskId
      && selectionOwner.current.id === requestedTaskId && mounted.current;
  }

  function closeCreate() {
    if (busy) return;
    setShowCreate(false);
    createButtonRef.current?.focus();
  }

  async function createTask(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const desktop = snapshot?.devices.find(device => device.type === "DESKTOP");
    if (!desktop || disabled || mutationPending.current || selectionOwner.current.id !== requestedTaskId) return;
    const owner = selectionOwner.current;
    mutationPending.current = true;
    setBusy(true);
    setNotice("");
    try {
      const created = await api<Task>("/tasks", { method: "POST", body: JSON.stringify({
        title, description, origin_device_id: desktop.id,
      }) });
      if (!ownsSelection(owner)) return;
      setShowCreate(false);
      createButtonRef.current?.focus();
      selectTask(created.id, `/?task=${created.id}`);
      setNotice("Task created on Desktop. Persistent state is ready to continue.");
    } catch (cause) { if (ownsSelection(owner)) setError(asError(cause)); }
    finally { mutationPending.current = false; setBusy(false); }
  }

  async function sendHandoff(payload: Handoff, replay = false) {
    const owner = selectionOwner.current;
    // Defense at the mutation boundary: never derive a POST target from stale data.
    if (disabled || mutationPending.current || !task || !selectedTaskId
      || task.id !== selectedTaskId || owner.id !== requestedTaskId || !ownsSelection(owner)) return;
    const targetTaskId = selectedTaskId;
    mutationPending.current = true;
    setBusy(true);
    setNotice("");
    try {
      const result = await api<HandoffResult>(`/tasks/${targetTaskId}/handoff`, {
        method: "POST", body: JSON.stringify(payload),
      });
      if (!replay) {
        try { localStorage.removeItem(`nova.handoff.${targetTaskId}.${payload.source_device_id}`); } catch { /* Storage is optional. */ }
      }
      if (!ownsSelection(owner)) return;
      if (!requestedTaskId) selectTask(targetTaskId, `${view === "continuity" ? "/continuity" : "/"}?task=${targetTaskId}`);
      setNotice(result.replayed
        ? "Original handoff acknowledged. No duplicate event or transition was created."
        : `Task continued on ${deviceName(result.task.current_device_id)}. Same task ID.`);
      if (requestedTaskId) await load();
    } catch (cause) {
      if (ownsSelection(owner)) setError(asError(cause));
    } finally { mutationPending.current = false; setBusy(false); }
  }

  function continueTask() {
    if (disabled || !task || !current || !nextDevice) return;
    const storageKey = `nova.handoff.${task.id}.${current.id}`;
    let key = crypto.randomUUID();
    // Store only request intent, never task state. Reuse after an uncertain response.
    try {
      key = localStorage.getItem(storageKey) ?? key;
      localStorage.setItem(storageKey, key);
    } catch { /* The API still enforces idempotency without browser storage. */ }
    void sendHandoff({ source_device_id: current.id, target_device_id: nextDevice.id, idempotency_key: key });
  }

  const continuity = (
    <section className="panel continuity-panel">
      <div className="panel-heading"><div><span className="eyebrow">CONTINUITY PROTOCOL</span><h2>One task. Every context.</h2></div><span className="tag">SIMULATED DEVICES</span></div>
      <div className="device-path" aria-label="Desktop to Wearable to Mobile continuity">
        {ORDER.map((type, index) => {
          const Icon = ICONS[type];
          const active = current?.type === type;
          const passed = index < currentIndex;
          return <div className="device-step" key={type}>
            <div className={`device-node ${active ? "current" : ""} ${passed ? "passed" : ""}`}>
              <span className="device-index">0{index + 1}</span>
              <Icon size={32} strokeWidth={1.3} />
              <h3>{type[0] + type.slice(1).toLowerCase()}</h3>
              <span className="mono node-status">{active ? "CURRENT CONTEXT" : passed ? "HANDED OFF" : "AWAITING HANDOFF"}</span>
              {active && <span className="node-check"><CircleDot size={14} /> Owns this task</span>}
              {passed && <span className="node-check muted"><Check size={14} /> Previous context</span>}
            </div>
            {index < 2 && <div className={`connector ${passed ? "passed" : ""}`}><ArrowRight size={18} /></div>}
          </div>;
        })}
      </div>
      <div className="handoff-bar"><div><span className="mono">{currentIndex === 2 ? "CONTINUITY PATH COMPLETE" : "READY TO CONTINUE"}</span><p>{currentIndex === 2 ? "The task remains active on Mobile. Its identity and history are preserved." : "Move the context forward. Keep the task and its history."}</p></div>
        {nextDevice ? <button className="button primary" onClick={continueTask} disabled={disabled}>{busy ? <LoaderCircle size={16} className="spin" /> : <ArrowUpRight size={16} />}Continue on {nextDevice.name}</button> : <span className="complete-tag"><Check size={15} /> On Mobile</span>}
      </div>
    </section>
  );

  const eventHistory = (full: boolean) => (
    <section className="panel history-panel">
      <div className="panel-heading"><div><span className="eyebrow">PERSISTENT EVENT LOG</span><h2>{full ? "Event history" : "Selected task activity"}</h2></div><span className="mono muted">{snapshot?.events.length ?? 0} EVENTS</span></div>
      <ol className="timeline">{[...(snapshot?.events ?? [])].reverse().map(event => <li key={event.id}>
        <span className="timeline-dot">{event.event_type === "TASK_CREATED" ? <Plus size={13} /> : <ArrowDownLeft size={13} />}</span>
        <div className="event-content"><strong>{eventLabel(event.event_type)}</strong><span className="mono event-code">{event.event_type}</span><time dateTime={event.created_at}>{timestamp(event.created_at)}</time>
          {full && <dl className="event-data"><dt>EVENT ID</dt><dd>{event.id}</dd><dt>SEQUENCE</dt><dd>{event.sequence}</dd><dt>FROM → TO</dt><dd>{deviceName(event.source_device_id)} → {deviceName(event.target_device_id)}</dd>{event.idempotency_key && <><dt>IDEMPOTENCY KEY</dt><dd>{event.idempotency_key}</dd></>}</dl>}
        </div>
        {full && event.idempotency_key && event.source_device_id && <button className="button ghost small" disabled={disabled} onClick={() => void sendHandoff({ source_device_id: event.source_device_id!, target_device_id: event.target_device_id, idempotency_key: event.idempotency_key! }, true)} aria-label={`Retry ${eventLabel(event.event_type)}`}><RefreshCw size={13} /> Retry original</button>}
      </li>)}</ol>
      {!full && task && <Link className="panel-footer-link" href={`/tasks/${task.id}`}>Inspect full task history<ArrowUpRight size={14} /></Link>}
    </section>
  );

  return <div className="app-shell">
    <aside className="sidebar">
      <Link className="brand" href="/" aria-label="NOVA home"><span className="brand-symbol"><Layers3 size={23} /></span>NOVA<span className="brand-core">CORE</span></Link>
      <div className="workspace-label mono">LOCAL WORKSPACE <span>01</span></div>
      <nav aria-label="Primary navigation">
        <Link className={`nav-item ${view === "command" ? "active" : ""}`} href={`/${suffix}`}><Command size={17} />Command center{view === "command" && <span className="nav-dot" />}</Link>
        <Link className={`nav-item ${view === "continuity" ? "active" : ""}`} href={`/continuity${suffix}`}><Radio size={17} />Device continuity{view === "continuity" && <span className="nav-dot" />}</Link>
        <Link className={`nav-item ${view === "intelligence" ? "active" : ""}`} href={`/intelligence${suffix}`}><Cpu size={17} />NOVA Intelligence{view === "intelligence" && <span className="nav-dot" />}</Link>
        <Link className={`nav-item ${view === "approvals" ? "active" : ""}`} href={`/approvals${suffix}`}><Check size={17} />Approval Center</Link>
        <Link className={`nav-item ${view === "models" ? "active" : ""}`} href={`/models${suffix}`}><Layers3 size={17} />Model Router</Link>
        {task ? <Link className={`nav-item ${view === "detail" ? "active" : ""}`} href={`/tasks/${task.id}`}><FileText size={17} />Task detail{view === "detail" && <span className="nav-dot" />}</Link> : <span className="nav-item disabled"><FileText size={17} />Task detail</span>}
      </nav>
      <div className="sidebar-section"><span className="eyebrow">DEVICE CONTEXTS</span>{ORDER.map(type => { const Icon = ICONS[type]; return <div className="context-item" key={type}><Icon size={15} /><span>{type[0] + type.slice(1).toLowerCase()}</span><span className="mono">SIM</span></div>; })}</div>
      <div className="sidebar-bottom"><div className="local-indicator"><span className="status-dot" />Local-first foundation</div><p>Real persistence.<br />Simulated device contexts.</p><span className="mono version">PHASE 04 / MODEL INTELLIGENCE</span></div>
    </aside>

    <main className="main">
      <header className="topbar"><div className="breadcrumb"><span>NOVA</span><ChevronRight size={13} /><span>{TITLES[view]}</span></div><div className={`connection mono ${offline ? "offline" : ""}`}><span className="status-dot" />{offline ? "OFFLINE" : error ? "ERROR" : selectionLoading ? "CONNECTING" : "BACKEND CONNECTED"}</div></header>
      <div className="main-content">
        <div className="page-heading"><div><div className="eyebrow"><span className="small-line" />NOVA CORE / PHASE 04</div><h1>{TITLES[view]}<span className="accent">.</span></h1><p>{view === "command" ? "Your tasks keep their context. Wherever you continue." : view === "continuity" ? "A continuous thread across three simulated device contexts." : view === "intelligence" ? "A visible execution graph. Explicit evidence. One continuous task." : "One persistent identity. A complete record of every transition."}</p></div>
          <button ref={createButtonRef} className="button primary" disabled={disabled} onClick={() => { setTitle(DEMO_TITLE); setShowCreate(true); }}><Plus size={16} />New task</button>
        </div>

        <div className="phase-notice"><Cpu size={15} /><span>Simulated device contexts · Live backend state · Local PostgreSQL</span><span className="mono">FIXTURE DEFAULT / OPTIONAL LOCAL</span></div>

        {notice && <div className="success-notice" role="status"><Check size={16} />{notice}<button onClick={() => setNotice("")} aria-label="Dismiss notice"><X size={14} /></button></div>}
        {error || !online ? <div className="error-notice" role="alert" aria-label="NOVA error"><WifiOff size={20} /><div><strong>{offline ? "Local services are offline" : "Request failed"}</strong><p>{!online ? "Your browser is offline. Reconnect to load persistent task state." : error?.message}</p>{snapshot && <p>Showing the last loaded data. Refresh before continuing.</p>}{error?.correlationId && <span className="mono">REQUEST {error.correlationId}</span>}</div><button className="button ghost small" onClick={() => void load()} disabled={busy}><RefreshCw size={14} />Retry connection</button></div> : null}

        {view !== "detail" && !!loadedSnapshot?.tasks.length && <section className="panel task-selector-panel"><div className="panel-heading"><div><span className="eyebrow">{view === "command" ? "ACTIVE TASKS" : "SELECT A TASK"}</span><h2>{view === "command" ? "Work in progress" : "Task context"}</h2></div><button className="icon-button" onClick={() => void load()} aria-label="Refresh tasks" disabled={busy || selectionLoading}><RefreshCw size={15} /></button></div>
          {view === "command" ? <div className="task-list">{loadedSnapshot.tasks.map(item => <Link key={item.id} className={`task-row ${item.id === selectedTaskId ? "selected" : ""}`} href={`/?task=${item.id}`} onClick={event => { if (!event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey) { event.preventDefault(); selectTask(item.id, `/?task=${item.id}`); } }}><span className="task-symbol"><FileText size={18} /></span><div><strong>{item.title}</strong><span className="mono">{item.id.slice(0, 8)} · {loadedSnapshot.devices.find(device => device.id === item.current_device_id)?.name ?? "—"}</span></div><span className="status-tag"><span />{item.status}</span><ChevronRight size={16} /></Link>)}</div>
            : <div className="task-select"><label className="sr-only" htmlFor="task-select">Select task</label><select id="task-select" value={selectedTaskId ?? ""} onChange={event => selectTask(event.target.value, `/${view === "intelligence" ? "intelligence" : view === "approvals" ? "approvals" : view === "models" ? "models" : "continuity"}?task=${event.target.value}`)}>{loadedSnapshot.tasks.map(item => <option key={item.id} value={item.id}>{item.title}</option>)}</select><span className="mono muted">ID {selectedTaskId}</span></div>}
        </section>}

        {selectionLoading && !snapshot && !error ? <div className="loading-state" role="status"><LoaderCircle size={24} className="spin" /><h2>{requestedTaskId ? "Loading selected task" : "Loading persistent state"}</h2><p>{requestedTaskId ? "Task actions are unavailable until this selection is confirmed." : "Connecting to your local NOVA backend…"}</p></div>
          : !snapshot ? <div className="empty-state"><WifiOff size={32} /><h2>{offline ? "Waiting for your local backend" : "No task data available"}</h2><p>{offline ? "Start the local services, then retry the connection." : "Open the command center to select an existing task."}</p>{!offline && <Link className="button ghost" href="/">Open command center</Link>}</div>
          : !task ? <div className="empty-state"><span className="empty-icon"><Layers3 size={32} /></span><span className="eyebrow">YOUR FIRST CONTINUOUS TASK</span><h2>Start here. Continue anywhere.</h2><p>Create the dinner planning task on Desktop, then hand it off to Wearable and Mobile. Every step is stored in your local database.</p><button className="button primary" disabled={disabled} onClick={() => setShowCreate(true)}><Plus size={16} />Create demonstration task</button><div className="empty-path mono">DESKTOP <ArrowRight size={14} /> WEARABLE <ArrowRight size={14} /> MOBILE</div></div>
          : <>
            <div className="stats-grid"><div className="stat"><span className="eyebrow">LOADED ACTIVE TASKS</span><span className="stat-value">{snapshot.tasks.length.toString().padStart(2, "0")}<Layers3 size={18} /></span><span className="stat-note">Persistent in PostgreSQL · up to 100</span></div><div className="stat"><span className="eyebrow">CURRENT CONTEXT</span><span className="stat-value">{current?.name}{current && (() => { const Icon = ICONS[current.type]; return <Icon size={20} />; })()}</span><span className="stat-note">Selected task’s device</span></div><div className="stat"><span className="eyebrow">RECORDED HANDOFFS</span><span className="stat-value">{snapshot.events.filter(event => event.idempotency_key).length.toString().padStart(2, "0")}<Radio size={19} /></span><span className="stat-note">Selected task · unique transitions</span></div></div>

            {view === "detail" && <section className="panel detail-panel"><div className="panel-heading"><span className="eyebrow">PERSISTENT TASK RECORD</span><span className="status-tag"><span />{task.status}</span></div><h2>{task.title}</h2><p>{task.description || "No description provided."}</p><dl className="task-data"><div className="wide"><dt>TASK ID</dt><dd data-testid="task-id">{task.id}</dd></div><div><dt>ORIGIN DEVICE</dt><dd>{origin?.name}</dd></div><div><dt>CURRENT DEVICE</dt><dd data-testid="current-device">{current?.name}</dd></div><div><dt>CREATED</dt><dd>{timestamp(task.created_at)}</dd></div><div><dt>UPDATED</dt><dd>{timestamp(task.updated_at)}</dd></div></dl></section>}

            {(view === "command" || view === "models") && <ModelWorkspace key={`models-${task.id}`} task={task} canMutate={canRunIntelligence} disabled={disabled} compact={view === "command"} />}
            {(view === "command" || view === "approvals" || view === "detail") && <ApprovalWorkspace key={`actions-${task.id}`} task={task} canMutate={canRunIntelligence} disabled={disabled} compact={view === "command"} />}
            {(view === "intelligence" || view === "detail") && <IntelligenceWorkspace key={task.id} task={task} canMutate={canRunIntelligence} disabled={disabled} />}
            {view === "command" ? <div className="dashboard-grid">{continuity}{eventHistory(false)}</div> : <>{continuity}{eventHistory(true)}</>}
            <div className="identity-strip"><span className="status-dot" /><span className="mono">TASK ID</span><code data-testid="identity-id">{task.id}</code><span className="identity-note">Identity preserved through every handoff</span></div>
          </>}

        <footer className="footer"><span className="mono">NOVA / CROSS-DEVICE CONTINUITY</span><span>Simulated context and devices. Explicit routing and human approval.</span></footer>
      </div>
    </main>

    {showCreate && <div className="modal-overlay" onClick={closeCreate}><section className="modal" role="dialog" aria-modal="true" aria-labelledby="create-title" onClick={event => event.stopPropagation()} onKeyDown={event => {
      if (event.key === "Escape") closeCreate();
      if (event.key === "Tab") {
        const focusable = Array.from(event.currentTarget.querySelectorAll<HTMLElement>("button:not(:disabled), textarea, input"));
        const first = focusable[0], last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
      }
    }}><div className="panel-heading"><span className="eyebrow">ORIGIN / DESKTOP</span><button className="icon-button" onClick={closeCreate} disabled={busy} aria-label="Close new task"><X size={18} /></button></div><h2 id="create-title">Create a continuous task.</h2><p>Saved to PostgreSQL with a TASK_CREATED event. Continue it on the next device when you’re ready.</p><form onSubmit={createTask}><label htmlFor="new-title">TASK TITLE</label><textarea ref={titleRef} id="new-title" required maxLength={240} value={title} onChange={event => setTitle(event.target.value)} rows={3} /><label htmlFor="new-description">DESCRIPTION</label><textarea id="new-description" maxLength={10000} value={description} onChange={event => setDescription(event.target.value)} rows={3} />{error && <p className="form-error" role="alert">{error.message}</p>}<div className="modal-actions"><button type="button" className="button ghost" onClick={closeCreate} disabled={busy}>Cancel</button><button className="button primary" disabled={disabled || !title.trim()}>{busy ? <LoaderCircle size={16} className="spin" /> : <Plus size={16} />}Create task on Desktop</button></div></form></section></div>}
  </div>;
}
