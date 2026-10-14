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
    const response = await fetch(url, {
      method: request.method,
      headers: { "Content-Type": "application/json", "X-Correlation-ID": correlationId },
      body: request.method === "POST" ? await request.text() : undefined,
      cache: "no-store",
      signal: controller.signal,
      redirect: "error",
    });
    return new Response(await response.text(), {
      status: response.status,
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "no-store",
        "X-Correlation-ID": response.headers.get("X-Correlation-ID") ?? correlationId,
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
