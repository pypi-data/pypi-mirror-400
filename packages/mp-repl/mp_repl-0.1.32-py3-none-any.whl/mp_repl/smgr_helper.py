from typing import Optional, List, Dict, Union
from .smgr_client import SessionManagerClient

class PlaywrightHelper:
    """Playwright 会话管理辅助类
    
    提供便捷的方法来注入、保存、切换会话，以及创建带环境配置的 context。
    """
    
    def __init__(self, client: SessionManagerClient):
        self.client = client
    
    def _normalize_cookies(self, cookies: list) -> list:
        """规范化 cookies 格式，兼容 Playwright"""
        normalized = []
        for c in cookies:
            cookie = c.copy()
            # 修正 sameSite 字段
            if 'sameSite' in cookie:
                same_site = cookie['sameSite']
                if same_site not in ['Strict', 'Lax', 'None']:
                    cookie['sameSite'] = 'Lax'
            # 移除不支持的字段
            cookie.pop('size', None)
            cookie.pop('session', None)
            cookie.pop('priority', None)
            cookie.pop('sameParty', None)
            cookie.pop('sourceScheme', None)
            cookie.pop('sourcePort', None)
            normalized.append(cookie)
        return normalized
    
    # ============ 核心方法 ============
    
    async def inject_session(self, context_or_page, account_id: str, client_type: str = 'browser') -> bool:
        """注入会话到 context 或 page
        
        Args:
            context_or_page: Playwright Context 或 Page 对象
            account_id: 账号 ID
            client_type: 客户端类型，默认 'browser'（与浏览器插件共享）
            
        Returns:
            是否成功注入
        """
        session = self.client.get_session(account_id, client_type)
        if not session:
            return False
        
        # 判断是 context 还是 page
        context = getattr(context_or_page, 'context', None) or context_or_page
        
        # 注入 cookies
        if 'cookies' in session and session['cookies']:
            cookies = self._normalize_cookies(session['cookies'])
            await context.add_cookies(cookies)
        
        # 注入 localStorage（需要先访问域名）
        if 'localStorage' in session and hasattr(context_or_page, 'evaluate'):
            page = context_or_page
            for domain, storage in session['localStorage'].items():
                try:
                    await page.goto(f'https://{domain}')
                    await page.evaluate(f"""(storage) => {{
                        for (const [key, value] of Object.entries(storage)) {{
                            localStorage.setItem(key, value);
                        }}
                    }}""", storage)
                except:
                    pass
        
        return True
    
    async def save_session(self, context_or_page, account_id: str, domains: List[str] = None, client_type: str = 'browser') -> Dict:
        """从 context/page 提取并保存会话
        
        Args:
            context_or_page: Playwright Context 或 Page 对象
            account_id: 账号 ID
            domains: 域名列表（用于过滤 cookies），不传则从账号信息获取
            client_type: 客户端类型，默认 'browser'（与浏览器插件共享）
            
        Returns:
            保存的凭据信息
        """
        # 获取 context
        context = getattr(context_or_page, 'context', None) or context_or_page
        
        # 获取账号关联的域名
        if not domains:
            account = self.client.get_account(account_id)
            domains = account.get('domains', [])
        
        # 提取 cookies
        all_cookies = await context.cookies()
        
        # 按域名过滤
        if domains:
            def match_domain(cookie_domain, patterns):
                for p in patterns:
                    p = p.lstrip('.')
                    cd = cookie_domain.lstrip('.')
                    if cd == p or cd.endswith('.' + p) or p.endswith(cd):
                        return True
                return False
            cookies = [c for c in all_cookies if match_domain(c.get('domain', ''), domains)]
        else:
            cookies = all_cookies
        
        session_data = {'cookies': cookies}
        
        # 如果是 page，尝试提取 localStorage
        if hasattr(context_or_page, 'evaluate'):
            page = context_or_page
            try:
                local_storage = await page.evaluate("""() => {
                    const items = {};
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        items[key] = localStorage.getItem(key);
                    }
                    return items;
                }""")
                if local_storage:
                    url = page.url
                    domain = url.split('/')[2] if '/' in url else url
                    session_data['localStorage'] = {domain: local_storage}
            except:
                pass
        
        # 获取当前指纹 ID（如果有）
        cred = self.client.get_credential(account_id, client_type)
        fingerprint_id = cred.get('fingerprint_id') if cred else None
        
        return self.client.save_session(account_id, session_data, client_type, fingerprint_id)
    
    async def switch_session(
        self, 
        context, 
        new_account_id: str, 
        save_current: bool = False, 
        current_account_id: str = None,
        client_type: str = 'browser'
    ) -> bool:
        """切换会话
        
        Args:
            context: Playwright Context 对象
            new_account_id: 新账号 ID
            save_current: 是否保存当前会话
            current_account_id: 当前账号 ID（save_current=True 时必需）
            client_type: 客户端类型，默认 'browser'（与浏览器插件共享）
            
        Returns:
            是否成功切换
        """
        # 保存当前会话
        if save_current and current_account_id:
            await self.save_session(context, current_account_id, client_type=client_type)
        
        # 获取新会话
        session = self.client.get_session(new_account_id, client_type)
        if not session:
            return False
        
        # 获取新账号的域名
        account = self.client.get_account(new_account_id)
        domains = account.get('domains', [])
        
        # 清理旧 cookies（只清理相关域名）
        if domains:
            all_cookies = await context.cookies()
            for cookie in all_cookies:
                cookie_domain = cookie.get('domain', '').lstrip('.')
                if any(d.lstrip('.') in cookie_domain or cookie_domain in d.lstrip('.') for d in domains):
                    await context.clear_cookies(domain=cookie['domain'])
        
        # 注入新 cookies
        if 'cookies' in session and session['cookies']:
            cookies = self._normalize_cookies(session['cookies'])
            await context.add_cookies(cookies)
        
        return True
    
    async def create_context(
        self, 
        browser, 
        account_id: str, 
        inject_session: bool = True,
        apply_proxy: bool = True,
        apply_fingerprint: bool = True,
        client_type: str = 'browser',
        **context_options
    ):
        """创建带环境配置的 context
        
        Args:
            browser: Playwright Browser 对象
            account_id: 账号 ID
            inject_session: 是否自动注入会话，默认 True
            apply_proxy: 是否应用代理配置，默认 True
            apply_fingerprint: 是否应用指纹配置，默认 True
            client_type: 客户端类型，默认 'browser'（与浏览器插件共享）
            **context_options: 传递给 browser.new_context() 的参数
            
        Returns:
            Playwright Context 对象
        """
        # 获取账号信息
        account = self.client.get_account(account_id)
        
        # 获取代理配置
        if apply_proxy and account.get('proxy_id'):
            try:
                proxy = self.client.get_proxy(account['proxy_id'])
                proxy_config = {
                    'server': f"{proxy['type']}://{proxy['host']}:{proxy['port']}"
                }
                if proxy.get('username'):
                    proxy_config['username'] = proxy['username']
                if proxy.get('password'):
                    proxy_config['password'] = proxy['password']
                context_options['proxy'] = proxy_config
            except:
                pass
        
        # 获取指纹配置
        if apply_fingerprint:
            cred = self.client.get_credential(account_id, client_type)
            if cred and cred.get('fingerprint_id'):
                try:
                    fp = self.client.get_fingerprint(cred['fingerprint_id'])
                    fp_config = fp.get('config', {})
                    
                    # 应用指纹配置
                    if 'userAgent' in fp_config:
                        context_options['user_agent'] = fp_config['userAgent']
                    if 'viewport' in fp_config:
                        context_options['viewport'] = fp_config['viewport']
                    if 'screen' in fp_config:
                        context_options['screen'] = fp_config['screen']
                    if 'locale' in fp_config:
                        context_options['locale'] = fp_config['locale']
                    if 'timezone_id' in fp_config:
                        context_options['timezone_id'] = fp_config['timezone_id']
                    if 'geolocation' in fp_config:
                        context_options['geolocation'] = fp_config['geolocation']
                        context_options['permissions'] = ['geolocation']
                except:
                    pass
        
        # 创建 context
        context = await browser.new_context(**context_options)
        
        # 注入会话
        if inject_session:
            await self.inject_session(context, account_id, client_type)
        
        return context
    
    # ============ 便捷方法 ============
    
    def get_environment(self, account_id: str, client_type: str = 'browser') -> Dict:
        """获取账号的环境配置（代理、指纹等）
        
        Args:
            account_id: 账号 ID
            client_type: 客户端类型，默认 'browser'（与浏览器插件共享）
        
        Returns:
            {
                'proxy': {...},
                'fingerprint': {...}
            }
        """
        result = {}
        
        # 获取账号信息
        account = self.client.get_account(account_id)
        
        # 获取代理
        if account.get('proxy_id'):
            try:
                result['proxy'] = self.client.get_proxy(account['proxy_id'])
            except:
                pass
        
        # 获取指纹
        cred = self.client.get_credential(account_id, client_type)
        if cred and cred.get('fingerprint_id'):
            try:
                result['fingerprint'] = self.client.get_fingerprint(cred['fingerprint_id'])
            except:
                pass
        
        return result
