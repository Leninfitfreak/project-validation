from __future__ import annotations

from contextlib import ExitStack
from pathlib import Path

from playwright.sync_api import BrowserContext, Page, sync_playwright

from .config import ValidationConfig
from .ports import PortForward, PortForwardSpec


class BrowserHarness:
    def __init__(self, config: ValidationConfig) -> None:
        self.config = config
        self.stack = ExitStack()
        self.playwright = None
        self.browser = None
        self.context: BrowserContext | None = None

    def __enter__(self) -> "BrowserHarness":
        for port_name, port_spec in self.config.settings["defaults"]["ports"].items():
            self.stack.enter_context(
                PortForward(
                    PortForwardSpec(
                        namespace=port_spec["namespace"],
                        resource=port_spec["resource"],
                        ports=port_spec["ports"],
                    )
                )
            )
        self.playwright = self.stack.enter_context(sync_playwright())
        browser_settings = self.config.settings["defaults"]["browser"]
        self.browser = self.playwright.chromium.launch(
            headless=browser_settings["headless"],
            slow_mo=browser_settings.get("slow_mo_ms", 0),
        )
        self.context = self.browser.new_context(
            ignore_https_errors=True,
            viewport=browser_settings["viewport"],
        )
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.browser:
            self.browser.close()
        self.stack.close()

    def new_page(self) -> Page:
        if not self.context:
            raise RuntimeError("browser harness not initialized")
        return self.context.new_page()
