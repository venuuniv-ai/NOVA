# ADR 0004: deterministic model routing and privacy eligibility

Status: accepted for Phase 4 local/fixture operation.

NOVA owns routing and classifies request purpose/context with explicit rules.
Models cannot choose provider, privacy, capability, tier, price or authorization.
The InferenceProvider contract normalizes fixture and optional local text JSON
transport; RoutedModelProvider integrates it through the existing kernel service
interface. Agent/native plugin code remains vendor-independent.

Routing considers capabilities, logical complexity, simulated device capacity,
latency preference, availability/circuit, privacy and budget. Every fallback
rechecks policy on an owned request copy. Sensitive-local-only excludes cloud;
personal cloud requires explicit server policy. Fixture reasoning is labeled
limited replay, not a real reasoning provider. Vision is a reserved tier only.

Local endpoints are trusted server configuration, constrained to loopback or
Docker host, with redirects/proxies disabled and bounded time/body sizes.
No request may supply an endpoint or credential. Disabled local operation does
not contact a server or install anything. Cloud transport remains unimplemented;
typed test providers exercise future policy without paid traffic.

A stronger provider never obtains approval/execution capability. Explicit routed
agent/draft paths retain deterministic Critic and Phase 3 policy checks. Defaults
remain fixture-backed. See [Phase 4 architecture](../phase-4-architecture.md).
