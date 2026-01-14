import requests
from typing import Optional, List, Dict, Any

class SessionManagerClient:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.headers = {}
        if api_key:
            self.headers['X-API-Key'] = api_key
    
    def _request(self, method: str, path: str, **kwargs) -> Dict:
        url = f"{self.base_url}{path}"
        r = requests.request(method, url, headers=self.headers, **kwargs)
        r.raise_for_status()
        return r.json()
    
    # ============ 账号 ============
    
    def list_accounts(
        self, 
        platform: str = None, 
        tag: str = None, 
        search: str = None,
        limit: int = 100,
        offset: int = 0,
        include: List[str] = None
    ) -> List[Dict]:
        """列出账号
        
        Args:
            platform: 平台过滤
            tag: 标签过滤
            search: 搜索关键词
            limit: 每页数量
            offset: 偏移量
            include: 关联查询 ['credentials', 'proxy', 'fingerprint']
        """
        params = {'limit': limit, 'offset': offset}
        if platform:
            params['platform'] = platform
        if tag:
            params['tag'] = tag
        if search:
            params['search'] = search
        if include:
            params['include'] = ','.join(include)
        return self._request('GET', '/accounts', params=params)['data']
    
    def get_account(self, account_id: str) -> Dict:
        return self._request('GET', f'/accounts/{account_id}')['data']
    
    def create_account(
        self, 
        platform: str, 
        username: str, 
        domains: List[str] = None, 
        tags: List[str] = None,
        proxy_id: str = None
    ) -> Dict:
        """创建账号"""
        data = {'platform': platform, 'username': username}
        if domains:
            data['domains'] = domains
        if tags:
            data['tags'] = tags
        if proxy_id:
            data['proxy_id'] = proxy_id
        return self._request('POST', '/accounts', json=data)['data']
    
    def update_account(self, account_id: str, **kwargs) -> Dict:
        """更新账号"""
        return self._request('PUT', f'/accounts/{account_id}', json=kwargs)['data']
    
    def delete_account(self, account_id: str) -> bool:
        """删除账号"""
        self._request('DELETE', f'/accounts/{account_id}')
        return True
    
    def batch_create_accounts(self, accounts: List[Dict]) -> List[Dict]:
        """批量创建账号"""
        return self._request('POST', '/accounts/batch', json=accounts)['data']
    
    def batch_delete_accounts(self, account_ids: List[str]) -> bool:
        """批量删除账号"""
        self._request('DELETE', '/accounts/batch', json=account_ids)
        return True
    
    def export_accounts(self) -> List[Dict]:
        """导出所有账号"""
        return self._request('GET', '/accounts/export')['data']
    
    def import_accounts(self, accounts: List[Dict]) -> List[Dict]:
        """导入账号"""
        return self._request('POST', '/accounts/import', json=accounts)['data']
    
    # ============ 凭据 ============
    
    def get_credential(self, account_id: str, client_type: str = 'browser') -> Optional[Dict]:
        """获取凭据"""
        try:
            return self._request('GET', f'/accounts/{account_id}/credentials/{client_type}')['data']
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def get_credentials_batch(self, account_ids: List[str], client_type: str = 'browser') -> Dict[str, Dict]:
        """批量获取凭据
        
        Returns:
            Dict[account_id, credential_data]
        """
        ids_str = ','.join(account_ids)
        return self._request('GET', f'/credentials/batch', params={
            'account_ids': ids_str,
            'client_type': client_type
        })['data']
    
    def save_credential(
        self, 
        account_id: str, 
        client_type: str, 
        credential_type: str, 
        credential_data: Dict,
        fingerprint_id: str = None
    ) -> Dict:
        """保存凭据"""
        data = {
            'client_type': client_type,
            'credential_type': credential_type,
            'credential_data': credential_data
        }
        if fingerprint_id:
            data['fingerprint_id'] = fingerprint_id
        return self._request('POST', f'/accounts/{account_id}/credentials', json=data)['data']
    
    def delete_credential(self, account_id: str, client_type: str) -> bool:
        """删除凭据"""
        self._request('DELETE', f'/accounts/{account_id}/credentials/{client_type}')
        return True
    
    def update_credential_fingerprint(self, account_id: str, client_type: str, fingerprint_id: str = None) -> Dict:
        """更新凭据指纹"""
        return self._request('PUT', f'/accounts/{account_id}/credentials/{client_type}/fingerprint', json={
            'fingerprint_id': fingerprint_id
        })['data']
    
    # ============ 会话数据快捷方法 ============
    
    def get_session(self, account_id: str, client_type: str = 'browser') -> Optional[Dict]:
        """获取会话数据（cookies, localStorage 等）"""
        cred = self.get_credential(account_id, client_type)
        return cred['credential_data'] if cred else None
    
    def save_session(self, account_id: str, session_data: Dict, client_type: str = 'browser', fingerprint_id: str = None) -> Dict:
        """保存会话数据"""
        return self.save_credential(account_id, client_type, 'session', session_data, fingerprint_id)
    
    # ============ 代理 ============
    
    def list_proxies(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """列出代理"""
        return self._request('GET', '/proxies', params={'limit': limit, 'offset': offset})['data']
    
    def get_proxy(self, proxy_id: str) -> Dict:
        """获取代理"""
        return self._request('GET', f'/proxies/{proxy_id}')['data']
    
    def create_proxy(self, **kwargs) -> Dict:
        """创建代理"""
        return self._request('POST', '/proxies', json=kwargs)['data']
    
    def update_proxy(self, proxy_id: str, **kwargs) -> Dict:
        """更新代理"""
        return self._request('PUT', f'/proxies/{proxy_id}', json=kwargs)['data']
    
    def delete_proxy(self, proxy_id: str) -> bool:
        """删除代理"""
        self._request('DELETE', f'/proxies/{proxy_id}')
        return True
    
    def detect_proxy(self, proxy_type: str, host: str, port: int, username: str = None, password: str = None) -> Dict:
        """检测代理"""
        data = {'type': proxy_type, 'host': host, 'port': port}
        if username:
            data['username'] = username
        if password:
            data['password'] = password
        return self._request('POST', '/proxy/detect', json=data)
    
    # ============ 指纹 ============
    
    def list_fingerprints(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """列出指纹"""
        return self._request('GET', '/fingerprints', params={'limit': limit, 'offset': offset})['data']
    
    def get_fingerprint(self, fingerprint_id: str) -> Dict:
        """获取指纹"""
        return self._request('GET', f'/fingerprints/{fingerprint_id}')['data']
    
    def create_fingerprint(self, **kwargs) -> Dict:
        """创建指纹"""
        return self._request('POST', '/fingerprints', json=kwargs)['data']
    
    def update_fingerprint(self, fingerprint_id: str, **kwargs) -> Dict:
        """更新指纹"""
        return self._request('PUT', f'/fingerprints/{fingerprint_id}', json=kwargs)['data']
    
    def delete_fingerprint(self, fingerprint_id: str) -> bool:
        """删除指纹"""
        self._request('DELETE', f'/fingerprints/{fingerprint_id}')
        return True
    
    # ============ 统计 ============
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self._request('GET', '/stats')
