import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

async function forward(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  // Keep the gateway bounded to the actual API; never proxy arbitrary hosts/paths.
  if (path[0] !== "v1") {
    return Response.json({ error: { code: "NOT_FOUND", message: "Unknown API path." } }, { status: 404 });
  }
  const base = process.env.API_INTERNAL_URL ?? "http://localhost:8000";
  const url = `${base}/api/${path.map(encodeURIComponent).join("/")}${request.nextUrl.search}`;
  const correlationId = request.headers.get("X-Correlation-ID") ?? crypto.randomUUID();
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);
  try {
    const contentType = request.headers.get("Content-Type") ?? "application/json";
    const binary = contentType.startsWith("image/");
    let body: Uint8Array | undefined;
    if (request.method === "POST") {
      const stream = request.body?.getReader(); const chunks: Uint8Array[] = []; let size = 0;
      if (stream) while (true) {
        const part = await stream.read(); if (part.done) break;
        size += part.value.length;
        if (size > (binary ? 2_000_000 : 1_000_000)) { await stream.cancel(); return Response.json({ error: { code: "REQUEST_SIZE_LIMIT", message: "Request exceeds gateway limit." } }, { status: 413 }); }
        chunks.push(part.value);
      }
      body = new Uint8Array(size); let offset = 0;
      for (const chunk of chunks) { body.set(chunk, offset); offset += chunk.length; }
    }
    const response = await fetch(url, {
      method: request.method,
      headers: { "Content-Type": contentType, "X-Correlation-ID": correlationId, ...(request.headers.get("Idempotency-Key") ? { "Idempotency-Key": request.headers.get("Idempotency-Key")! } : {}) },
      body: body as BodyInit | undefined,
      cache: "no-store",
      signal: controller.signal,
      redirect: "error",
    });
    return new Response(await response.arrayBuffer(), {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("Content-Type") ?? "application/json",
        "X-Content-Type-Options": "nosniff",
        "Cache-Control": "no-store",
        "X-Correlation-ID": response.headers.get("X-Correlation-ID") ?? correlationId,
        ...(response.headers.get("X-Trace-ID") ? { "X-Trace-ID": response.headers.get("X-Trace-ID")! } : {}),
      },
    });
  } catch {
    return Response.json({
      error: { code: "BACKEND_OFFLINE", message: "The NOVA backend is unreachable. Check your local services." },
      correlation_id: correlationId,
    }, { status: 503, headers: { "X-Correlation-ID": correlationId } });
  } finally {
    clearTimeout(timeout);
  }
}

export const GET = forward;
export const POST = forward;
