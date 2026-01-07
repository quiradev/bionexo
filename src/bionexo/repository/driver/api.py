import requests
import aiohttp
import asyncio
from typing import Dict, Any, Optional

class APIDriver:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get('base_url', '')
        self.headers = config.get('headers', {})
        self.timeout = config.get('timeout', 10)
        self.async_mode = config.get('async_mode', False)  # True para async, False para sync

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        if self.async_mode:
            return asyncio.run(self._async_get(endpoint, params))
        else:
            return self._sync_get(endpoint, params)

    def post(self, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict:
        if self.async_mode:
            return asyncio.run(self._async_post(endpoint, data, params, files))
        else:
            return self._sync_post(endpoint, data, params, files)

    def _sync_get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def _sync_post(self, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, headers=self.headers, json=data, params=params, files=files, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    async def _async_get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        async with aiohttp.ClientSession(headers=self.headers, timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()

    async def _async_post(self, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        async with aiohttp.ClientSession(headers=self.headers, timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            # Nota: aiohttp no soporta files directamente como requests; para uploads, usar FormData
            if files:
                from aiohttp import FormData
                form = FormData()
                if data:
                    for k, v in data.items():
                        form.add_field(k, str(v))
                for k, v in files.items():
                    form.add_field(k, v, filename=v.name if hasattr(v, 'name') else 'file')
                async with session.post(url, data=form, params=params) as response:
                    response.raise_for_status()
                    return await response.json()
            else:
                async with session.post(url, json=data, params=params) as response:
                    response.raise_for_status()
                    return await response.json()
