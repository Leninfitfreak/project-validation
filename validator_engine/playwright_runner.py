from __future__ import annotations

import base64
import socket
import subprocess
import time
from contextlib import ExitStack
from pathlib import Path
from typing import Any, Iterable

import requests
from playwright.sync_api import Page, sync_playwright


class UiStateError(RuntimeError):
    pass


class PortForward:
    def __init__(self, namespace: str, resource: str, ports: str) -> None:
        self.namespace = namespace
        self.resource = resource
        self.ports = ports
        self.process: subprocess.Popen[str] | None = None

    def __enter__(self):
        self.process = subprocess.Popen(
            ['kubectl', 'port-forward', '-n', self.namespace, self.resource, self.ports],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        host = '127.0.0.1'
        port = int(self.ports.split(':', 1)[0])
        for _ in range(60):
            with socket.socket() as sock:
                if sock.connect_ex((host, port)) == 0:
                    return self
            time.sleep(0.5)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except Exception:
                self.process.kill()


class PlaywrightRunner:
    INVALID_TEXT_SNIPPETS = (
        "this site can't be reached",
        'this site cannot be reached',
        'dns_probe',
        'err_',
        '404 not found',
        '500 internal',
        'bad gateway',
        'gateway timeout',
        'something went wrong',
        'connection refused',
        'unable to connect',
        'service unavailable',
    )

    def __init__(self, root: Path, env: dict[str, str], model: dict, evidence) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence
        self.screenshots_dir = root / 'screenshots'
        self.screenshots_dir.mkdir(exist_ok=True)

    def open(self):
        self.stack = ExitStack()
        for namespace, resource, ports in self.model.get('port_forwards', {}).values():
            self.stack.enter_context(PortForward(namespace, resource, ports))
        self.playwright = self.stack.enter_context(sync_playwright())
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context(ignore_https_errors=True, viewport={'width': 1600, 'height': 1000})
        return self

    def close(self) -> None:
        if getattr(self, 'browser', None):
            self.browser.close()
        if getattr(self, 'stack', None):
            self.stack.close()

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def new_page(self) -> Page:
        return self.context.new_page()

    def screenshot(self, page: Page, test_id: str, slug: str) -> str:
        file_name = f'{test_id}-{slug}.png'
        page.screenshot(path=str(self.screenshots_dir / file_name), full_page=True)
        self.evidence.add_screenshot(test_id, file_name)
        return file_name

    def _body_text(self, page: Page) -> str:
        try:
            return ' '.join((page.text_content('body') or '').split())
        except Exception:
            return ''

    def validate_page_state(
        self,
        page: Page,
        *,
        required_texts: Iterable[str] | None = None,
        required_selectors: Iterable[str] | None = None,
        forbidden_texts: Iterable[str] | None = None,
        forbidden_selectors: Iterable[str] | None = None,
        min_body_chars: int = 40,
    ) -> None:
        page.locator('body').first.wait_for(state='visible', timeout=5000)
        try:
            page.wait_for_load_state('networkidle', timeout=5000)
        except Exception:
            pass
        for selector in required_selectors or []:
            page.locator(selector).first.wait_for(state='visible', timeout=5000)
        text = self._body_text(page)
        normalized = text.lower()
        if len(text.strip()) < min_body_chars:
            raise UiStateError(f'page body too small for validated capture: {len(text.strip())} chars')
        if normalized in {'loading', 'loading...', 'please wait...', 'processing...'}:
            raise UiStateError(f'page still in transient state: {text}')
        for snippet in self.INVALID_TEXT_SNIPPETS:
            if snippet in normalized:
                raise UiStateError(f'invalid page state contains forbidden snippet: {snippet}')
        for snippet in forbidden_texts or []:
            if snippet.lower() in normalized:
                raise UiStateError(f'invalid page state contains forbidden text: {snippet}')
        for required in required_texts or []:
            if required.lower() not in normalized:
                raise UiStateError(f'missing required text: {required}')
        for selector in forbidden_selectors or []:
            locator = page.locator(selector)
            if locator.count() > 0 and locator.first.is_visible():
                raise UiStateError(f'forbidden selector visible: {selector}')

    def wait_for_valid_state(
        self,
        page: Page,
        *,
        required_texts: Iterable[str] | None = None,
        required_selectors: Iterable[str] | None = None,
        forbidden_texts: Iterable[str] | None = None,
        forbidden_selectors: Iterable[str] | None = None,
        min_body_chars: int = 40,
        timeout_ms: int = 60000,
        poll_ms: int = 1000,
    ) -> None:
        deadline = time.time() + (timeout_ms / 1000)
        last_error: Exception | None = None
        while time.time() < deadline:
            try:
                self.validate_page_state(
                    page,
                    required_texts=required_texts,
                    required_selectors=required_selectors,
                    forbidden_texts=forbidden_texts,
                    forbidden_selectors=forbidden_selectors,
                    min_body_chars=min_body_chars,
                )
                return
            except Exception as exc:
                last_error = exc
                page.wait_for_timeout(poll_ms)
        raise UiStateError(str(last_error) if last_error else 'timed out waiting for validated UI state')

    def validated_screenshot(
        self,
        page: Page,
        test_id: str,
        slug: str,
        **validation: Any,
    ) -> str:
        self.wait_for_valid_state(page, **validation)
        return self.screenshot(page, test_id, slug)

    def argocd_password(self) -> str:
        if self.env.get('ARGOCD_PASSWORD'):
            return self.env['ARGOCD_PASSWORD']
        result = subprocess.run(
            ['kubectl', 'get', 'secret', '-n', 'argocd', 'argocd-initial-admin-secret', '-o', 'jsonpath={.data.password}'],
            capture_output=True,
            text=True,
        )
        return base64.b64decode(result.stdout.strip()).decode() if result.returncode == 0 and result.stdout.strip() else ''

    def observer_service_present(self, service_name: str) -> bool:
        try:
            response = requests.get(self.env['OBSERVER_STACK_URL'].rstrip('/') + '/api/v1/services', timeout=20)
            return service_name in response.text
        except Exception:
            return False


