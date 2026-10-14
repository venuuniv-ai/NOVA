export type Evidence = { fact: string; provenance: { source: "DEMO_FIXTURE"; reference: string; memory_type: string | null }; plugin: string; function: string };
export type Plan = {
  goal: string; assumptions: string[]; constraints: Evidence[];
  steps: { title: string; action: string; requires_approval: boolean }[];
  required_tools: { plugin: string; function: string }[];
  missing_information: string[]; requires_approval: boolean;
};
export type Execution = {
  id: string; task_id: string; trace_id: string; status: "RUNNING" | "DONE" | "FAILED";
  provider: string; model: string; idempotency_key: string;
  started_at: string; completed_at: string | null; error: string | null;
};
export type ToolCall = {
  id: string; agent_run_id: string; trace_id: string; plugin: string; function: string;
  status: "DONE" | "FAILED"; input: Record<string, unknown>; output: Record<string, unknown> | null;
  started_at: string; completed_at: string; error: string | null;
};
export type AgentRun = {
  id: string; task_id: string; execution_id: string; agent_name: string; stage: string;
  status: "WAITING" | "RUNNING" | "DONE" | "FAILED" | "SKIPPED";
  sequence: number; trace_id: string; provider: string; model: string;
  started_at: string | null; completed_at: string | null; summary: string;
  structured_output: Record<string, unknown> | null; evidence: Evidence[];
  warnings: string[]; error: string | null; tool_calls: ToolCall[];
};
export type Intelligence = {
  task_id: string; execution: Execution | null; agent_runs: AgentRun[];
  context: {
    device: { device_type: string; simulated: true } | null;
    location: { description: string; area: string } | null;
    calendar: { title: string; starts_at: string; ends_at: string; location: string; date_label: string }[];
    preferences: { person: string; preference: string; provenance: { source: string; reference: string; memory_type: string } }[];
  } | null;
  plan: Plan | null; critic: { verdict: "PASS" | "REVISION_REQUIRED"; reasons: { code: string; message: string }[] } | null;
};
