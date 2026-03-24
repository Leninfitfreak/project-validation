from __future__ import annotations

import socket
import subprocess
import time
from dataclasses import dataclass


@dataclass
class PortForwardSpec:
    namespace: str
    resource: str
    ports: str


class PortForward:
    def __init__(self, spec: PortForwardSpec) -> None:
        self.spec = spec
        self.process: subprocess.Popen[str] | None = None

    def __enter__(self) -> "PortForward":
        self.process = subprocess.Popen(
            ["kubectl", "port-forward", "-n", self.spec.namespace, self.spec.resource, self.spec.ports],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        port = int(self.spec.ports.split(":", 1)[0])
        for _ in range(60):
            with socket.socket() as sock:
                if sock.connect_ex(("127.0.0.1", port)) == 0:
                    return self
            time.sleep(0.5)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except Exception:
                self.process.kill()
