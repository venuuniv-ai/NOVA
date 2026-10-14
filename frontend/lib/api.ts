export type DeviceType = "DESKTOP" | "WEARABLE" | "MOBILE";
export type Device = { id: string; user_id: string; name: string; type: DeviceType; created_at: string };
export type Task = {
  id: string; user_id: string; title: string; description: string;
  origin_device_id: string; current_device_id: string; status: "ACTIVE";
  created_at: string; updated_at: string;
};
export type TaskEvent = {
  id: string; task_id: string; event_type: string; source_device_id: string | null;
  target_device_id: string; idempotency_key: string | null; metadata: Record<string, unknown>;
  sequence: number; created_at: string;
};
export type Handoff = { source_device_id: string; target_device_id: string; idempotency_key: string };
export type HandoffResult = { task: Task; event: TaskEvent; replayed: boolean };

export class ApiError extends Error {
  constructor(message: string, public code: string, public correlationId?: string) {
    super(message);
  }
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const timeout = new AbortController();
  const timer = setTimeout(() => timeout.abort(), 12000);
  try {
    const response = await fetch(`/api/v1${path}`, {
      ...options,
      headers: { "Content-Type": "application/json", "X-Correlation-ID": crypto.randomUUID(), ...options.headers },
      cache: "no-store",
      signal: options.signal ?? timeout.signal,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new ApiError(data.error?.message ?? "Request failed.", data.error?.code ?? "REQUEST_FAILED", data.correlation_id);
    }
    return data as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("Unable to reach local services. Reconnect and retry.", "BACKEND_OFFLINE");
  } finally {
    clearTimeout(timer);
  }
}

export const DEMO_TITLE = "Find somewhere for dinner with Sarah tomorrow after my meeting.";
