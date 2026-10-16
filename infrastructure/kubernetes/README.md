# Local kind deployment target

Compose with compose.phase8.yaml is the complete local Kafka/observability runtime.
This Kubernetes target declares the authenticated application, persistent PostgreSQL/Redis/media/key volumes, Kafka/outbox workers and local observability. It does not install an OIDC provider/operator/chart. Compose provides the separately enabled local Keycloak profile. Kubernetes full-stack rollout remains subject to the executed evidence and limitations in the Phase 8 audit.

Use an isolated local `kind-nova` context only. Do not point these commands at cloud:

```sh
kind create cluster --name nova
kind load docker-image --name nova nova-backend:latest nova-frontend:latest nova-gateway:local nova-postgres-vector:local
docker pull redis:7-alpine
kind load docker-image --name nova redis:7-alpine
kubectl --context kind-nova apply -f infrastructure/kubernetes/namespace.yaml
# Operator supplies a fresh password; do not commit the resulting Secret.
kubectl --context kind-nova -n nova create secret generic nova-db --from-literal=password="$NOVA_LOCAL_DB_PASSWORD"
kubectl --context kind-nova apply -k infrastructure/kubernetes
kubectl --context kind-nova -n nova rollout status deployment/backend --timeout=180s
kubectl --context kind-nova -n nova port-forward service/frontend 3000:3000
```

No credential is included in manifests. Secrets are Kubernetes Secrets, not an
external vault or encryption-at-rest guarantee. The signing key is initialized
privately on the backend PVC. Provision identities with the same operator CLI as
Compose. Never expose replay/demo mode publicly.

Default-deny and allowed application edges require a NetworkPolicy-enforcing CNI;
kind's default CNI alone is not proof of enforcement. Restricted pod policy,
non-root containers, dropped capabilities and disabled service-account mounts
are declared. Local PVCs are not a backup or multi-zone storage design. The single
backend replica preserves the existing single-process recovery assumptions.
