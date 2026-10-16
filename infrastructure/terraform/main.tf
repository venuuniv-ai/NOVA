terraform {
  required_version = ">= 1.10, < 2.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.38.0"
    }
  }
}
variable "kubeconfig" {
  type    = string
  default = "~/.kube/config"
}
provider "kubernetes" {
  config_path    = pathexpand(var.kubeconfig)
  config_context = "kind-nova"
}
# Local-cluster namespace only: no cloud provider, account, billable resource or deployment.
resource "kubernetes_namespace_v1" "nova" {
  metadata {
    name = "nova"
    labels = {
      "pod-security.kubernetes.io/enforce" = "restricted"
    }
  }
}
output "namespace" {
  value = kubernetes_namespace_v1.nova.metadata[0].name
}

variable "deploy_local_stack" {
  description = "Explicit opt-in to the local Kubernetes stack; no cloud resources."
  type        = bool
  default     = false
}
locals {
  application = concat(jsondecode(file("${path.module}/../kubernetes/application.yaml")).items, jsondecode(file("${path.module}/../kubernetes/pipeline.yaml")).items)
}
resource "kubernetes_manifest" "application" {
  for_each = {
    for object in local.application : "${object.kind}-${object.metadata.name}" => object
    if var.deploy_local_stack
  }
  manifest = merge(each.value, {
    metadata = merge(each.value.metadata, { namespace = kubernetes_namespace_v1.nova.metadata[0].name })
  })
}
