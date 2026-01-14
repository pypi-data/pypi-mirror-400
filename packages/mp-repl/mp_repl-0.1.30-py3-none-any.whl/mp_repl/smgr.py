#!/usr/bin/env python3
"""Session Manager 客户端"""
import httpx
from typing import Optional, List, Dict

class SmgrClient:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.headers = {'X-API-Key': api_key} if api_key else {}
    
    def _request(self, method: str, path: str, **kwargs) -> Dict:
        url = f"{self.base_url}{path}"
        try:
            r = httpx.request(method, url, headers=self.headers, timeout=30, verify=False, **kwargs)
            r.raise_for_status()
            return r.json()
        except httpx.ConnectError as e:
            raise Exception(f"Cannot connect to {self.base_url}: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP {e.response.status_code}: {e.response.text[:100]}")
    
    def list_accounts(self, platform: str = None, limit: int = 50) -> List[Dict]:
        params = {'limit': limit}
        if platform:
            params['platform'] = platform
        return self._request('GET', '/accounts', params=params).get('data', [])
    
    def get_account(self, account_id: str) -> Dict:
        return self._request('GET', f'/accounts/{account_id}').get('data', {})
    
    def get_session(self, account_id: str) -> Optional[Dict]:
        try:
            r = self._request('GET', f'/accounts/{account_id}/credentials/browser')
            return r.get('data', {}).get('credential_data')
        except:
            return None
    
    def save_session(self, account_id: str, session_data: Dict) -> bool:
        try:
            self._request('POST', f'/accounts/{account_id}/credentials', json={
                'client_type': 'browser',
                'credential_type': 'session',
                'credential_data': session_data
            })
            return True
        except:
            return False
