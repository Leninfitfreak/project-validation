from __future__ import annotations

import subprocess
from pathlib import Path

from validator_engine.validators import ValidationResult


class KafkaValidator:
    def __init__(self, root: Path, env: dict, model: dict, evidence) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence

    def _docker(self, script: str) -> subprocess.CompletedProcess:
        return subprocess.run(['docker', 'exec', 'kafka-platform', '/bin/sh', '-lc', script], capture_output=True, text=True)

    def repair(self) -> ValidationResult:
        repairs = []
        running = subprocess.run(['docker', 'inspect', 'kafka-platform', '--format', '{{.State.Running}}'], capture_output=True, text=True)
        if running.stdout.strip() != 'true':
            subprocess.run(['docker', 'start', 'kafka-platform'], capture_output=True, text=True)
            repairs.append('started kafka-platform container')
        for topic in ('product-orders', 'product-events', 'order-events', 'order-created', 'validation-probe'):
            self._docker(f'unset KAFKA_OPTS; kafka-topics --bootstrap-server localhost:9092 --create --if-not-exists --topic {topic} --partitions 1 --replication-factor 1 >/dev/null 2>&1 || true')
        repairs.append('ensured Kafka topics exist')
        return ValidationResult('kafka-repair', True, 'Applied Kafka repair actions', {'repairs': repairs}, repairs)

    def validate(self) -> ValidationResult:
        topics = self._docker('unset KAFKA_OPTS; kafka-topics --bootstrap-server localhost:9092 --list')
        available = [line.strip() for line in topics.stdout.splitlines() if line.strip()]
        probe = 'validation-probe-message'
        self._docker(f'unset KAFKA_OPTS; printf "{probe}\\n" | kafka-console-producer --bootstrap-server localhost:9092 --topic validation-probe >/dev/null 2>&1')
        consume = self._docker('unset KAFKA_OPTS; timeout 10 kafka-console-consumer --bootstrap-server localhost:9092 --topic validation-probe --from-beginning --max-messages 1 2>/dev/null')
        health = subprocess.run(['docker', 'inspect', 'kafka-platform', '--format', '{{json .State.Health}}'], capture_output=True, text=True).stdout.strip()
        success = all(topic in available for topic in self.model['kafka_topics']) and probe in consume.stdout
        details = {'topics': available, 'probe_output': consume.stdout.strip(), 'health': health}
        self.evidence.record('kafka', details)
        return ValidationResult('kafka', success, 'Kafka validated' if success else 'Kafka validation failed', details)
