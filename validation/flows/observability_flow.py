from __future__ import annotations

import json
import re
import shutil
import urllib.parse
import urllib.request

from playwright.sync_api import Page

from validation.checks import grafana_checks
from validation.core.config import ValidationConfig
from validation.core.reporting import RunRecorder, StepResult
from validation.core.screenshots import capture_when_ready
from validation.core.waits import wait_for_condition, wait_for_text


def _grafana_explore_url(config: ValidationConfig, datasource_uid: str, datasource_type: str, query: dict, *, from_range: str = "now-15m", to_range: str = "now") -> str:
    pane = {
        "datasource": datasource_uid,
        "queries": [query | {"refId": "A", "datasource": {"type": datasource_type, "uid": datasource_uid}}],
        "range": {"from": from_range, "to": to_range},
        "compact": False,
    }
    return (
        config.env["GRAFANA_URL"].rstrip("/")
        + "/explore?"
        + urllib.parse.urlencode({"schemaVersion": 1, "panes": json.dumps({"pv": pane}, separators=(",", ":")), "orgId": 1})
    )


def _grafana_login(page: Page, config: ValidationConfig, recorder: RunRecorder) -> None:
    waits = config.settings["defaults"]["waits"]
    image_rules = config.settings["defaults"]["screenshot_quality"]
    timeout = waits["timeout_ms"]
    long_timeout = waits["long_timeout_ms"]
    page.goto(config.env["GRAFANA_URL"] + "/login", wait_until="domcontentloaded")
    capture_when_ready(
        page,
        config.screenshot_dir("observability") / "grafana-login.png",
        require_no_loading=False,
        verify=lambda: (
            wait_for_text(page, "Welcome to Grafana", timeout),
            wait_for_condition(
                page,
                "grafana login fields visible",
                lambda: page.locator('input[name="user"]').count() > 0 and page.locator('input[name="password"]').count() > 0,
                timeout,
            ),
        ),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult("OBS-001", "observability", "Grafana login", "PASS", "Grafana login page visible", "screenshots/observability/grafana-login.png"))

    page.locator('input[name="user"]').fill(config.env["GRAFANA_USERNAME"])
    page.locator('input[name="password"]').fill(config.env["GRAFANA_PASSWORD"])
    page.get_by_role("button", name="Log in").click()
    wait_for_text(page, "Home", long_timeout)


def _open_dashboard_folder(page: Page, config: ValidationConfig, timeout_ms: int) -> None:
    folder_name = config.settings["defaults"]["observability"]["grafana"]["folder_hint"]
    page.goto(config.env["GRAFANA_URL"] + "/dashboards", wait_until="domcontentloaded")
    wait_for_text(page, "Dashboards", timeout_ms)
    wait_for_text(page, folder_name, timeout_ms)
    body = page.text_content("body") or ""
    if "LeninKart Platform Overview" not in body:
        page.get_by_text(folder_name, exact=False).first.click()
        wait_for_text(page, "LeninKart Platform Overview", timeout_ms)


def _capture_dashboard_list(page: Page, config: ValidationConfig, recorder: RunRecorder) -> None:
    waits = config.settings["defaults"]["waits"]
    image_rules = config.settings["defaults"]["screenshot_quality"]
    long_timeout = waits["long_timeout_ms"]
    dashboard_names = config.settings["defaults"]["observability"]["dashboards"]
    _open_dashboard_folder(page, config, long_timeout)
    capture_when_ready(
        page,
        config.screenshot_dir("observability") / "grafana-dashboard-list.png",
        require_no_loading=False,
        verify=lambda: (
            wait_for_text(page, dashboard_names[0], long_timeout),
            wait_for_text(page, dashboard_names[1], long_timeout),
            wait_for_text(page, dashboard_names[2], long_timeout),
        ),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult("OBS-002", "observability", "Grafana dashboard list", "PASS", "Provisioned dashboard list visible inside the LeninKart folder", "screenshots/observability/grafana-dashboard-list.png"))


def _open_dashboard(page: Page, config: ValidationConfig, recorder: RunRecorder, dashboard_name: str, screenshot_name: str, panel_hint: str, step_id: str) -> None:
    waits = config.settings["defaults"]["waits"]
    image_rules = config.settings["defaults"]["screenshot_quality"]
    long_timeout = waits["long_timeout_ms"]
    _open_dashboard_folder(page, config, long_timeout)
    page.get_by_text(dashboard_name, exact=False).first.click()
    page.wait_for_timeout(3000)

    current_url = urllib.parse.urlparse(page.url)
    query = urllib.parse.parse_qs(current_url.query)
    query["from"] = ["now-6h"]
    query["to"] = ["now"]
    query["refresh"] = ["off"]
    page.goto(urllib.parse.urlunparse(current_url._replace(query=urllib.parse.urlencode(query, doseq=True))), wait_until="domcontentloaded")

    capture_when_ready(
        page,
        config.screenshot_dir("observability") / screenshot_name,
        require_no_loading=False,
        verify=lambda: grafana_checks.dashboard_ready(page, dashboard_name, panel_hint, long_timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult(step_id, "observability", dashboard_name, "PASS", f"{dashboard_name} rendered with visible content", f"screenshots/observability/{screenshot_name}"))


def _capture_loki_explore(page: Page, config: ValidationConfig, recorder: RunRecorder) -> None:
    waits = config.settings["defaults"]["waits"]
    image_rules = config.settings["defaults"]["screenshot_quality"]
    long_timeout = waits["long_timeout_ms"]
    page.goto(
        _grafana_explore_url(
            config,
            "loki",
            "loki",
            {"expr": '{service="product-service"}', "queryType": "range", "editorMode": "code", "direction": "backward"},
        ),
        wait_until="domcontentloaded",
    )
    capture_when_ready(
        page,
        config.screenshot_dir("observability") / "grafana-loki-explore.png",
        require_no_loading=False,
        verify=lambda: (
            wait_for_text(page, "Loki", long_timeout),
            wait_for_text(page, "Logs volume", long_timeout),
            wait_for_condition(
                page,
                "loki results visible",
                lambda: (page.text_content("body") or "").count("product-service") >= 2 and "Logs" in (page.text_content("body") or ""),
                long_timeout,
            ),
        ),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult("OBS-009", "observability", "Grafana Explore Loki", "PASS", "Loki search returned recent product-service logs", "screenshots/observability/grafana-loki-explore.png"))


def _capture_prometheus(page: Page, config: ValidationConfig, recorder: RunRecorder) -> None:
    waits = config.settings["defaults"]["waits"]
    image_rules = config.settings["defaults"]["screenshot_quality"]
    timeout = waits["timeout_ms"]
    page.goto(config.env["PROMETHEUS_URL"] + "/targets", wait_until="domcontentloaded")
    capture_when_ready(
        page,
        config.screenshot_dir("observability") / "prometheus-targets.png",
        require_no_loading=False,
        verify=lambda: (
            wait_for_text(page, "Target health", timeout),
            wait_for_text(page, "product-service", timeout),
            wait_for_text(page, "order-service", timeout),
            wait_for_text(page, "kafka-platform", timeout),
        ),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult("OBS-010", "observability", "Prometheus targets", "PASS", "Prometheus targets page populated", "screenshots/observability/prometheus-targets.png"))


def _tempo_recent_trace(service_name: str, config: ValidationConfig) -> str:
    url = (
        config.env["TEMPO_URL"].rstrip("/")
        + "/api/search?"
        + urllib.parse.urlencode({"q": f'{{resource.service.name="{service_name}"}}', "limit": 5})
    )
    with urllib.request.urlopen(url, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))
    traces = payload.get("traces", [])
    return traces[0]["traceID"] if traces else ""


def _tempo_search_results_visible(page: Page, service_name: str) -> bool:
    body = page.text_content("body") or ""
    return (
        "Table - Traces" in body
        and service_name in body
        and re.search(r"[0-9a-f]{32}", body) is not None
    )


def _capture_tempo(page: Page, config: ValidationConfig, recorder: RunRecorder) -> None:
    waits = config.settings["defaults"]["waits"]
    image_rules = config.settings["defaults"]["screenshot_quality"]
    long_timeout = waits["long_timeout_ms"]

    page.goto(config.env["GRAFANA_URL"] + "/connections/datasources", wait_until="domcontentloaded")
    page.get_by_text("Tempo", exact=False).first.click()
    capture_when_ready(
        page,
        config.screenshot_dir("observability") / "grafana-tempo-datasource.png",
        require_no_loading=False,
        verify=lambda: wait_for_text(page, "Tempo", long_timeout),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult("OBS-011", "observability", "Grafana Tempo datasource", "PASS", "Tempo datasource page visible", "screenshots/observability/grafana-tempo-datasource.png"))

    page.goto(config.env["GRAFANA_URL"] + "/explore", wait_until="domcontentloaded")
    wait_for_text(page, "Explore", long_timeout)
    datasource_input = page.locator('input[aria-label="Select a data source"]').first
    datasource_input.click()
    datasource_input.fill("Tempo")
    page.keyboard.press("Enter")
    wait_for_condition(
        page,
        "tempo editor visible",
        lambda: page.locator('textarea[aria-label*="Editor content"]').count() > 0,
        long_timeout,
    )
    product_trace_id = _tempo_recent_trace("product-service", config)
    query_box = page.locator('textarea[aria-label*="Editor content"]').first
    query_box.fill('{resource.service.name="product-service"}')
    page.keyboard.press("Shift+Enter")
    capture_when_ready(
        page,
        config.screenshot_dir("observability") / "tempo-search.png",
        require_no_loading=False,
        verify=lambda: (
            wait_for_condition(
                page,
                "tempo search results visible",
                lambda: _tempo_search_results_visible(page, "product-service"),
                long_timeout,
            ),
        ),
        retries=waits["retry_count"],
        retry_wait_ms=waits["retry_sleep_ms"],
        timeout_ms=long_timeout,
        image_rules=image_rules,
    )
    recorder.add_step(StepResult("OBS-012", "observability", "Tempo search results", "PASS", "Tempo search returned product-service traces", "screenshots/observability/tempo-search.png"))

    if product_trace_id:
        query_box = page.locator('textarea[aria-label*="Editor content"]').first
        query_box.fill(product_trace_id)
        page.keyboard.press("Shift+Enter")
        capture_when_ready(
            page,
            config.screenshot_dir("observability") / "tempo-product-trace.png",
            require_no_loading=False,
            verify=lambda: (
                wait_for_text(page, product_trace_id[:8], long_timeout),
                wait_for_text(page, "product-service", long_timeout),
            ),
            retries=waits["retry_count"],
            retry_wait_ms=waits["retry_sleep_ms"],
            timeout_ms=long_timeout,
            image_rules=image_rules,
        )
        recorder.add_step(StepResult("OBS-013", "observability", "Product trace detail", "PASS", "Product-service trace detail visible", "screenshots/observability/tempo-product-trace.png"))

    order_trace_id = _tempo_recent_trace("order-service", config)
    if order_trace_id:
        query_box = page.locator('textarea[aria-label*="Editor content"]').first
        query_box.fill(order_trace_id)
        page.keyboard.press("Shift+Enter")
        capture_when_ready(
            page,
            config.screenshot_dir("observability") / "tempo-order-trace.png",
            require_no_loading=False,
            verify=lambda: (
                wait_for_text(page, order_trace_id[:8], long_timeout),
                wait_for_text(page, "order-service", long_timeout),
            ),
            retries=waits["retry_count"],
            retry_wait_ms=waits["retry_sleep_ms"],
            timeout_ms=long_timeout,
            image_rules=image_rules,
        )
        recorder.add_step(StepResult("OBS-014", "observability", "Order trace detail", "PASS", "Order-service trace detail visible", "screenshots/observability/tempo-order-trace.png"))


def run(page: Page, config: ValidationConfig, recorder: RunRecorder) -> None:
    _grafana_login(page, config, recorder)
    _capture_dashboard_list(page, config, recorder)
    _open_dashboard(page, config, recorder, "LeninKart Platform Overview", "dashboard-platform.png", "Product Request Rate", "OBS-003")
    _open_dashboard(page, config, recorder, "LeninKart Product Service Overview", "dashboard-product.png", "Request Rate", "OBS-004")
    _open_dashboard(page, config, recorder, "LeninKart Order Service Overview", "dashboard-order.png", "Request Rate", "OBS-005")
    _open_dashboard(page, config, recorder, "LeninKart Frontend Overview", "dashboard-frontend.png", "Frontend Log Volume", "OBS-006")
    _open_dashboard(page, config, recorder, "LeninKart Logs Overview", "dashboard-logs.png", "Product Logs", "OBS-007")
    _open_dashboard(page, config, recorder, "LeninKart Kafka Overview", "dashboard-kafka.png", "Broker Up", "OBS-008")
    shutil.copyfile(
        config.screenshot_dir("observability") / "dashboard-kafka.png",
        config.screenshot_dir("messaging") / "kafka-dashboard.png",
    )
    _capture_loki_explore(page, config, recorder)
    _capture_prometheus(page, config, recorder)
    _capture_tempo(page, config, recorder)

