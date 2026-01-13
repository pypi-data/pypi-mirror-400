import httpx
from pydantic import BaseModel
from pydantic_core import Url

from deno_sandbox.console import AsyncConsoleClient
from deno_sandbox.options import Options, get_internal_options


class VolumeCreateOptions(BaseModel):
    slug: str
    region: str
    capacity: int


class VolumeListOptions(BaseModel):
    cursor: str | None = None
    limit: int | None = None
    search: str | None = None


class Volume(BaseModel):
    id: str
    slug: str
    region: str
    capacity: int
    used: int


class AsyncVolumes:
    def __init__(self, options: Options | None = None):
        internal_options = get_internal_options(options or Options())
        self.__client = AsyncConsoleClient(internal_options)

    async def create(self, options: VolumeCreateOptions):
        json = await self.__client.post("/api/v2/volumes", options)
        return Volume(json)

    async def delete(self, id: str) -> None:
        await self.__client.delete(f"/api/v2/volumes/{id}")

    async def get(self, id: str) -> Volume | None:
        try:
            json = await self.__client.get(f"/api/v2/volumes/{id}")
            return Volume(json)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    async def list_all(self, options: VolumeListOptions) -> list[Volume]:
        url = Url("/api/v2/volumes")
        url.build_query(
            {
                "cursor": options.get("cursor", None),
                "limit": options.get("limit", None),
                "search": options.get("search", None),
            }
        )
        json = await self.__client.get(str(url))
        return [Volume(item) for item in json["volumes"]]
