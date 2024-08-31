import httpx
from app.common.core.logger import get_logger
from app.common.core.config import config

logger = get_logger(__name__)

class AsyncHttpClient:
    _client = httpx.AsyncClient(limits=httpx.Limits(
        max_keepalive_connections=config.MAX_KEEPALIVE_CONNECTIONS, 
        max_connections=config.MAX_CONNECTIONS))
    
    def __init__(self) -> None:
        pass

    async def request(self,
                      method,
                      url,
                      headers=None,
                      params=None,
                      data=None,
                      json=None,
                      files=None,
                      timeout=None,
                      response_type="text",
                      follow_redirects=False):
        try:
            status = repr(self._client._transport._pool)
            logger.info(f"httpx normal client status request url: {url}, status: {status}")
            response = await self._client.request(method, url, headers=headers, params=params, data=data, json=json, files=files, timeout=timeout, follow_redirects=follow_redirects)
            if response_type == "text":
                return response.text
            elif response_type == "json":
                return response.json()
            elif response_type == "raw":
                return response
            else:
                raise ValueError("Unsupported response type")
        except Exception as ex:
            logger.warning(f"AsyncHttpClient.request url:{url} ex:{ex}")
        finally:
            logger.info(f"AsyncHttpClient.request url:{url} finally")


async def test():
    client = AsyncHttpClient()
    headers = {"User-Agent": "Custom User Agent"}
    text_response = await client.request("get", "https://jsonplaceholder.typicode.com/posts/1", timeout=5, headers=headers, response_type="json")
    print("Text response:")
    print(text_response)


if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
