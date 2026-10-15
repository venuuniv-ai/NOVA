"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { api, type Task } from "@/lib/api";
import type { Memory, MemoryHit, Retrieval } from "@/lib/memory";

type Intent = { path:string; method:string; payload:Record<string,unknown> };
type Audit = { id:string; event_type:string; created_at:string; safe_metadata:{status:string;origin:string} };

export default function MemoryWorkspace({task,disabled,canMutate,isCurrentTask,compact=false}:{task:Task;disabled:boolean;canMutate:()=>boolean;isCurrentTask?:()=>boolean;compact?:boolean}) {
  const [records,setRecords]=useState<Memory[]>([]),[retrieval,setRetrieval]=useState<Retrieval|null>(null),[ready,setReady]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState("");
  const [value,setValue]=useState("quiet Italian restaurants"),[query,setQuery]=useState("Where should Sarah and I eat?"),[history,setHistory]=useState<Audit[]>([]),[historyId,setHistoryId]=useState("");
  const [used,setUsed]=useState<MemoryHit[]>([]);
  const [editing,setEditing]=useState<Memory|null>(null),[editValue,setEditValue]=useState(""),[intent,setIntent]=useState<Intent|null>(null);
  const alive=useRef(false),posting=useRef(false),generation=useRef(0),reader=useRef<AbortController|null>(null),owner=useRef(canMutate);
  useEffect(()=>{owner.current=canMutate;},[canMutate]);
  const selection = useRef(isCurrentTask ?? canMutate);
  useEffect(() => { selection.current = isCurrentTask ?? canMutate; }, [isCurrentTask, canMutate]);
  const storage=`nova.memory-intent.${task.id}`;
  const load=useCallback(async()=>{
    const version=++generation.current;reader.current?.abort();const controller=new AbortController();reader.current=controller;
    try {
      const [memories,context,plan]=await Promise.all([api<Memory[]>("/memory",{signal:controller.signal}),api<Retrieval>(`/tasks/${task.id}/memory`,{signal:controller.signal}),api<{context:{memory_hits:MemoryHit[]}|null}>(`/tasks/${task.id}/plan`,{signal:controller.signal})]);
      if(!alive.current||controller.signal.aborted||version!==generation.current)return;
      if(context.hits.some(h=>h.memory.scope==="TASK"&&h.memory.task_id!==task.id))throw new Error("Memory context ownership mismatch.");
      setRecords(memories);setRetrieval(context);setUsed(plan.context?.memory_hits??[]);setReady(true);setError("");
    }catch(cause){if(alive.current&&!controller.signal.aborted&&version===generation.current)setError(cause instanceof Error?cause.message:"Memory is unavailable.");}
  },[task.id]);
  useEffect(()=>{
    alive.current=true;const lifecycle=alive,reads=reader,versions=generation;
    const timer=setTimeout(()=>{try{const pending=localStorage.getItem(storage);if(pending)setIntent(JSON.parse(pending) as Intent);}catch{/* Optional mutation intent. */}void load();},0);
    const poll=setInterval(()=>{if(!document.hidden)void load();},15000);
    return()=>{lifecycle.current=false;++versions.current;reads.current?.abort();clearTimeout(timer);clearInterval(poll);};
  },[load,storage]);
  async function mutate(request:Intent|(()=>Promise<Intent>)){
    if(posting.current||disabled||!owner.current()||!alive.current)return;
    posting.current=true;setBusy(true);
    try{
      const next=typeof request==="function"?await request():request;
      if(!alive.current||!selection.current()||!owner.current())return;
      setIntent(next);try{localStorage.setItem(storage,JSON.stringify(next));}catch{/* Optional intent. */}
      await api(next.path,{method:next.method,body:JSON.stringify(next.payload)});
      if(!alive.current||!selection.current())return;
      setIntent(null);setEditing(current=>current&&next.path.includes(current.id)?null:current);try{localStorage.removeItem(storage);}catch{/* Optional intent. */}await load();
    }catch(cause){if(alive.current&&selection.current())setError(cause instanceof Error?cause.message:"Memory mutation was not confirmed.");}
    finally{posting.current=false;if(alive.current)setBusy(false);}
  }
  function change(path:string,payload:Record<string,unknown>={},method="POST"){return mutate({path,method,payload:{...payload,idempotency_key:crypto.randomUUID()}});}
  async function search(){
    if(!owner.current()||posting.current)return;posting.current=true;setBusy(true);
    try{const result=await api<Retrieval>("/memory/search",{method:"POST",body:JSON.stringify({task_id:task.id,query,limit:10})});if(alive.current&&selection.current())setRetrieval(result);}
    catch(cause){if(alive.current&&selection.current())setError(cause instanceof Error?cause.message:"Retrieval failed.");}
    finally{posting.current=false;if(alive.current)setBusy(false);}
  }
  async function viewHistory(memory:Memory){
    const results=await api<Audit[]>(`/memory/${memory.id}/history`);if(alive.current&&selection.current()){setHistory(results);setHistoryId(memory.id);}
  }
  async function visualCandidate(){
    await mutate(async()=>{
      const runs=await api<{task_id:string;observations:{id:string;label:string}[]}[]>(`/tasks/${task.id}/perception`);
      const observation=runs.filter(r=>r.task_id===task.id).flatMap(r=>r.observations).find(o=>o.label==="coffee_cup_present");
      if(!observation)throw new Error("Run the controlled wearable perception scene first.");
      return {path:"/memory/candidates/visual",method:"POST",payload:{task_id:task.id,observation_id:observation.id,idempotency_key:crypto.randomUUID()}};
    });
  }

  const blocked=disabled||busy||!ready,visible=records.filter(m=>m.scope==="USER"||m.task_id===task.id),pending=visible.filter(m=>m.status==="PENDING_CONFIRMATION");
  return <section className="panel memory-workspace" data-testid="memory-workspace" data-task-id={task.id}>
    <div className="panel-heading"><div><span className="eyebrow">PERSISTENT MEMORY / USER CONTROL</span><h2>{compact?"Memory context":"Memory Center"}</h2></div><span className="tag">{retrieval?.disclosure??"LOADING MEMORY"}</span></div>
    {error&&<div className="error-notice" role="alert" aria-label="Memory error"><p>{error}</p><button className="button ghost" onClick={()=>void load()}>Reload memory</button></div>}
    {!ready?<p role="status">Loading owned memory and task context…</p>:compact?<div><p>Active preferences: {visible.filter(m=>m.status==="ACTIVE"&&m.memory_type==="PREFERENCE").length} · Pending confirmation: {pending.length}</p><p>Last retrieved: {retrieval?.hits.map(h=>`${h.memory.subject} → ${h.memory.value} (${h.memory.origin})`).join("; ")||"No eligible memory"}</p><p>Recorded plan memory (historical snapshot): {used.map(h=>`${h.memory.value} / ${h.memory.origin} / ${h.memory_id} / ${h.retrieval_sources.join("+")}`).join("; ")||"No memory used by a recorded plan."}</p><Link className="button ghost" href={`/memory?task=${task.id}`}>Open Memory Center</Link></div>:<>
      <p className="memory-disclosure">Memory is user-controlled evidence, never instructions or authority. Fixture embeddings test vector/ranking infrastructure, NOT REAL SEMANTIC QUALITY. Unconfirmed candidates are excluded from planning. No cloud embeddings are enabled.</p>
      <div className="memory-counts">{["ACTIVE","PENDING_CONFIRMATION","EXPIRED","SUPERSEDED","DELETED","REJECTED"].map(status=><span key={status}>{status}<b>{visible.filter(m=>m.status===status).length}</b></span>)}</div>
      <form className="memory-controls" onSubmit={event=>{event.preventDefault();void change("/memory",{value,subject:"demo_user",predicate:"dining_preference",memory_type:"PREFERENCE",scope:"USER"});}}><label>Explicit preference<input aria-label="Explicit preference" value={value} maxLength={500} disabled={blocked||!!intent} onChange={event=>setValue(event.target.value)}/></label><button className="button primary" disabled={blocked||!!intent||!value.trim()}>Remember preference</button><button type="button" className="button ghost" disabled={blocked||!!intent} onClick={()=>void visualCandidate()}>Create visual candidate</button></form>
      {intent&&<button className="button ghost" disabled={blocked} onClick={()=>void mutate(intent)}>Retry original memory request</button>}
      <span className="eyebrow">WHAT NOVA REMEMBERS / LIFECYCLE</span>
      <div className="memory-grid">{visible.map(memory=><article className="memory-card" key={memory.id} data-memory-id={memory.id}>
        <span className="eyebrow">{memory.origin} / {memory.explicitness}{memory.confirmed?" — CONFIRMED":""}</span><h3>{memory.value}</h3><p>{memory.subject} · {memory.predicate} · {memory.memory_type}</p><p>{memory.status} / {memory.scope} / {memory.privacy_class}</p><p>Inference confidence: {memory.confidence??"NOT A MODEL PROBABILITY"}</p><code>ID {memory.id}<br/>SOURCE {memory.source_reference}</code><p>Valid: {memory.valid_from??"no start bound"} → {memory.valid_until??"no end bound"}</p>{memory.supersedes_id&&<p>Supersedes {memory.supersedes_id}</p>}
        <div className="memory-actions">{memory.status==="ACTIVE"&&<><button className="button ghost" disabled={blocked} onClick={()=>{setEditing(memory);setEditValue(memory.value);}}>Correct</button><button className="button ghost" disabled={blocked} onClick={()=>void change(`/memory/${memory.id}`,{},"DELETE")}>Delete</button></>}{memory.status==="PENDING_CONFIRMATION"&&<><button className="button primary" disabled={blocked} onClick={()=>void change(`/memory/candidates/${memory.id}/confirm`)}>Confirm</button><button className="button ghost" disabled={blocked} onClick={()=>{setEditing(memory);setEditValue(memory.value);}}>Edit & confirm</button><button className="button ghost" disabled={blocked} onClick={()=>void change(`/memory/candidates/${memory.id}/reject`)}>Reject</button></>}<button className="button ghost" disabled={blocked} onClick={()=>void viewHistory(memory)}>History</button></div>
      </article>)}</div>
      {editing&&<form className="memory-edit" onSubmit={event=>{event.preventDefault();void change(editing.status==="ACTIVE"?`/memory/${editing.id}/correct`:`/memory/candidates/${editing.id}/confirm`,editing.status==="ACTIVE"?{value:editValue}:{edited_value:editValue});}}><label>Corrected memory<input aria-label="Corrected memory" value={editValue} maxLength={500} onChange={event=>setEditValue(event.target.value)}/></label><button className="button primary" disabled={blocked}>Save correction</button><button type="button" className="button ghost" onClick={()=>setEditing(null)}>Cancel</button></form>}
      {historyId&&<div className="memory-history"><span className="eyebrow">AUDIT HISTORY / {historyId}</span>{history.map(event=><p key={event.id}>{event.event_type} · {event.safe_metadata.status} · {event.created_at}</p>)}</div>}
      <div className="retrieval-explorer"><span className="eyebrow">RETRIEVAL EXPLORER / RRF K=60</span><label>Memory query<input aria-label="Memory query" value={query} maxLength={500} onChange={event=>setQuery(event.target.value)}/></label><button className="button primary" disabled={blocked} onClick={()=>void search()}>Search memory</button><p>{retrieval?.disclosure}</p>{retrieval?.hits.map(hit=><article key={hit.memory_id} className="memory-hit"><h3>{hit.memory.value}</h3><p>{hit.memory.origin} / {hit.memory.scope} / {hit.memory.status}</p><p>{hit.reason_codes.join(" / ")}</p><p>Ranks: structured {hit.structured_rank??"—"} · lexical {hit.lexical_rank??"—"} · semantic {hit.semantic_rank??"—"} · fused {hit.fused_rank}</p><p>{hit.embedding_simulation?"Fixture vector similarity (no semantic quality claim)":"Local cosine similarity"}: {hit.semantic_similarity??"not used"}</p><code>MEMORY {hit.memory_id} · {hit.embedding_provider}/{hit.embedding_model}</code></article>)}</div>
    </>}
  </section>;
}
