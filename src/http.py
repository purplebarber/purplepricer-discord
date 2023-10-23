from json import dumps
from aiohttp import ClientSession, ClientTimeout


class HTTP:
    def __init__(self):
        self.session = ClientSession()  # ClientSession for making HTTP requests
        self.timeout = ClientTimeout(total=10) # 10 second timeout for requests

    # GET and POST methods for making HTTP requests
    async def get(self, url: str, **kwargs) -> dict:
        kwargs["headers"] = kwargs.get("headers", dict())
        kwargs["params"] = kwargs.get("params", dict())
        kwargs["json"] = kwargs.get("json", dumps(dict()))
        kwargs["timeout"] = kwargs.get("timeout", self.timeout)

        try:
            async with self.session.get(url, **kwargs) as response:
                if response.status == 200:  # if the response is OK
                    return await response.json()

                else:
                    print(f"HTTP error {response.status} for {response.url}")
                    return dict()

        except Exception as e:
            print(f"Error making GET request to {url}: {e}")
            return dict()

    async def post(self, url: str, **kwargs) -> dict:
        kwargs["headers"] = kwargs.get("headers", dict())
        kwargs["params"] = kwargs.get("params", dict())
        kwargs["json"] = kwargs.get("json", dict())
        kwargs["timeout"] = kwargs.get("timeout", self.timeout)
        try:
            await self.session.post(url, **kwargs)
            return dict()

        except Exception as e:
            print(f"Error making POST request to {url}: {e}")
            return dict()

    async def close(self):
        await self.session.close()