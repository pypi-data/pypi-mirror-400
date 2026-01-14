#!/usr/bin/env python3
"""REPL 主循环"""
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
        self.scripts = {}  # 已加载脚本的命名空间
        self._running = True
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.session = PromptSession(history=FileHistory(str(HISTORY_FILE)))
    
    async def run(self):
        print("pw-repl v0.1.21 - Type 'help' for commands")
        # 自动重连上次的连接
        last_url = config.get("last_connection")
        if last_url:
            try:
                await self.conn_mgr.connect(last_url)
                print(f"✓ Reconnected: {last_url}")
                if self.conn_mgr.page:
                    print(f"  Page: {self.conn_mgr.page.url}")
            except:
                print(f"⚠ Failed to reconnect: {last_url}")
        
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
            # await 开头 - 去掉 await 执行
            if line.startswith("await "):
                result = await self._exec_func(line[6:])
                self._ok(result, start)
            # Playwright 直接执行
            elif line.startswith(("page.", "browser.", "context.")):
                result = await self._exec_playwright(line)
                self._ok(result, start)
            # 赋值语句
            elif "=" in line and not line.startswith(("go ", "goto ")) and "==" not in line:
                await self._exec_assign(line)
            # 可能是函数调用
            elif "(" in line and not line.startswith(("go ", "goto ", "click ", "fill ", "btn ", "txt ", "wait ", "run ")):
                result = await self._exec_func(line)
                self._ok(result, start)
            # 内置命令
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
    
    async def _exec_assign(self, code: str):
        ns = {"page": self.conn_mgr.page, "browser": self.conn_mgr.browser, "context": self.conn_mgr.context}
        ns.update(self.scripts)
        exec(code, ns)
        # 提取变量名并保存到 scripts
        var_name = code.split("=")[0].strip()
        if var_name in ns:
            self.scripts[var_name] = ns[var_name]
            print(f"✓ {var_name} = {repr(ns[var_name])[:50]}")
    
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
    
    # === 连接命令 ===
    async def cmd_connect(self, url: str = None, name: str = None):
        url = url or config.get("cdp_url")
        conn = await self.conn_mgr.connect(url, name)
        config.set("last_connection", url)  # 保存用于下次自动重连
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
    
    # === 导航命令 ===
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
    
    # === 页面操作 ===
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
    
    # === 脚本执行 ===
    async def cmd_run(self, filepath: str):
        import sys
        import builtins
        
        with open(filepath, 'r') as f:
            code = f.read()
        
        # 保存 self 引用给 debug 使用
        repl_self = self
        
        # debug 函数 - 进入交互模式
        class DebugBreak(Exception):
            pass
        
        def debug():
            builtins.print("🔴 Debug breakpoint - type 'c' to continue, 'q' to quit")
            sys.stdout.flush()
            while True:
                try:
                    line = input("(debug) pw> ")
                    if line.strip() == 'c' or line.strip() == 'continue':
                        break
                    if line.strip() == 'q' or line.strip() == 'quit':
                        raise DebugBreak("User quit")
                    # 执行命令
                    if line.strip():
                        try:
                            if line.startswith(("page.", "browser.", "context.")):
                                result = eval(line, ns)
                                if hasattr(result, '__await__'):
                                    import asyncio
                                    result = asyncio.get_event_loop().run_until_complete(result)
                                builtins.print(f"  {result}")
                            else:
                                result = eval(line, ns)
                                builtins.print(f"  {result}")
                        except SyntaxError:
                            exec(line, ns)
                        except Exception as e:
                            builtins.print(f"  ✗ {e}")
                        sys.stdout.flush()
                except EOFError:
                    break
        
        # 包装 print 确保立即输出
        original_print = builtins.print
        def flushed_print(*args, **kwargs):
            original_print(*args, **kwargs)
            sys.stdout.flush()
        
        ns = {
            "page": self.conn_mgr.page,
            "browser": self.conn_mgr.browser,
            "context": self.conn_mgr.context,
            "debug": debug,
            "print": flushed_print,
            "__builtins__": builtins,
        }
        
        # 检查是否有顶层 await
        if 'await ' in code and not code.strip().startswith('async def'):
            # 包装成 async 函数执行
            lines = code.split('\n')
            # 先处理 import 语句和函数/类定义
            imports = []
            defs = []
            body = []
            in_def = False
            def_indent = 0
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('import ') or stripped.startswith('from '):
                    imports.append(line)
                elif stripped.startswith('def ') or stripped.startswith('class ') or stripped.startswith('async def '):
                    in_def = True
                    def_indent = len(line) - len(line.lstrip())
                    defs.append(line)
                elif in_def:
                    curr_indent = len(line) - len(line.lstrip()) if line.strip() else def_indent + 1
                    if curr_indent > def_indent or not line.strip():
                        defs.append(line)
                    else:
                        in_def = False
                        body.append(f"    {line}")
                else:
                    body.append(f"    {line}")
            
            # import 和函数定义放在外面
            for imp in imports:
                exec(imp, ns)
            if defs:
                exec('\n'.join(defs), ns)
            
            wrapped = "async def __run__():\n" + '\n'.join(body)
            wrapped += "\n__result__ = __run__()"
            
            exec(wrapped, ns)
            await ns["__result__"]
            
            # 导出函数到 scripts
            for name, obj in ns.items():
                if callable(obj) and not name.startswith('_') and name not in ('debug', 'print'):
                    self.scripts[name] = obj
            
            funcs = [n for n in self.scripts.keys() if not n.startswith('__')]
            print(f"✓ Executed: {filepath}")
            if funcs:
                print(f"  Functions: {', '.join(funcs)}")
            sys.stdout.flush()
        else:
            # 原有逻辑：加载模块并导出函数
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
    
    # === 截图 ===
    async def cmd_shot(self, name: str = "screenshot.png"):
        await self.conn_mgr.page.screenshot(path=name)
        print(f"✓ Saved: {name}")
    
    # === 多 Tab 管理 ===
    async def cmd_pages(self):
        if not self.conn_mgr.page:
            print("Not connected")
            return
        # 用 CDP 获取 targets
        try:
            cdp = await self.conn_mgr.context.new_cdp_session(self.conn_mgr.page)
            result = await cdp.send("Target.getTargets")
            targets = [t for t in result.get("targetInfos", []) if t.get("type") == "page"]
            current_page = self.conn_mgr.page
            for i, t in enumerate(targets):
                # 通过匹配 playwright pages 找到对应的 page 对象
                is_current = False
                for p in self.conn_mgr.context.pages:
                    if p.url == t["url"] and p == current_page:
                        is_current = True
                        break
                mark = "*" if is_current else " "
                url = t["url"][:60] if len(t["url"]) > 60 else t["url"]
                print(f"  {mark} [{i}] {url}")
            self._targets = targets
        except Exception as e:
            # fallback 到 Playwright
            pages = self.conn_mgr.get_pages()
            for i, url, active in pages:
                mark = "*" if active else " "
                print(f"  {mark} [{i}] {url}")
    
    async def cmd_page(self, index: str = None):
        if not self.conn_mgr.page:
            print("Not connected")
            return
        if index is None:
            # 无参数时显示当前 page 信息
            print(f"Current: {self.conn_mgr.page.url}")
            return
        idx = int(index)
        # 只切换内部 page 对象，不激活浏览器 tab
        if hasattr(self, '_targets') and idx < len(self._targets):
            target = self._targets[idx]
            for p in self.conn_mgr.context.pages:
                if p.url == target["url"]:
                    self.conn_mgr.current.page = p
                    print(f"✓ Switched to [{index}] {target['url'][:60]}")
                    return
        # fallback
        if self.conn_mgr.set_page(idx):
            print(f"✓ Switched to [{index}] {self.conn_mgr.page.url[:60]}")
        else:
            print(f"✗ Invalid page index: {index}")
    
    async def cmd_front(self):
        """Bring current page to front"""
        await self.conn_mgr.page.bring_to_front()
        print("✓ Brought to front")
    
    # === 历史 ===
    async def cmd_history(self, pattern: str = None):
        items = list(self.session.history.get_strings())
        
        # 去重，保留最后出现的位置
        seen = {}
        for i, cmd in enumerate(items):
            seen[cmd] = i
        unique = sorted(seen.keys(), key=lambda x: seen[x])
        
        if pattern and not pattern.isdigit():
            unique = [c for c in unique if pattern in c]
            unique = unique[-20:]
        elif pattern and pattern.isdigit():
            unique = unique[-int(pattern):]
        else:
            unique = unique[-20:]
        
        self._history_items = unique
        for i, cmd in enumerate(unique, 1):
            print(f"  {i}. {cmd}")
    
    async def cmd_r(self, index: str):
        """执行历史命令"""
        if not hasattr(self, '_history_items') or not self._history_items:
            await self.cmd_history()
        idx = int(index) - 1
        if 0 <= idx < len(self._history_items):
            cmd = self._history_items[idx]
            print(f"> {cmd}")
            await self.execute(cmd)
        else:
            print(f"✗ Invalid index: {index}")
    
    # === 帮助 ===
    async def cmd_help(self, cmd: str = None):
        import sys
        if cmd:
            handler = getattr(self, f"cmd_{cmd}", None)
            if handler and handler.__doc__:
                print(handler.__doc__)
            else:
                print(f"No help for: {cmd}")
            return
        print("""Commands:
  connect [url] [name]  - Connect to CDP
  launch [port] [name]  - Launch browser
  disconnect [name]     - Disconnect
  connections           - List connections
  use <name>            - Switch connection
  status                - Show status

  url                   - Show current URL
  go <url>              - Navigate (auto adds https://)
  back/forward/reload   - Navigation
  pages                 - List all tabs
  page <index>          - Switch to tab

  click <selector>      - Click element
  fill <sel> <val>      - Fill input
  btn <name>            - Click button by name
  txt <text>            - Click by text
  wait <sec|selector>   - Wait

  run <file>            - Load script
  funcs                 - List functions
  shot [name]           - Screenshot
  history [n|pattern]   - Show history
  r <index>             - Run history command

  page.xxx              - Execute Playwright code
  help [cmd]            - Show help
  Ctrl+C                - Cancel
  Ctrl+D                - Exit""")
        sys.stdout.flush()
    
    async def cmd_exit(self):
        self._running = False
    
    async def cmd_quit(self):
        self._running = False
