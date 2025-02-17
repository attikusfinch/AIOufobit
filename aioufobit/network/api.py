import aiohttp
import json

class API(object):
    async def make_request(url: str, method='get', params=None, data=None, headers=None, text=False):
        """Make async request to url

        Args:
            url (str): _description_
            method (str, optional): get/post. Defaults to 'get'.
            params (dict, optional): q=?. Defaults to None.
            headers (dict, optional): header. Defaults to None.
            text (bool, optional): If true return text else response. Defaults to True.

        Raises:
            ValueError: if request failed

        Returns:
            response: text or response
        """
        async with aiohttp.ClientSession() as session:
            if method == 'get':
                response = await session.get(url, params=params, data=data, headers=headers)
            elif method == 'post':
                response = await session.post(url, params=params, data=data, headers=headers)
            else:
                raise ValueError(f"Invalid request method: {method}")

            if text:
                return await response.text()

            return response

class RPCAPI(object):
    async def make_request(self, method, args=None):
        async with aiohttp.ClientSession() as session:
            session.verify_ssl = self.http_verify
            
            response = await session.post(
                self._url,
                headers=self._headers,
                data=json.dumps(
                        {
                        "method": method, 
                        "params": args or [], 
                        "jsonrpc": "2.0"
                        }
                    ),
                timeout=aiohttp.ClientTimeout(total=10),
            )
            
            return response