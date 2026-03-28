from __future__ import annotations

from contextlib import ExitStack

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
        for _, port_spec in self.config.settings["defaults"]["ports"].items():
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
            device_scale_factor=browser_settings.get("device_scale_factor", 1),
            color_scheme=browser_settings.get("color_scheme", "light"),
            locale=browser_settings.get("locale", "en-US"),
            timezone_id=browser_settings.get("timezone_id", "Asia/Calcutta"),
        )
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.browser:
            self.browser.close()
        self.stack.close()

    def new_page(self) -> Page:
        if not self.context:
            raise RuntimeError("browser harness not initialized")
        page = self.context.new_page()
        page.set_default_timeout(self.config.settings["defaults"]["waits"]["timeout_ms"])
        return page
