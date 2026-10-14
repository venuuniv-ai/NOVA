export type Situation = {
  current_time: string; minutes_available: number; travel_minutes: number; lateness_minutes: number; arrival_at: string;
  meeting: { title: string; starts_at: string; location: string }; source: "DEMO_FIXTURE";
};
export type Proposal = {
  id: string; task_id: string; trace_id: string; trigger_id: string; status: string;
  recipient: string; content: string; reason: string; payload_hash: string;
  policy_decision: string; policy_version: string; expires_at: string; supersedes_id: string | null; situation: Situation;
};
export type ProposalDetail = { proposal: Proposal; approval: { id: string; payload_hash: string; expires_at: string } | null;
  execution: { id: string; status: string; receipt: { disclosure: string; external_message_sent: boolean } } | null };
export type Trigger = { id: string; trace_id: string; status: string; reason: string; situation: Situation;
  agent_record: { agent: string; status: string; tool_calls: unknown[] } | null };
export type Audit = { id: string; event_type: string; proposal_id: string | null; trace_id: string; created_at: string };
