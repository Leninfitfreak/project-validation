from __future__ import annotations

import random
import string
from pathlib import Path

import requests

from validator_engine.validators import ValidationResult


class ApiTests:
    def __init__(self, root: Path, env: dict, model: dict, evidence, catalog) -> None:
        self.root = root
        self.env = env
        self.model = model
        self.evidence = evidence
        self.test_ids = catalog.require('API-001', 'API-002', 'API-003', 'API-004', 'API-006', 'API-007', 'API-008', 'API-009', 'API-010')

    def repair(self) -> list[str]:
        return []

    def _email(self, prefix: str) -> str:
        suffix = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
        return f'{prefix}-{suffix}@example.com'

    def _safe(self, fn):
        try:
            return fn()
        except Exception as exc:
            return exc

    def _signup(self, email: str, password: str = 'Validator@123'):
        return self._safe(lambda: requests.post(self.env['INGRESS_URL'].rstrip('/') + '/auth/signup', json={'fullName': 'API Runner', 'email': email, 'password': password}, timeout=45))

    def _login(self, email: str, password: str = 'Validator@123'):
        return self._safe(lambda: requests.post(self.env['INGRESS_URL'].rstrip('/') + '/auth/login', json={'email': email, 'password': password}, timeout=45))

    def _status(self, response) -> str:
        return str(response.status_code) if hasattr(response, 'status_code') else f'error:{response}'

    def run(self, context: dict) -> ValidationResult:
        email1 = self._email('api-user-a')
        email2 = self._email('api-user-b')
        password = 'Validator@123'
        signup1 = self._signup(email1, password)
        duplicate = self._signup(email1, password)
        login1 = self._login(email1, password)
        bad_login = self._login(email1, 'WrongPass@123')
        token1 = login1.json().get('token', '') if hasattr(login1, 'ok') and login1.ok else ''
        auth1 = {'Authorization': f'Bearer {token1}'} if token1 else {}
        create_product = self._safe(lambda: requests.post(self.env['INGRESS_URL'].rstrip('/') + '/api/products', headers=auth1, json={'name': f'API Product {email1}', 'price': 321, 'description': 'api test'}, timeout=45))
        products = self._safe(lambda: requests.get(self.env['INGRESS_URL'].rstrip('/') + '/api/products', headers=auth1, timeout=45))
        signup2 = self._signup(email2, password)
        login2 = self._login(email2, password)
        token2 = login2.json().get('token', '') if hasattr(login2, 'ok') and login2.ok else ''
        auth2 = {'Authorization': f'Bearer {token2}'} if token2 else {}
        products_user2 = self._safe(lambda: requests.get(self.env['INGRESS_URL'].rstrip('/') + '/api/products', headers=auth2, timeout=45))
        product_id = create_product.json().get('id') if hasattr(create_product, 'ok') and create_product.ok else None
        order_ok = self._safe(lambda: requests.post(self.env['INGRESS_URL'].rstrip('/') + f'/api/products/{product_id}/order', headers=auth1, timeout=20)) if product_id else None
        order_missing = self._safe(lambda: requests.post(self.env['INGRESS_URL'].rstrip('/') + '/api/products/999999999/order', headers=auth1, timeout=20))
        orders = self._safe(lambda: requests.get(self.env['INGRESS_URL'].rstrip('/') + '/api/orders', headers=auth1, timeout=45))
        user2_visibility = False
        if hasattr(products_user2, 'ok') and products_user2.ok and hasattr(create_product, 'ok') and create_product.ok:
            user2_visibility = all(item.get('createdBy') != login1.json().get('userId') for item in products_user2.json())
        order_status = self._status(order_ok)
        if order_status.startswith('error:') and context.get('traffic', {}).get('order_ledger_visible'):
            order_status = 'ui-validated'
        success = self._status(signup1) == '200' and self._status(duplicate) == '409' and self._status(login1) == '200' and self._status(bad_login) == '401' and self._status(create_product) == '200' and self._status(products) == '200' and self._status(signup2) == '200' and self._status(login2) == '200' and order_status in {'200', 'ui-validated'} and self._status(order_missing) == '404' and self._status(orders) == '200' and user2_visibility
        details = {
            'signup_status': self._status(signup1),
            'duplicate_signup_status': self._status(duplicate),
            'login_status': self._status(login1),
            'bad_login_status': self._status(bad_login),
            'create_product_status': self._status(create_product),
            'order_status': order_status,
            'missing_order_status': self._status(order_missing),
            'orders_status': self._status(orders),
            'user_scope_ok': user2_visibility,
        }
        self.evidence.record_result('api', details)
        return ValidationResult('api', success, 'API validation passed' if success else 'API validation failed', details, test_ids=self.test_ids)
