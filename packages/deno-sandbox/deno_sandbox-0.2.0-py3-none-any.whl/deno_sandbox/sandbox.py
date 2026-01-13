import asyncio
from contextlib import asynccontextmanager, contextmanager
from dataclasses import asdict, dataclass, field
import json
from typing import AsyncIterator
import uuid
from pydantic import BaseModel, Field
from typing_extensions import Literal

from deno_sandbox.bridge import AsyncBridge
from deno_sandbox.options import Options, get_internal_options
from deno_sandbox.rpc import AsyncRpcClient, RpcClient
from deno_sandbox.sandbox_generated import (
    AsyncSandboxHandle as GeneratedAsyncSandboxHandle,
    SpawnArgs,
    AsyncSandboxProcess as GeneratedAsyncSandboxProcess,
    SandboxHandle,
)
from deno_sandbox.transport import (
    Transport,
    WebSocketTransportFactory,
)


type Mode = Literal["connect", "create"]
type StdIo = Literal["piped", "null"]


@dataclass(frozen=True)
class SandboxCreateOptions:
    env: dict[str, str] | None = None
    """Environment variables to set in the sandbox."""
    memory_mb: int | None = 1024
    """Memory limit for the sandbox in megabytes (default: 1024)."""
    labels: dict[str, str] | None = None
    """
    Labels to set on the sandbox. Up to 5 labels can be specified.
    Each label key must be at most 64 bytes, and each label value must be at most 128 bytes.
    """
    volumes: dict[str, str] | None = None
    """
    Volumes to mount on the sandbox.
    The key is the mount path inside the sandbox, and the value is
    the volume ID or slug
    """


@dataclass(frozen=True)
class SandboxConnectOptions:
    id: uuid.UUID
    """Unique id of the sandbox."""


@dataclass
class SandboxRequestResult:
    revision_id: str


@dataclass
class SandboxDeployOptions:
    path: str | None = None
    entrypoint: str = "main.ts"
    args: list[str] = field(default_factory=list)


@dataclass
class SandboxInfo:
    sandboxId: uuid.UUID
    """The ID of the sandbox."""
    createdAt: str
    """The creation time of the sandbox."""
    region: str
    """The region where the sandbox is running."""


@dataclass
class AppConfig:
    sandbox_id: str
    mode: Mode
    stop_at_ms: int | None
    labels: dict[str, str] | None
    memory_mb: int | None


class Sandbox:
    def __init__(self, options=None):
        self._bridge = AsyncBridge()
        self._async_sandbox = AsyncSandbox(options)

    @contextmanager
    def create(self, options=None):
        async_cm = self._async_sandbox.create(options)
        async_handle = self._bridge.run(async_cm.__aenter__())

        rpc = RpcClient(async_handle._rpc, self._bridge)

        try:
            yield SandboxHandle(rpc, async_handle.id)
        finally:
            self._bridge.run(async_cm.__aexit__(None, None, None))

    def close(self):
        self._bridge.stop()


class AsyncSandboxProcess(GeneratedAsyncSandboxProcess):
    async def spawn(self, args: SpawnArgs) -> RemoteProcess:
        result: SpawnResult = await super().spawn(args)
        return RemoteProcess(result, self._rpc)


class AsyncSandboxHandle(GeneratedAsyncSandboxHandle):
    def __init__(self, rpc: AsyncRpcClient, sandbox_id: str):
        super().__init__(rpc, sandbox_id)
        self.process = AsyncSandboxProcess(rpc)


class AsyncSandbox:
    def __init__(
        self,
        options: Options | None = None,
    ):
        self.__options = get_internal_options(options or Options())
        self._transport_factory = WebSocketTransportFactory()
        self._rpc: AsyncRpcClient | None = None

    async def _init_transport(self, app_config: AppConfig) -> Transport:
        transport = self._transport_factory.create_transport()

        headers = {
            "Authorization": f"Bearer {self.__options.token}",
            "x-denodeploy-config-v2": json.dumps(asdict(app_config)),
        }

        await transport.connect(url=self.__options.sandbox_ws_url, headers=headers)
        return transport

    @asynccontextmanager
    async def create(
        self, options: SandboxCreateOptions | None = None
    ) -> AsyncIterator[AsyncSandboxHandle]:
        """Creates a new sandbox instance."""

        sandbox_id = str(uuid.uuid4())
        app_config = AppConfig(
            sandbox_id=sandbox_id,
            mode="create",
            stop_at_ms=None,
            labels=options.labels if options else None,
            memory_mb=options.memory_mb if options else None,
        )
        transport = await self._init_transport(app_config)

        try:
            self._rpc = AsyncRpcClient(transport)
            yield AsyncSandboxHandle(self._rpc, sandbox_id)
        finally:
            await transport.close()

    @asynccontextmanager
    async def connect(
        self, options: SandboxConnectOptions
    ) -> AsyncIterator[AsyncSandboxHandle]:
        """Connects to an existing sandbox instance."""

        sandbox_id = str(options.id)
        app_config = AppConfig(
            sandbox_id=sandbox_id,
            mode="connect",
            stop_at_ms=None,
            labels=None,
            memory_mb=None,
        )
        transport = await self._init_transport(app_config)

        try:
            rpc = AsyncRpcClient(transport)
            yield AsyncSandboxHandle(rpc, sandbox_id)
        finally:
            await transport.close()


class SpawnResult(BaseModel):
    pid: int
    stdout_stream_id: int | None = Field(default=None, alias="stdoutStreamId")
    stderr_stream_id: int | None = Field(default=None, alias="stderrStreamId")


class ProcessExit(BaseModel):
    code: int


class RemoteProcess:
    def __init__(self, res: SpawnResult, rpc: AsyncRpcClient):
        self.pid = res.pid
        self._stdout_stream_id = res.stdout_stream_id
        self._stderr_stream_id = res.stderr_stream_id
        self.returncode: int | None = None

        self.stdout = asyncio.StreamReader()
        self.stderr = asyncio.StreamReader()
        self._wait_task = asyncio.create_task(
            rpc.call("processWait", {"pid": self.pid})
        )

        rpc._pending_processes[self._stdout_stream_id] = self.stdout
        rpc._pending_processes[self._stderr_stream_id] = self.stderr

    async def wait(self) -> int:
        raw = await self._wait_task
        result = ProcessExit.model_validate(raw)
        self.returncode = result.code
        return self.returncode
