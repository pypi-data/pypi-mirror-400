import asyncio
import base64
import json
from typing import Any, Dict, Optional
from pydantic import BaseModel
from websockets import ConnectionClosed

from deno_sandbox.bridge import AsyncBridge
from deno_sandbox.transport import Transport


class RpcRequest(BaseModel):
    method: str
    params: Dict[str, Any]
    id: int
    jsonrpc: str = "2.0"


class RpcResult[T](BaseModel):
    ok: Optional[T] = None
    error: Optional[Any] = None


class RpcResponse[T](BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[RpcResult[T]] = None
    error: Dict[str, Any] | None = None
    id: int


class AsyncRpcClient:
    def __init__(self, transport: Transport):
        self._transport = transport
        self._id = 0
        self._pending_requests: Dict[int, asyncio.Future[Any]] = {}
        self._listen_task = asyncio.create_task(self._listener())
        self._pending_processes: Dict[int, asyncio.StreamReader] = {}

    async def close(self):
        await self._transport.close()

    async def call(self, method: str, params: Dict[str, Any]) -> Any:
        req_id = self._id + 1
        self._id = req_id

        payload = RpcRequest(method=method, params=params, id=req_id)

        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._pending_requests[req_id] = future

        await self._transport.send(payload.model_dump_json())

        raw_response = await future
        response = RpcResponse[Any](**raw_response)

        if response.error:
            raise Exception(response.error)

        if response.result and response.result.error:
            raise Exception(f"Application Error: {response.result.error}")

        return response.result.ok if response.result else None

    async def _listener(self) -> None:
        try:
            async for raw in self._transport:
                data = json.loads(raw)
                req_id = data.get("id")

                if req_id is not None and req_id in self._pending_requests:
                    future = self._pending_requests.pop(req_id)
                    if not future.done():
                        future.set_result(data)

                elif "method" in data:
                    method = data["method"]
                    params = data.get("params", {})

                    if method == "$sandbox.stream.enqueue":
                        stream_id = params.get("streamId")
                        chunk = base64.b64decode(params.get("data", ""))
                        stream = self._pending_processes.get(stream_id)
                        if stream:
                            stream.feed_data(chunk)
                    elif method == "$sandbox.stream.end":
                        stream_id = params.get("streamId")
                        stream = self._pending_processes.get(stream_id)
                        if stream:
                            stream.feed_eof()
                            del self._pending_processes[stream_id]

        except ConnectionClosed:
            pass
        except Exception as e:
            for future in self._pending_requests.values():
                if not future.done():
                    future.set_exception(e)


class RpcClient:
    def __init__(self, async_client: AsyncRpcClient, bridge: AsyncBridge):
        self._async_client = async_client
        self._bridge = bridge

    def call(self, method: str, params: Dict[str, Any]) -> Any:
        return self._bridge.run(self._async_client.call(method, params))

    def close(self):
        self._bridge.run(self._async_client.close())
