from __future__ import annotations

import random
import string
import time
from pathlib import Path

from validator_engine.playwright_runner import PlaywrightRunner, UiStateError


class TrafficGenerator:
    def __init__(self, root: Path, env: dict[str, str], model: dict, evidence) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence

    def _random_email(self) -> str:
        suffix = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
        return f'validator-{suffix}@example.com'

    def _random_product(self) -> str:
        suffix = ''.join(random.choice(string.ascii_lowercase) for _ in range(6))
        return f'Validation Product {suffix}'

    def run(self) -> dict:
        last_error = None
        for _ in range(3):
            state: dict = {
                'user_email': self._random_email(),
                'password': 'Validator@123',
                'product_name': self._random_product(),
                'screenshots': [],
                'timings': {},
                'orders_requested': 20,
                'product_visible': False,
                'order_ledger_visible': False,
            }
            try:
                with PlaywrightRunner(self.root, self.env, self.model, self.evidence) as runner:
                    page = runner.new_page()

                    started = time.perf_counter()
                    page.goto(self.env['INGRESS_URL'], wait_until='domcontentloaded', timeout=120000)
                    state['timings']['auth_page_seconds'] = round(time.perf_counter() - started, 2)
                    state['screenshots'].append(
                        runner.validated_screenshot(
                            page,
                            'FE-001',
                            'auth-page',
                            required_texts=['login', 'create account'],
                            required_selectors=['input[name="email"]', 'input[name="password"]', '.login-form button'],
                            forbidden_selectors=['text=This site can\'t be reached'],
                            min_body_chars=80,
                        )
                    )

                    page.get_by_role('button', name='Create account').click(timeout=5000)
                    page.locator('input[name="fullName"]').fill('Validation Runner')
                    page.locator('input[name="email"]').fill(state['user_email'])
                    page.locator('input[name="password"]').fill(state['password'])
                    page.locator('input[name="confirmPassword"]').fill(state['password'])
                    page.get_by_role('button', name='Create account').click(timeout=5000)
                    state['screenshots'].append(
                        runner.validated_screenshot(
                            page,
                            'FE-002',
                            'signup-success',
                            required_texts=['account created successfully', 'login'],
                            required_selectors=['input[name="email"]', 'input[name="password"]'],
                            min_body_chars=100,
                        )
                    )

                    started = time.perf_counter()
                    page.locator('input[name="email"]').fill(state['user_email'])
                    page.locator('input[name="password"]').fill(state['password'])
                    page.locator('.login-form button').click(timeout=5000)
                    state['screenshots'].append(
                        runner.validated_screenshot(
                            page,
                            'FE-004',
                            'dashboard',
                            required_texts=['sign out', 'product catalog', 'order ledger'],
                            required_selectors=['input[name="name"]', 'input[name="price"]', 'button:has-text("Add product")'],
                            forbidden_texts=['account created successfully'],
                            min_body_chars=250,
                            timeout_ms=90000,
                        )
                    )
                    state['timings']['dashboard_seconds'] = round(time.perf_counter() - started, 2)

                    page.locator('input[name="name"]').fill(state['product_name'])
                    page.locator('input[name="price"]').fill('999')
                    page.locator('input[name="description"]').fill('Created by validation automation')
                    state['screenshots'].append(
                        runner.validated_screenshot(
                            page,
                            'FE-008',
                            'product-form',
                            required_texts=['create product entry', 'add product'],
                            required_selectors=['input[name="name"]', 'input[name="price"]', 'button:has-text("Add product")'],
                            min_body_chars=250,
                        )
                    )
                    started = time.perf_counter()
                    page.get_by_role('button', name='Add product').click(timeout=5000)
                    runner.wait_for_valid_state(
                        page,
                        required_texts=[state['product_name'], 'buy'],
                        required_selectors=['button:has-text("Buy")'],
                        min_body_chars=300,
                        timeout_ms=90000,
                    )
                    state['timings']['product_create_seconds'] = round(time.perf_counter() - started, 2)
                    page_text = page.text_content('body') or ''
                    state['product_visible'] = state['product_name'] in page_text
                    state['screenshots'].append(
                        runner.validated_screenshot(
                            page,
                            'FE-008',
                            'product-list',
                            required_texts=[state['product_name'], 'buy'],
                            required_selectors=['button:has-text("Buy")'],
                            min_body_chars=300,
                        )
                    )

                    product_card = page.locator('.card', has_text=state['product_name']).first
                    started = time.perf_counter()
                    for _ in range(state['orders_requested']):
                        product_card.get_by_role('button', name='Buy').click(timeout=8000)
                        page.wait_for_timeout(700)
                    page.wait_for_timeout(6000)
                    deadline = time.time() + 180
                    while time.time() < deadline:
                        page.reload(wait_until='domcontentloaded', timeout=120000)
                        body = page.text_content('body') or ''
                        created_count = body.count('Status: CREATED')
                        if state['product_name'] in body and created_count >= state['orders_requested']:
                            state['order_ledger_visible'] = True
                            break
                        page.wait_for_timeout(5000)
                    state['timings']['order_ledger_seconds'] = round(time.perf_counter() - started, 2)
                    if not state['order_ledger_visible']:
                        raise UiStateError('order ledger did not show the expected created orders')
                    state['screenshots'].append(
                        runner.validated_screenshot(
                            page,
                            'FE-009',
                            'order-ledger',
                            required_texts=[state['product_name'], 'status: created', 'order ledger'],
                            forbidden_texts=['no orders yet'],
                            min_body_chars=350,
                            timeout_ms=30000,
                        )
                    )

                    storage = page.evaluate("""() => ({ token: localStorage.getItem('lk_token'), user: localStorage.getItem('lk_user') })""")
                    state['token'] = storage.get('token')
                    state['session_user'] = storage.get('user')

                self.evidence.record('traffic', state)
                return state
            except Exception as exc:
                last_error = exc
        failure = {'error': str(last_error) if last_error else 'traffic generation failed', 'screenshots': [], 'timings': {}}
        self.evidence.record('traffic', failure)
        raise RuntimeError(failure['error'])
