# NOVA engineering constraints

These cost requirements apply to all work in this repository. Treat cost as
an architectural requirement, not an optional optimization.

## Spending and deployment

- Target development cost: $0 whenever possible.
- Default recurring infrastructure cost: $0.
- Optional, deliberately enabled benchmarking/API spend must stay at or below
  $25 unless the user explicitly approves a higher amount. This ceiling is not
  authorization to spend or to enable paid services.
- Never provision AWS, Azure, or GCP resources without explicit user approval.
- If an implementation decision introduces a paid dependency, stop and report
  it before proceeding.
- Do not automatically download models. Downloads require explicit developer
  action; prefer small, CPU-friendly models. Large GPU models are optional
  benchmark adapters.

## Phase 1

Phase 1 must run entirely locally with zero paid services. Use Next.js,
FastAPI, PostgreSQL, Redis, and Docker Compose. No OpenAI API, Anthropic API,
paid VLM, cloud infrastructure, managed database, managed Redis, or managed
Kafka may be required.

## Local infrastructure

Prefer local/open-source components when technically justified:

- PostgreSQL with pgvector, Redis, and Kafka: local Docker deployments.
- OpenTelemetry, Prometheus, Grafana, and MLflow: local services.
- Kubernetes: kind or k3d.
- Terraform: local formatting, validation, and planning where possible;
  cloud deployment is optional and requires explicit approval.
- DeepEval, XGBoost, scikit-learn, and Semantic Kernel: local/open-source
  execution, using CPU where practical.

Production-quality Terraform, Kubernetes, Kafka, and observability artifacts
may be added as the project develops. Their existence does not require ongoing
deployment. Make the full architecture reproducible locally where practical.
Every infrastructure dependency needs a technical justification; do not add
managed cloud services solely for portfolio keywords.

## Model providers and tests

All AI functionality must use a provider abstraction, designed to support
`ModelProvider`, `FixtureProvider`, `LocalProvider`,
`OpenAICompatibleProvider`, and an optional cloud provider. Do not tightly
couple application code to a commercial model provider.

Development must work without paid API keys. Use deterministic fixtures in
automated tests. Commercial/frontier models are optional. Tests must never
accidentally generate paid API traffic; external model integration tests must
be explicitly enabled, with `ENABLE_EXTERNAL_MODEL_TESTS=false` by default.
Explicit test enablement must also respect spending and deployment approvals.

## Routing and budgets

When implementing model routing, consider quality, latency, privacy, task
complexity, estimated cost, and local availability. Prefer the cheapest model
capable of satisfying the task.

Support configurable budgets such as `DAILY_AI_BUDGET_USD` and
`MAX_REQUEST_COST_USD`. Enforce budgets in deterministic application code,
never through LLM instructions. Default behavior must not incur paid traffic.

## Public demo

Support a live mode using available backend/model services and a demo/replay
mode using deterministic predefined scenarios with no external model API
calls. Clearly label replayed or simulated behavior; never present it as live
model execution. The portfolio demo must not depend on the complete production
architecture remaining online continuously.

## Cost observability

When real model APIs are introduced, record provider, model, input tokens,
output tokens, latency, and estimated cost when pricing is configured.
Pricing must be configuration-driven; never assume hardcoded provider pricing
is permanently accurate. If pricing is unavailable, display `COST UNKNOWN`
rather than inventing a value.

As the project develops, expose cost per task, agent, model, successful task,
and daily accumulated cost.

## CI/CD

Standard CI must not call paid LLM/VLM APIs or run expensive GPU/model
workloads. Run unit tests, deterministic agent tests, fixture-based model
tests, lint, typecheck, build, and security checks as applicable to the codebase.
External AI evaluation requires explicit manual execution and must respect
the spending constraints above.
