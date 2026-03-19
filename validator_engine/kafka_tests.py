from __future__ import annotations

import json
import subprocess
from pathlib import Path

from validator_engine.validators import ValidationResult


class KafkaTests:
    REQUIRED_TOPICS = {'product-orders', 'product-events', 'order-events', 'order-created'}
    KAFKA_BOOTSTRAP_HOST = 'host.k3d.internal'
    KAFKA_NETWORK = 'k3d-leninkart-dev'

    def __init__(self, root: Path, env: dict, model: dict, evidence, catalog) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence
        self.test_ids = catalog.require('MQ-001', 'MQ-002', 'MQ-003', 'MQ-004', 'MQ-005', 'MQ-006', 'MQ-007')

    def _docker(self, script: str) -> subprocess.CompletedProcess:
        return subprocess.run(['docker', 'exec', 'kafka-platform', '/bin/sh', '-lc', script], capture_output=True, text=True)

    def _docker_inspect_networks(self) -> dict:
        result = subprocess.run(['docker', 'inspect', 'kafka-platform', '--format', '{{json .NetworkSettings.Networks}}'], capture_output=True, text=True)
        if result.returncode != 0 or not result.stdout.strip():
            return {}
        return json.loads(result.stdout)

    def _kafka_k3d_ip(self) -> str | None:
        return self._docker_inspect_networks().get(self.KAFKA_NETWORK, {}).get('IPAddress')

    def _business_pods(self) -> list[str]:
        pod_names = []
        selectors = ['app=product-service', 'app.kubernetes.io/name=order-service']
        for selector in selectors:
            result = subprocess.run(
                ['kubectl', 'get', 'pods', '-n', 'dev', '-l', selector, '-o', 'jsonpath={.items[0].metadata.name}'],
                capture_output=True,
                text=True,
            )
            name = result.stdout.strip()
            if name:
                pod_names.append(name)
        return pod_names

    def _tcp_check_from_pod(self, pod: str, target: str) -> bool:
        result = subprocess.run(
            ['kubectl', 'exec', '-n', 'dev', pod, '--', 'bash', '-lc', f"timeout 5 bash -c '</dev/tcp/{target}/9092' && echo OK || echo FAIL"],
            capture_output=True,
            text=True,
        )
        return 'OK' in result.stdout

    def _rewrite_pod_hosts(self, pod: str, host_ip: str) -> None:
        script = (
            "pod_ip=$(hostname -i | awk '{print $1}'); "
            "pod_name=$(hostname); "
            "printf '# Kubernetes-managed hosts file.\\n127.0.0.1\\tlocalhost\\n::1\\tlocalhost ip6-localhost ip6-loopback\\n"
            "fe00::0\\tip6-localnet\\nfe00::0\\tip6-mcastprefix\\nfe00::1\\tip6-allnodes\\nfe00::2\\tip6-allrouters\\n"
            "%s\\t%s\\n\\n# Entries added by HostAliases.\\n%s\\thost.k3d.internal\\n' \"$pod_ip\" \"$pod_name\" '"
            + host_ip
            + "' > /etc/hosts"
        )
        subprocess.run(['kubectl', 'exec', '-n', 'dev', pod, '--', 'sh', '-c', script], capture_output=True, text=True)

    def repair(self) -> list[str]:
        repairs = []
        running = subprocess.run(['docker', 'inspect', 'kafka-platform', '--format', '{{.State.Running}}'], capture_output=True, text=True)
        if running.stdout.strip() != 'true':
            subprocess.run(['docker', 'start', 'kafka-platform'], capture_output=True, text=True)
            repairs.append('started kafka-platform container')

        networks = self._docker_inspect_networks()
        if self.KAFKA_NETWORK not in networks:
            network_exists = subprocess.run(['docker', 'network', 'inspect', self.KAFKA_NETWORK], capture_output=True, text=True).returncode == 0
            if network_exists:
                subprocess.run(['docker', 'network', 'connect', self.KAFKA_NETWORK, 'kafka-platform'], capture_output=True, text=True)
                repairs.append(f'connected kafka-platform container to {self.KAFKA_NETWORK}')
            else:
                repairs.append(f'k3d network {self.KAFKA_NETWORK} not present yet')
            networks = self._docker_inspect_networks()

        kafka_ip = networks.get(self.KAFKA_NETWORK, {}).get('IPAddress')

        for topic in sorted(self.REQUIRED_TOPICS | {'validation-probe'}):
            self._docker(f'unset KAFKA_OPTS; kafka-topics --bootstrap-server localhost:9092 --create --if-not-exists --topic {topic} --partitions 1 --replication-factor 1 >/dev/null 2>&1 || true')
        repairs.append('ensured required Kafka topics exist')

        pods = self._business_pods()
        if pods:
            if not all(self._tcp_check_from_pod(pod, self.KAFKA_BOOTSTRAP_HOST) for pod in pods):
                candidates = ['192.168.56.1']
                if kafka_ip:
                    candidates.append(kafka_ip)
                for candidate in candidates:
                    if all(self._tcp_check_from_pod(pod, candidate) for pod in pods):
                        for pod in pods:
                            self._rewrite_pod_hosts(pod, candidate)
                        repairs.append(f'rewrote running pod hosts entries to host.k3d.internal={candidate}')
                        break
        return repairs

    def run(self, context: dict) -> ValidationResult:
        topics = self._docker('unset KAFKA_OPTS; kafka-topics --bootstrap-server localhost:9092 --list')
        available = {line.strip() for line in topics.stdout.splitlines() if line.strip()}
        probe = f"probe-{context.get('traffic', {}).get('user_email', 'validation')}"
        self._docker(f'unset KAFKA_OPTS; printf "{probe}\\n" | kafka-console-producer --bootstrap-server localhost:9092 --topic validation-probe >/dev/null 2>&1')
        consume = self._docker('unset KAFKA_OPTS; timeout 10 kafka-console-consumer --bootstrap-server localhost:9092 --topic validation-probe --from-beginning --max-messages 10 2>/dev/null')
        metrics = subprocess.run(['curl.exe', '-s', 'http://127.0.0.1:7071/metrics'], capture_output=True, text=True)
        probe_ok = bool(consume.stdout.strip())
        details = {
            'topics': sorted(available),
            'probe_output': consume.stdout.strip(),
            'jmx_metrics_present': 'jmx_scrape_duration_seconds' in metrics.stdout,
            'k3d_gateway': subprocess.run(['docker', 'network', 'inspect', self.KAFKA_NETWORK, '--format', '{{range .IPAM.Config}}{{.Gateway}}{{end}}'], capture_output=True, text=True).stdout.strip(),
            'kafka_k3d_ip': self._kafka_k3d_ip(),
            'kafka_bootstrap_target': self.KAFKA_BOOTSTRAP_HOST,
        }
        success = self.REQUIRED_TOPICS.issubset(available) and probe_ok and details['jmx_metrics_present']
        self.evidence.record_result('kafka', details)
        return ValidationResult('kafka', success, 'Kafka validation passed' if success else 'Kafka validation failed', details, test_ids=self.test_ids)
