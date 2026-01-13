import httpx
from pydantic import HttpUrl

from deno_sandbox.options import Options, get_internal_options


class AsyncConsoleClient:
    def __init__(self, options: Options):
        self.__options = get_internal_options(options or Options())

    async def post(self, path: str, data: any) -> dict:
        async with httpx.AsyncClient() as client:
            req_url = HttpUrl(self.__options.console_url, path=path)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.__options.token}",
            }
            response = await client.post(req_url, headers=headers, json=data)
            response.raise_for_status()
            return await response.json()

    async def get(self, path: str, search: dict | None = None) -> dict:
        async with httpx.AsyncClient() as client:
            req_url = HttpUrl(self.__options.console_url, path=path, search=search)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.__options.token}",
            }
            response = await client.get(req_url, headers=headers)
            response.raise_for_status()
            return await response.json()

    async def delete(self, path: str) -> None:
        async with httpx.AsyncClient() as client:
            req_url = HttpUrl(self.__options.console_url, path=path)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.__options.token}",
            }
            response = await client.delete(req_url, headers=headers)
            response.raise_for_status()
