# mp-repl

Playwright 交互式调试工具 - 提升自动化脚本开发效率

## 安装

```bash
pip install mp-repl
playwright install chromium
```

## 快速开始

```bash
# 启动 REPL
pw-repl

# 连接浏览器
pw> connect

# 页面操作
pw> go https://example.com
pw> btn 'Submit'
pw> fill '#email' 'test@example.com'

# 执行 Playwright 代码
pw> page.locator('button').click()

# 加载并执行脚本
pw> run my_script.py
pw> my_function()
```

## 功能

- 命令式操作：`btn`, `click`, `fill`, `go` 等快捷命令
- Playwright 直接执行：`page.xxx`, `browser.xxx`
- 脚本执行：加载 Python 脚本，函数可直接调用
- 多连接管理：同时连接多个浏览器
- 会话管理：集成 s-mgr 账号切换

## 文档

详见 [docs/design.md](docs/design.md)

## License

MIT
