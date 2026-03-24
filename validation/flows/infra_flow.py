from __future__ import annotations

from validation.core.config import ValidationConfig
from validation.core.reporting import RunRecorder, StepResult
from validation.core.shell import run as run_command


def run(config: ValidationConfig, recorder: RunRecorder) -> None:
    outputs = {
        "kubernetes-pod-inventory.txt": run_command(["kubectl", "get", "pods", "-A", "-o", "wide"], config.root),
        "kubernetes-services.txt": run_command(["kubectl", "get", "svc", "-A"], config.root),
        "kubernetes-ingress.txt": run_command(["kubectl", "get", "ingress", "-A"], config.root),
        "argocd-apps.txt": run_command(["kubectl", "get", "applications", "-A"], config.root),
        "externalsecrets.txt": run_command(["kubectl", "get", "externalsecrets", "-A"], config.root),
    }
    for file_name, payload in outputs.items():
        target = config.artifacts_dir / file_name
        target.write_text(payload["stdout"], encoding="utf-8")
        recorder.add_artifact(target)

    recorder.add_step(StepResult("INF-001", "infra", "Kubernetes inventory artifacts", "PASS", "Pod, service, ingress, ArgoCD app, and ExternalSecret outputs captured", artifact="artifacts/kubernetes-pod-inventory.txt"))
