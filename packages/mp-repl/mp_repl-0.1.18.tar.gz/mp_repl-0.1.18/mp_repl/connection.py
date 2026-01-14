#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
@dataclass
class Connection:
    name: str
    url: str
    browser: Browser
    context: BrowserContext
    page: Page
class ConnectionManager:
    def __init__(self):
        self._pw = None
        self._connections: dict[str, Connection] = {}
        self._current: Optional[str] = None
    async def _ensure_pw(self):
        if not self._pw:
            self._pw = await async_playwright().start()
    async def connect(self, url: str = "127.0.0.1:9222", name: str = None) -> Connection:
        await self._ensure_pw()
        name = name or f"conn{len(self._connections)}"
        if not url.startswith("http"):
            url = f"http://{url}"
        browser = await self._pw.chromium.connect_over_cdp(url)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = context.pages[0] if context.pages else await context.new_page()
        conn = Connection(name, url, browser, context, page)
        self._connections[name] = conn
        self._current = name
        return conn
    async def launch(self, port: int = 9222, name: str = None) -> Connection:
        await self._ensure_pw()
        name = name or f"browser{len(self._connections)}"
        browser = await self._pw.chromium.launch(headless=False, args=[f"--remote-debugging-port={port}"])
        context = await browser.new_context()
        page = await context.new_page()
        conn = Connection(name, f"127.0.0.1:{port}", browser, context, page)
        self._connections[name] = conn
        self._current = name
        return conn
    async def disconnect(self, name: str = None):
        name = name or self._current
        if name in self._connections:
            await self._connections[name].browser.close()
            del self._connections[name]
            if self._current == name:
                self._current = next(iter(self._connections), None)
    def use(self, name: str) -> bool:
        if name in self._connections:
            self._current = name
            return True
        return False
    @property
    def current(self) -> Optional[Connection]:
        return self._connections.get(self._current)
    @property
    def page(self) -> Optional[Page]:
        return self.current.page if self.current else None
    def set_page(self, index: int) -> bool:
        if not self.current:
            return False
        pages = self.current.context.pages
        if 0 <= index < len(pages):
            self.current.page = pages[index]
            return True
        return False
    def set_page_by_id(self, target_id: str) -> bool:
        if not self.current:
            return False
        for p in self.current.context.pages:
            if hasattr(p, '_target_id') and p._target_id == target_id:
                self.current.page = p
                return True
        return False
    def get_pages(self) -> list[tuple[int, str, bool]]:
        if not self.current:
            return []
        pages = self.current.context.pages
        current_page = self.current.page
        return [(i, p.url[:60], p == current_page) for i, p in enumerate(pages)]
    @property
    def browser(self) -> Optional[Browser]:
        return self.current.browser if self.current else None
    @property
    def context(self) -> Optional[BrowserContext]:
        return self.current.context if self.current else None
    def list(self) -> list[tuple[str, str, bool]]:
        return [(n, c.url, n == self._current) for n, c in self._connections.items()]
    async def close_all(self):
        for conn in list(self._connections.values()):
            try: await conn.browser.close()
            except: pass
        self._connections.clear()
        self._current = None
        if self._pw:
            await self._pw.stop()
            self._pw = None