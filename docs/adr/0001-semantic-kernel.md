# ADR 0001: Semantic Kernel as a bounded capability and provider runtime

Status: accepted for Phase 2. Date: October 14, 2026.

## Context

NOVA needs specialized agents with typed outputs, narrowly scoped tools,
provider independence, and persistent execution evidence. Development must
remain local and require no API keys. An SDK import alone would not demonstrate
an integration, and an unrestricted agent loop would weaken the existing
application trust boundaries.

## Decision

Use Semantic Kernel 1.45.0 in the Python backend for native plugin registration,
function metadata/discovery, controlled invocation with typed KernelArguments,
and resolution of the configured ModelProvider service. Register
CalendarPlugin, MemoryPlugin, ContextPlugin, and FixtureModelProvider in each
execution's KernelRuntime.

All plugin calls pass through `Kernel.get_function` and `Kernel.invoke`; tests
exercise these real SDK paths. FixtureModelProvider extends the SDK's
AIServiceClientBase and NOVA's abstract `generate_structured` contract. Agents
resolve it through `Kernel.get_service`, not a hardwired commercial client.
KernelArguments and invocation metadata carry bounded inputs and the NOVA trace.

NOVA application code owns authorization, selected task identity, transitions,
execution claims, idempotency, database transactions, graph dependencies,
failure/recovery rules, structured-output validation, and deterministic policy.
The kernel receives no database session, filesystem handle, shell runner, or
network client through its plugins. The tool-call persistence callback is owned
by the runtime/orchestrator and is not a plugin capability.

**FixtureModelProvider is deterministic test/demo infrastructure and is NOT
an LLM.** It returns typed fixture output, not generated commercial-model text.
No paid/local model adapter is implemented in Phase 2. A later adapter can
implement the same provider contract and register as a kernel service without
changing agents' call sites; domain contracts/policy remain explicitly versioned.

## Alternatives

- Plain direct Python calls would be cheaper in dependency size but would not
  satisfy meaningful Semantic Kernel responsibility or common discovery/service
  registration.
- Commercial chat-completion agents would add API-key and cost requirements and
  violate the local zero-cost requirement.
- A broker/durable-worker platform would add infrastructure before the short,
  deterministic workflow justifies it. Use synchronous FastAPI worker threads
  with persisted progress and explicit interrupted-run recovery in this phase.

## Consequences

The integration remains reviewable and testable with no paid traffic. Kernel
function discovery and invocation are reused across specialized agents, while
the database remains authoritative. Dependency versions are pinned/constrained;
Pydantic 2.13.5 satisfies the SDK's version bounds.

Semantic Kernel has substantial mandatory dependencies, including OpenAI/Azure
SDKs, numerical libraries, and OpenTelemetry packages. Their installation does
not configure or invoke hosted services. NOVA registers only the fixture
provider and native fixture plugins; there are no model clients, credentials,
telemetry exporters, real calendar integrations, or cloud resources configured.
Tests fail if commercial client/credential constructors or external async HTTP
paths are used. No model files are downloaded.

The current execution runner targets one local application process. It is not
a durable distributed job queue. Long-running real inference or multiple
replicas will require a later explicitly designed lifecycle. That future work
is not implemented here.

This decision follows the official [native-plugin guidance](https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/adding-native-plugins)
and [Python Kernel API](https://learn.microsoft.com/en-us/python/api/semantic-kernel/semantic_kernel.kernel.kernel?view=semantic-kernel-python).
