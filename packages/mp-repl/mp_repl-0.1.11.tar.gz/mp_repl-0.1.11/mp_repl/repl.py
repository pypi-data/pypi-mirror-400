#!/usr/bin/env python3
import asyncio
import time
import shlex
from typing import Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from mp_repl.config import config, CONFIG_DIR, HISTORY_FILE
from mp_repl.connection import ConnectionManager
class Repl:
    def __init__(self):
        self.conn_mgr = ConnectionManager()
        self.scripts = {}
        self._running = True
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.session = PromptSession(history=FileHistory(str(HISTORY_FILE)))
    async def run(self):
        print("pw-repl v0.1.11 - Type 'help' for commands")
        while self._running:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.session.prompt("pw> ")
                )
                if line.strip():
                    await self.execute(line.strip())
            except EOFError:
                break
            except KeyboardInterrupt:
                print()
                continue
        await self.conn_mgr.close_all()
    async def execute(self, line: str):
        start = time.time()
        try:
            if line.startswith(("page.", "browser.", "context.")):
                result = await self._exec_playwright(line)
                self._ok(result, start)
            elif "(" in line and not line.startswith(("go ", "goto ", "click ", "fill ", "btn ", "txt ", "wait ", "run ")):
                result = await self._exec_func(line)
                self._ok(result, start)
            else:
                await self._exec_command(line)
        except Exception as e:
            self._err(e)
    async def _exec_playwright(self, code: str):
        ns = {"page": self.conn_mgr.page, "browser": self.conn_mgr.browser, "context": self.conn_mgr.context}
        result = eval(code, ns)
        if asyncio.iscoroutine(result):
            result = await result
        return result
    async def _exec_func(self, code: str):
        ns = {"page": self.conn_mgr.page, "browser": self.conn_mgr.browser, "context": self.conn_mgr.context}
        ns.update(self.scripts)
        result = eval(code, ns)
        if asyncio.iscoroutine(result):
            result = await result
        return result
    async def _exec_command(self, line: str):
        parts = shlex.split(line)
        cmd, args = parts[0], parts[1:]
        handler = getattr(self, f"cmd_{cmd}", None)
        if handler:
            result = await handler(*args)
            return result
        else:
            print(f"✗ Unknown command: {cmd}")
    def _ok(self, result, start):
        elapsed = time.time() - start
        if result is not None:
            print(f"✓ {result} ({elapsed:.2f}s)")
        else:
            print(f"✓ ({elapsed:.2f}s)")
    def _err(self, e):
        print(f"✗ {type(e).__name__}: {e}")
    async def cmd_connect(self, url: str = None, name: str = None):
        url = url or config.get("cdp_url")
        conn = await self.conn_mgr.connect(url, name)
        print(f"✓ Connected: {conn.name} ({conn.url})")
        if conn.page:
            print(f"  Page: {conn.page.url}")
    async def cmd_launch(self, port: str = "9222", name: str = None):
        conn = await self.conn_mgr.launch(int(port), name)
        print(f"✓ Launched: {conn.name} ({conn.url})")
    async def cmd_disconnect(self, name: str = None):
        await self.conn_mgr.disconnect(name)
        print("✓ Disconnected")
    async def cmd_connections(self):
        conns = self.conn_mgr.list()
        if not conns:
            print("No connections")
            return
        for name, url, active in conns:
            mark = "*" if active else " "
            print(f"  {mark} {name}  {url}")
    async def cmd_use(self, name: str):
        if self.conn_mgr.use(name):
            print(f"✓ Switched to: {name}")
        else:
            print(f"✗ Connection not found: {name}")
    async def cmd_status(self):
        conn = self.conn_mgr.current
        if conn:
            print(f"Connection: {conn.name} ({conn.url})")
            print(f"Page: {conn.page.url if conn.page else 'none'}")
        else:
            print("Not connected")
    async def cmd_url(self):
        if self.conn_mgr.page:
            print(self.conn_mgr.page.url)
    async def cmd_go(self, url: str):
        if not url.startswith(("http://", "https://", "file://")):
            url = "https://" + url
        await self.conn_mgr.page.goto(url)
        print(f"✓ {self.conn_mgr.page.url}")
    async def cmd_goto(self, url: str):
        await self.cmd_go(url)
    async def cmd_back(self):
        await self.conn_mgr.page.go_back()
        print(f"✓ {self.conn_mgr.page.url}")
    async def cmd_forward(self):
        await self.conn_mgr.page.go_forward()
        print(f"✓ {self.conn_mgr.page.url}")
    async def cmd_reload(self):
        await self.conn_mgr.page.reload()
        print("✓ Reloaded")
    async def cmd_click(self, selector: str):
        await self.conn_mgr.page.locator(selector).click()
        print("✓ Clicked")
    async def cmd_fill(self, selector: str, value: str):
        await self.conn_mgr.page.locator(selector).fill(value)
        print("✓ Filled")
    async def cmd_type(self, text: str):
        await self.conn_mgr.page.keyboard.type(text)
        print("✓ Typed")
    async def cmd_press(self, key: str):
        await self.conn_mgr.page.keyboard.press(key)
        print("✓ Pressed")
    async def cmd_btn(self, name: str):
        await self.conn_mgr.page.get_by_role("button", name=name).click()
        print("✓ Clicked")
    async def cmd_link(self, text: str):
        await self.conn_mgr.page.get_by_role("link", name=text).click()
        print("✓ Clicked")
    async def cmd_txt(self, text: str):
        await self.conn_mgr.page.get_by_text(text).click()
        print("✓ Clicked")
    async def cmd_input(self, label: str, value: str):
        await self.conn_mgr.page.get_by_label(label).fill(value)
        print("✓ Filled")
    async def cmd_wait(self, arg: str):
        if arg.isdigit():
            await asyncio.sleep(int(arg))
        else:
            await self.conn_mgr.page.wait_for_selector(arg)
        print("✓ Done")
    async def cmd_hover(self, selector: str):
        await self.conn_mgr.page.locator(selector).hover()
        print("✓ Hovered")
    async def cmd_run(self, filepath: str):
        import sys
        with open(filepath, 'r') as f:
            code = f.read()
        def debug():
            print("🔴 Debug breakpoint (continue not implemented yet)")
            sys.stdout.flush()
        ns = {
            "page": self.conn_mgr.page,
            "browser": self.conn_mgr.browser,
            "context": self.conn_mgr.context,
            "debug": debug,
            "print": lambda *args, **kwargs: (print(*args, **kwargs), sys.stdout.flush()),
        }
        if 'await ' in code and not code.strip().startswith('async def'):
            lines = code.split('\n')
            imports = []
            body = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('import ') or stripped.startswith('from '):
                    imports.append(line)
                else:
                    body.append(f"    {line}")
            for imp in imports:
                exec(imp, ns)
            wrapped = "async def __run__():\n" + '\n'.join(body)
            wrapped += "\n__result__ = __run__()"
            exec(wrapped, ns)
            await ns["__result__"]
            print(f"✓ Executed: {filepath}")
            sys.stdout.flush()
        else:
            import importlib.util
            spec = importlib.util.spec_from_file_location("script", filepath)
            module = importlib.util.module_from_spec(spec)
            module.page = self.conn_mgr.page
            module.browser = self.conn_mgr.browser
            module.context = self.conn_mgr.context
            module.debug = debug
            spec.loader.exec_module(module)
            for name in dir(module):
                if not name.startswith("_"):
                    obj = getattr(module, name)
                    if callable(obj):
                        self.scripts[name] = obj
            funcs = [n for n in self.scripts.keys()]
            print(f"✓ Loaded: {filepath}")
            if funcs:
                print(f"  Functions: {', '.join(funcs)}")
            sys.stdout.flush()
    async def cmd_funcs(self):
        if not self.scripts:
            print("No functions loaded")
            return
        for name, func in self.scripts.items():
            print(f"  {name}")
    async def cmd_shot(self, name: str = "screenshot.png"):
        await self.conn_mgr.page.screenshot(path=name)
        print(f"✓ Saved: {name}")
    async def cmd_pages(self):
        if not self.conn_mgr.page:
            print("Not connected")
            return
        try:
            cdp = await self.conn_mgr.context.new_cdp_session(self.conn_mgr.page)
            result = await cdp.send("Target.getTargets")
            targets = [t for t in result.get("targetInfos", []) if t.get("type") == "page"]
            current_url = self.conn_mgr.page.url
            for i, t in enumerate(targets):
                mark = "*" if t["url"] == current_url else " "
                url = t["url"][:60] if len(t["url"]) > 60 else t["url"]
                print(f"  {mark} [{i}] {url}")
            self._targets = targets
        except Exception as e:
            pages = self.conn_mgr.get_pages()
            for i, url, active in pages:
                mark = "*" if active else " "
                print(f"  {mark} [{i}] {url}")
    async def cmd_page(self, index: str):
        if not self.conn_mgr.page:
            print("Not connected")
            return
        idx = int(index)
        if hasattr(self, '_targets') and idx < len(self._targets):
            target = self._targets[idx]
            for p in self.conn_mgr.context.pages:
                if p.url == target["url"]:
                    self.conn_mgr.current.page = p
                    print(f"✓ Switched to [{index}] {target['url'][:60]}")
                    return
        if self.conn_mgr.set_page(idx):
            print(f"✓ Switched to [{index}] {self.conn_mgr.page.url[:60]}")
        else:
            print(f"✗ Invalid page index: {index}")
    async def cmd_front(self):
        await self.conn_mgr.page.bring_to_front()
        print("✓ Brought to front")
    async def cmd_history(self, pattern: str = None):
        items = list(self.session.history.get_strings())
        if pattern and not pattern.isdigit():
            items = [c for c in items if pattern in c]
        elif pattern and pattern.isdigit():
            items = items[-int(pattern):]
        else:
            items = items[-20:]
        self._history_items = items
        for i, cmd in enumerate(items, 1):
            print(f"  {i}. {cmd}")
    async def cmd_r(self, index: str):
        if not hasattr(self, '_history_items') or not self._history_items:
            await self.cmd_history()
        idx = int(index) - 1
        if 0 <= idx < len(self._history_items):
            cmd = self._history_items[idx]
            print(f"> {cmd}")
            await self.execute(cmd)
        else:
            print(f"✗ Invalid index: {index}")
    async def cmd_help(self, cmd: str = None):
        import sys
        if cmd:
            handler = getattr(self, f"cmd_{cmd}", None)
            if handler and handler.__doc__:
                print(handler.__doc__)
            else:
                print(f"No help for: {cmd}")
            return
        print(help_text)
        sys.stdout.flush()
    async def cmd_exit(self):
        self._running = False
    async def cmd_quit(self):
        self._running = False