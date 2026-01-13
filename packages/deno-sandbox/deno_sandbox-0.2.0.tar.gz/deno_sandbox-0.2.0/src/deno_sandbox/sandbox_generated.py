# ATTENTION: This file is auto-generated. Do not edit it manually.

from pydantic import BaseModel, ConfigDict, validate_call
from pydantic.alias_generators import to_camel
from typing import Any
from typing_extensions import Literal

from deno_sandbox.rpc import AsyncRpcClient, RpcClient


class AbortArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    abort_id: int


class ReadFileArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    path: str
    abort_id: int | None = None


class ReadTextFileArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    path: str
    abort_id: int | None = None


class ReadDirArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    path: str


class RemoveOptions(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    recursive: bool | None = None


class RemoveArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    path: str
    options: RemoveOptions | None = None


class MkdirOptions(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    recursive: bool | None = None
    mode: int | None = None


class MkdirArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    path: str
    options: MkdirOptions | None = None


class RenameArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    old_path: str
    new_path: str


class CopyFileArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    from_path: str
    to_path: str


class LinkArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    target: str
    path: str


class LstatArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    path: str


class LstatResult(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    is_file: bool
    is_directory: bool
    is_symlink: bool
    size: int
    mtime: str
    atime: str
    birthtime: str
    ctime: str
    mode: int
    dev: int
    ino: int
    nlink: int
    uid: int
    gid: int
    rdev: int
    blksize: int
    blocks: int
    is_block_device: bool
    is_char_device: bool
    is_fifo: bool
    is_socket: bool


class MakeTempDirOptions(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    dir: str | None = None
    prefix: str | None = None
    suffix: str | None = None


class MakeTempDirArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    options: MakeTempDirOptions | None = None


class MakeTempFileOptions(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    dir: str | None = None
    prefix: str | None = None
    suffix: str | None = None


class MakeTempFileArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    options: MakeTempFileOptions | None = None


class ReadLinkArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    path: str


class RealPathArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    path: str


class SymlinkOptions(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    type: Literal["file", "dir", "junction"] | None = None


class SymlinkArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    target: str
    path: str
    options: SymlinkOptions | None = None


class TruncateArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    name: str
    len: int | None = None


class UmaskArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    mask: int | None = None


class UtimeArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    path: str
    atime: str
    mtime: str


class FileOpenOptions(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    read: bool | None = None
    write: bool | None = None
    append: bool | None = None
    truncate: bool | None = None
    create: bool | None = None
    create_new: bool | None = None
    mode: int | None = None


class OpenArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    path: str
    options: FileOpenOptions | None = None


class OpenResult(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    file_handle_id: int


class CreateArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    path: str


class CreateResult(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    file_handle_id: int


class FileCloseArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    file_handle_id: int


class FileLockArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    file_handle_id: int
    exclusive: bool | None = None


class FileReadArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    file_handle_id: int
    length: int


class FileReadResult(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    data: str | None = None


class FileSeekArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    file_handle_id: int
    offset: int | str
    whence: int


class FileSeekResult(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    position: int


class FileStatArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    file_handle_id: int


class FileStatResult(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    is_file: bool
    is_directory: bool
    is_symlink: bool
    size: int
    mtime: str
    atime: str
    birthtime: str
    ctime: str
    mode: int
    dev: int
    ino: int
    nlink: int
    uid: int
    gid: int
    rdev: int
    blksize: int
    blocks: int
    is_block_device: bool
    is_char_device: bool
    is_fifo: bool
    is_socket: bool


class FileSyncArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    file_handle_id: int


class FileSyncDataArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    file_handle_id: int


class FileTruncateArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    file_handle_id: int
    len: int | None = None


class FileUnlockArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    file_handle_id: int


class FileUtimeArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    file_handle_id: int
    atime: str
    mtime: str


class FileWriteArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    file_handle_id: int
    data: str


class FileWriteResult(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    bytes_written: int


class WalkArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    path: str
    max_depth: int | None = None
    include_files: bool | None = None
    include_dirs: bool | None = None
    include_symlinks: bool | None = None
    follow_symlinks: bool | None = None
    canonicalize: bool | None = None
    exts: list[str] | None = None
    match: list[str] | None = None
    skip: list[str] | None = None


class ExpandGlobArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    glob: str
    extended: bool | None = None
    globstar: bool | None = None
    case_insensitive: bool | None = None
    root: str | None = None
    exclude: list[str] | None = None
    include_dirs: bool | None = None
    follow_symlinks: bool | None = None
    canonicalize: bool | None = None


class SpawnArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    command: str
    args: list[str] | None = None
    env: dict[str, str] | None = None
    clear_env: bool | None = None
    cwd: str | None = None
    stdin_stream_id: int | None = None
    stdout: Literal["piped", "null"] = "piped"
    stderr: Literal["piped", "null"] = "piped"


class SpawnResult(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    pid: int
    stdout_stream_id: int | None = None
    stderr_stream_id: int | None = None


class ProcessWaitArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    pid: int
    vscode: bool | None = None


class ProcessWaitResult(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    success: bool
    code: int
    signal: str | None = None


class ProcessKillArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    pid: int
    signal: str | None = None
    vscode: bool | None = None


class RunResult(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    pid: int
    stdout_stream_id: int | None = None
    stderr_stream_id: int | None = None


class DenoHttpWaitArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    pid: int


class SpawnDenoReplArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    env: dict[str, str] | None = None
    clear_env: bool | None = None
    cwd: str | None = None
    stdin_stream_id: int | None = None
    stdout: Literal["piped", "null"] = "piped"
    stderr: Literal["piped", "null"] = "piped"
    script_args: list[str] | None = None


class SpawnDenoReplResult(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    pid: int
    stdout_stream_id: int | None = None
    stderr_stream_id: int | None = None


class DenoReplCloseArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    pid: int


class DenoReplEvalArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    pid: int
    code: str


class DenoReplCallArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    pid: int
    fn: str
    args: list[Any]


class FetchArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    url: str
    method: str
    headers: dict[str, str]
    redirect: Literal["follow", "manual"]
    abort_id: int | None = None
    body_stream_id: int | None = None
    pid: int | None = None


class FetchResult(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    status: int
    status_text: str
    headers: dict[str, str]
    body_stream_id: int | None = None


class VSCodeConnectArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    path: str
    extensions: list[str]
    env: dict[str, str] | None = None
    preview: str | None = None
    disable_stop_button: bool | None = None
    editor_settings: dict[str, Any] | None = None


class VSCodeConnectResult(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    pid: int
    port: int
    stdout_stream_id: int
    stderr_stream_id: int


class EnvGetArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    key: str


class EnvSetArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    key: str
    value: str


class EnvDeleteArgs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    key: str


class WriteFileOptions(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    create: bool | None = None
    append: bool | None = None
    create_new: bool | None = None
    mode: int | None = None


class WriteFileWithContent(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    path: str
    abort_id: int | None = None
    options: WriteFileOptions | None = None
    content: str


class WriteFileWithStream(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    path: str
    abort_id: int | None = None
    options: WriteFileOptions | None = None
    content_stream_id: int


class WriteTextFileWithContent(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    path: str
    abort_id: int | None = None
    options: WriteFileOptions | None = None
    content: str


class WriteTextFileWithStream(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    path: str
    abort_id: int | None = None
    options: WriteFileOptions | None = None
    content_stream_id: int


class ReadDirEntry(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    name: str
    is_file: bool
    is_directory: bool
    is_symlink: bool


class SpawnDenoByEntrypoint(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    env: dict[str, str] | None = None
    clear_env: bool | None = None
    cwd: str | None = None
    stdin_stream_id: int | None = None
    stdout: Literal["piped", "null"] = "piped"
    stderr: Literal["piped", "null"] = "piped"
    script_args: list[str] | None = None
    entrypoint: str


class SpawnDenoByCode(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    env: dict[str, str] | None = None
    clear_env: bool | None = None
    cwd: str | None = None
    stdin_stream_id: int | None = None
    stdout: Literal["piped", "null"] = "piped"
    stderr: Literal["piped", "null"] = "piped"
    script_args: list[str] | None = None
    code: str
    extension: Literal["js", "cjs", "mjs", "ts", "cts", "mts", "jsx", "tsx"]


class ExposeHttpByPort(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    domain: str
    port: int


class ExposeHttpByPid(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    domain: str
    pid: int


class SandboxHandle:
    def __init__(self, rpc: RpcClient, id: str):
        self.id = id
        self._rpc = rpc
        self.fs = SandboxFs(rpc)
        self.process = SandboxProcess(rpc)
        self.deno = SandboxDeno(rpc)
        self.net = SandboxNet(rpc)
        self.vscode = SandboxVscode(rpc)
        self.env = SandboxEnv(rpc)

    @validate_call(validate_return=True)
    def abort(self, args: AbortArgs) -> None:
        value = args.model_dump()
        self._rpc.call("abort", value)


class SandboxFs:
    def __init__(self, rpc: RpcClient):
        self._rpc = rpc

    @validate_call(validate_return=True)
    def read_file(self, args: ReadFileArgs) -> None:
        """Reads the entire contents of a file as bytes."""

        value = args.model_dump()
        self._rpc.call("readFile", value)

    @validate_call(validate_return=True)
    def read_text_file(self, args: ReadTextFileArgs) -> str:
        """Reads the entire contents of a file as an UTF-8 decoded string."""

        value = args.model_dump()
        return self._rpc.call("readTextFile", value)

    @validate_call(validate_return=True)
    def write_file(self, args: WriteFileWithContent | WriteFileWithStream) -> None:
        """Write bytes to file. Creates a new file if needed. Existing files will be overwritten."""

        value = args.model_dump()
        self._rpc.call("writeFile", value)

    @validate_call(validate_return=True)
    def write_text_file(
        self, args: WriteTextFileWithContent | WriteTextFileWithStream
    ) -> None:
        """Write text to file. Creates a new file if needed. Existing files will be overwritten."""

        value = args.model_dump()
        self._rpc.call("writeTextFile", value)

    @validate_call(validate_return=True)
    def read_dir(self, args: ReadDirArgs) -> list[ReadDirEntry]:
        """Read the directory entries at the given path."""

        value = args.model_dump()
        return self._rpc.call("readDir", value)

    @validate_call(validate_return=True)
    def remove(self, args: RemoveArgs) -> None:
        """Remove the file or directory at the given path."""

        value = args.model_dump()
        self._rpc.call("remove", value)

    @validate_call(validate_return=True)
    def mkdir(self, args: MkdirArgs) -> None:
        """Create a new directory at the specified path."""

        value = args.model_dump()
        self._rpc.call("mkdir", value)

    @validate_call(validate_return=True)
    def rename(self, args: RenameArgs) -> None:
        """Rename (move) a file or directory."""

        value = args.model_dump()
        self._rpc.call("rename", value)

    @validate_call(validate_return=True)
    def copy_file(self, args: CopyFileArgs) -> None:
        """Copy a file from one location to another."""

        value = args.model_dump()
        self._rpc.call("copyFile", value)

    @validate_call(validate_return=True)
    def link(self, args: LinkArgs) -> None:
        """Create a hard link pointing to an existing file."""

        value = args.model_dump()
        self._rpc.call("link", value)

    @validate_call(validate_return=True)
    def lstat(self, args: LstatArgs) -> LstatResult:
        """Return file information about a file or directory symlink."""

        value = args.model_dump()
        return self._rpc.call("lstat", value)

    @validate_call(validate_return=True)
    def make_temp_dir(self, args: MakeTempDirArgs) -> str:
        """Create a new temporary directory."""

        value = args.model_dump()
        return self._rpc.call("makeTempDir", value)

    @validate_call(validate_return=True)
    def make_temp_file(self, args: MakeTempFileArgs) -> str:
        """Create a new temporary file."""

        value = args.model_dump()
        return self._rpc.call("makeTempFile", value)

    @validate_call(validate_return=True)
    def read_link(self, args: ReadLinkArgs) -> str:
        """Read the target of a symbolic link."""

        value = args.model_dump()
        return self._rpc.call("readLink", value)

    @validate_call(validate_return=True)
    def real_path(self, args: RealPathArgs) -> str:
        """Return the canonicalized absolute pathname."""

        value = args.model_dump()
        return self._rpc.call("realPath", value)

    @validate_call(validate_return=True)
    def symlink(self, args: SymlinkArgs) -> None:
        """Create a symbolic link."""

        value = args.model_dump()
        self._rpc.call("symlink", value)

    @validate_call(validate_return=True)
    def truncate(self, args: TruncateArgs) -> None:
        """Truncate or extend the specified file to reach a given size."""

        value = args.model_dump()
        self._rpc.call("truncate", value)

    @validate_call(validate_return=True)
    def umask(self, args: UmaskArgs) -> int:
        """Sets the process's file mode creation mask."""

        value = args.model_dump()
        return self._rpc.call("umask", value)

    @validate_call(validate_return=True)
    def utime(self, args: UtimeArgs) -> None:
        """Change the access and modification times of a file."""

        value = args.model_dump()
        self._rpc.call("utime", value)

    @validate_call(validate_return=True)
    def open(self, args: OpenArgs) -> OpenResult:
        """Open a file and return a file handle id."""

        value = args.model_dump()
        return self._rpc.call("open", value)

    @validate_call(validate_return=True)
    def create(self, args: CreateArgs) -> CreateResult:
        """Create a new file and return a file handle id."""

        value = args.model_dump()
        return self._rpc.call("create", value)

    @validate_call(validate_return=True)
    def file_close(self, args: FileCloseArgs) -> None:
        """Close the specified file handle."""

        value = args.model_dump()
        self._rpc.call("fileClose", value)

    @validate_call(validate_return=True)
    def file_lock(self, args: FileLockArgs) -> None:
        value = args.model_dump()
        self._rpc.call("fileLock", value)

    @validate_call(validate_return=True)
    def file_read(self, args: FileReadArgs) -> FileReadResult:
        value = args.model_dump()
        return self._rpc.call("fileRead", value)

    @validate_call(validate_return=True)
    def file_seek(self, args: FileSeekArgs) -> FileSeekResult:
        value = args.model_dump()
        return self._rpc.call("fileSeek", value)

    @validate_call(validate_return=True)
    def file_stat(self, args: FileStatArgs) -> FileStatResult:
        value = args.model_dump()
        return self._rpc.call("fileStat", value)

    @validate_call(validate_return=True)
    def file_sync(self, args: FileSyncArgs) -> None:
        value = args.model_dump()
        self._rpc.call("fileSync", value)

    @validate_call(validate_return=True)
    def file_sync_data(self, args: FileSyncDataArgs) -> None:
        value = args.model_dump()
        self._rpc.call("fileSyncData", value)

    @validate_call(validate_return=True)
    def file_truncate(self, args: FileTruncateArgs) -> None:
        value = args.model_dump()
        self._rpc.call("fileTruncate", value)

    @validate_call(validate_return=True)
    def file_unlock(self, args: FileUnlockArgs) -> None:
        value = args.model_dump()
        self._rpc.call("fileUnlock", value)

    @validate_call(validate_return=True)
    def file_utime(self, args: FileUtimeArgs) -> None:
        value = args.model_dump()
        self._rpc.call("fileUtime", value)

    @validate_call(validate_return=True)
    def file_write(self, args: FileWriteArgs) -> FileWriteResult:
        value = args.model_dump()
        return self._rpc.call("fileWrite", value)

    @validate_call(validate_return=True)
    def walk(self, args: WalkArgs) -> int:
        value = args.model_dump()
        return self._rpc.call("walk", value)

    @validate_call(validate_return=True)
    def expand_glob(self, args: ExpandGlobArgs) -> int:
        value = args.model_dump()
        return self._rpc.call("expandGlob", value)


class SandboxProcess:
    def __init__(self, rpc: RpcClient):
        self._rpc = rpc

    @validate_call(validate_return=True)
    def spawn(self, args: SpawnArgs) -> SpawnResult:
        value = args.model_dump()
        return self._rpc.call("spawn", value)

    @validate_call(validate_return=True)
    def wait(self, args: ProcessWaitArgs) -> ProcessWaitResult:
        value = args.model_dump()
        return self._rpc.call("processWait", value)

    @validate_call(validate_return=True)
    def kill(self, args: ProcessKillArgs) -> None:
        value = args.model_dump()
        self._rpc.call("processKill", value)


class SandboxDeno:
    def __init__(self, rpc: RpcClient):
        self._rpc = rpc

    @validate_call(validate_return=True)
    def run(self, args: SpawnDenoByEntrypoint | SpawnDenoByCode) -> RunResult:
        value = args.model_dump()
        return self._rpc.call("spawnDeno", value)

    @validate_call(validate_return=True)
    def deno_http_wait(self, args: DenoHttpWaitArgs) -> bool:
        value = args.model_dump()
        return self._rpc.call("denoHttpWait", value)

    @validate_call(validate_return=True)
    def spawn_deno_repl(self, args: SpawnDenoReplArgs) -> SpawnDenoReplResult:
        value = args.model_dump()
        return self._rpc.call("spawnDenoRepl", value)

    @validate_call(validate_return=True)
    def deno_repl_close(self, args: DenoReplCloseArgs) -> None:
        value = args.model_dump()
        self._rpc.call("denoReplClose", value)

    @validate_call(validate_return=True)
    def deno_repl_eval(self, args: DenoReplEvalArgs) -> Any:
        value = args.model_dump()
        return self._rpc.call("denoReplEval", value)

    @validate_call(validate_return=True)
    def deno_repl_call(self, args: DenoReplCallArgs) -> Any:
        value = args.model_dump()
        return self._rpc.call("denoReplCall", value)


class SandboxNet:
    def __init__(self, rpc: RpcClient):
        self._rpc = rpc

    @validate_call(validate_return=True)
    def fetch(self, args: FetchArgs) -> FetchResult:
        value = args.model_dump()
        return self._rpc.call("fetch", value)

    @validate_call(validate_return=True)
    def expose_http(self, args: ExposeHttpByPort | ExposeHttpByPid) -> None:
        value = args.model_dump()
        self._rpc.call("exposeHttp", value)


class SandboxVscode:
    def __init__(self, rpc: RpcClient):
        self._rpc = rpc

    @validate_call(validate_return=True)
    def connect(self, args: VSCodeConnectArgs) -> VSCodeConnectResult:
        value = args.model_dump()
        return self._rpc.call("connect", value)


class SandboxEnv:
    def __init__(self, rpc: RpcClient):
        self._rpc = rpc

    @validate_call(validate_return=True)
    def get(self, args: EnvGetArgs) -> str:
        value = args.model_dump()
        return self._rpc.call("envGet", value)

    @validate_call(validate_return=True)
    def set(self, args: EnvSetArgs) -> None:
        value = args.model_dump()
        self._rpc.call("envSet", value)

    @validate_call(validate_return=True)
    def to_object(self, args: None) -> dict[str, str]:
        value = args.model_dump()
        return self._rpc.call("envToObject", value)

    @validate_call(validate_return=True)
    def delete(self, args: EnvDeleteArgs) -> None:
        value = args.model_dump()
        self._rpc.call("envDelete", value)


class AsyncSandboxHandle:
    def __init__(self, rpc: AsyncRpcClient, id: str):
        self.id = id
        self._rpc = rpc
        self.fs = AsyncSandboxFs(rpc)
        self.process = AsyncSandboxProcess(rpc)
        self.deno = AsyncSandboxDeno(rpc)
        self.net = AsyncSandboxNet(rpc)
        self.vscode = AsyncSandboxVscode(rpc)
        self.env = AsyncSandboxEnv(rpc)

    @validate_call(validate_return=True)
    async def abort(self, args: AbortArgs) -> None:
        value = args.model_dump()
        await self._rpc.call("abort", value)


class AsyncSandboxFs:
    def __init__(self, rpc: AsyncRpcClient):
        self._rpc = rpc

    @validate_call(validate_return=True)
    async def read_file(self, args: ReadFileArgs) -> None:
        """Reads the entire contents of a file as bytes."""

        value = args.model_dump()
        await self._rpc.call("readFile", value)

    @validate_call(validate_return=True)
    async def read_text_file(self, args: ReadTextFileArgs) -> str:
        """Reads the entire contents of a file as an UTF-8 decoded string."""

        value = args.model_dump()
        return await self._rpc.call("readTextFile", value)

    @validate_call(validate_return=True)
    async def write_file(
        self, args: WriteFileWithContent | WriteFileWithStream
    ) -> None:
        """Write bytes to file. Creates a new file if needed. Existing files will be overwritten."""

        value = args.model_dump()
        await self._rpc.call("writeFile", value)

    @validate_call(validate_return=True)
    async def write_text_file(
        self, args: WriteTextFileWithContent | WriteTextFileWithStream
    ) -> None:
        """Write text to file. Creates a new file if needed. Existing files will be overwritten."""

        value = args.model_dump()
        await self._rpc.call("writeTextFile", value)

    @validate_call(validate_return=True)
    async def read_dir(self, args: ReadDirArgs) -> list[ReadDirEntry]:
        """Read the directory entries at the given path."""

        value = args.model_dump()
        return await self._rpc.call("readDir", value)

    @validate_call(validate_return=True)
    async def remove(self, args: RemoveArgs) -> None:
        """Remove the file or directory at the given path."""

        value = args.model_dump()
        await self._rpc.call("remove", value)

    @validate_call(validate_return=True)
    async def mkdir(self, args: MkdirArgs) -> None:
        """Create a new directory at the specified path."""

        value = args.model_dump()
        await self._rpc.call("mkdir", value)

    @validate_call(validate_return=True)
    async def rename(self, args: RenameArgs) -> None:
        """Rename (move) a file or directory."""

        value = args.model_dump()
        await self._rpc.call("rename", value)

    @validate_call(validate_return=True)
    async def copy_file(self, args: CopyFileArgs) -> None:
        """Copy a file from one location to another."""

        value = args.model_dump()
        await self._rpc.call("copyFile", value)

    @validate_call(validate_return=True)
    async def link(self, args: LinkArgs) -> None:
        """Create a hard link pointing to an existing file."""

        value = args.model_dump()
        await self._rpc.call("link", value)

    @validate_call(validate_return=True)
    async def lstat(self, args: LstatArgs) -> LstatResult:
        """Return file information about a file or directory symlink."""

        value = args.model_dump()
        return await self._rpc.call("lstat", value)

    @validate_call(validate_return=True)
    async def make_temp_dir(self, args: MakeTempDirArgs) -> str:
        """Create a new temporary directory."""

        value = args.model_dump()
        return await self._rpc.call("makeTempDir", value)

    @validate_call(validate_return=True)
    async def make_temp_file(self, args: MakeTempFileArgs) -> str:
        """Create a new temporary file."""

        value = args.model_dump()
        return await self._rpc.call("makeTempFile", value)

    @validate_call(validate_return=True)
    async def read_link(self, args: ReadLinkArgs) -> str:
        """Read the target of a symbolic link."""

        value = args.model_dump()
        return await self._rpc.call("readLink", value)

    @validate_call(validate_return=True)
    async def real_path(self, args: RealPathArgs) -> str:
        """Return the canonicalized absolute pathname."""

        value = args.model_dump()
        return await self._rpc.call("realPath", value)

    @validate_call(validate_return=True)
    async def symlink(self, args: SymlinkArgs) -> None:
        """Create a symbolic link."""

        value = args.model_dump()
        await self._rpc.call("symlink", value)

    @validate_call(validate_return=True)
    async def truncate(self, args: TruncateArgs) -> None:
        """Truncate or extend the specified file to reach a given size."""

        value = args.model_dump()
        await self._rpc.call("truncate", value)

    @validate_call(validate_return=True)
    async def umask(self, args: UmaskArgs) -> int:
        """Sets the process's file mode creation mask."""

        value = args.model_dump()
        return await self._rpc.call("umask", value)

    @validate_call(validate_return=True)
    async def utime(self, args: UtimeArgs) -> None:
        """Change the access and modification times of a file."""

        value = args.model_dump()
        await self._rpc.call("utime", value)

    @validate_call(validate_return=True)
    async def open(self, args: OpenArgs) -> OpenResult:
        """Open a file and return a file handle id."""

        value = args.model_dump()
        return await self._rpc.call("open", value)

    @validate_call(validate_return=True)
    async def create(self, args: CreateArgs) -> CreateResult:
        """Create a new file and return a file handle id."""

        value = args.model_dump()
        return await self._rpc.call("create", value)

    @validate_call(validate_return=True)
    async def file_close(self, args: FileCloseArgs) -> None:
        """Close the specified file handle."""

        value = args.model_dump()
        await self._rpc.call("fileClose", value)

    @validate_call(validate_return=True)
    async def file_lock(self, args: FileLockArgs) -> None:
        value = args.model_dump()
        await self._rpc.call("fileLock", value)

    @validate_call(validate_return=True)
    async def file_read(self, args: FileReadArgs) -> FileReadResult:
        value = args.model_dump()
        return await self._rpc.call("fileRead", value)

    @validate_call(validate_return=True)
    async def file_seek(self, args: FileSeekArgs) -> FileSeekResult:
        value = args.model_dump()
        return await self._rpc.call("fileSeek", value)

    @validate_call(validate_return=True)
    async def file_stat(self, args: FileStatArgs) -> FileStatResult:
        value = args.model_dump()
        return await self._rpc.call("fileStat", value)

    @validate_call(validate_return=True)
    async def file_sync(self, args: FileSyncArgs) -> None:
        value = args.model_dump()
        await self._rpc.call("fileSync", value)

    @validate_call(validate_return=True)
    async def file_sync_data(self, args: FileSyncDataArgs) -> None:
        value = args.model_dump()
        await self._rpc.call("fileSyncData", value)

    @validate_call(validate_return=True)
    async def file_truncate(self, args: FileTruncateArgs) -> None:
        value = args.model_dump()
        await self._rpc.call("fileTruncate", value)

    @validate_call(validate_return=True)
    async def file_unlock(self, args: FileUnlockArgs) -> None:
        value = args.model_dump()
        await self._rpc.call("fileUnlock", value)

    @validate_call(validate_return=True)
    async def file_utime(self, args: FileUtimeArgs) -> None:
        value = args.model_dump()
        await self._rpc.call("fileUtime", value)

    @validate_call(validate_return=True)
    async def file_write(self, args: FileWriteArgs) -> FileWriteResult:
        value = args.model_dump()
        return await self._rpc.call("fileWrite", value)

    @validate_call(validate_return=True)
    async def walk(self, args: WalkArgs) -> int:
        value = args.model_dump()
        return await self._rpc.call("walk", value)

    @validate_call(validate_return=True)
    async def expand_glob(self, args: ExpandGlobArgs) -> int:
        value = args.model_dump()
        return await self._rpc.call("expandGlob", value)


class AsyncSandboxProcess:
    def __init__(self, rpc: AsyncRpcClient):
        self._rpc = rpc

    @validate_call(validate_return=True)
    async def spawn(self, args: SpawnArgs) -> SpawnResult:
        value = args.model_dump()
        return await self._rpc.call("spawn", value)

    @validate_call(validate_return=True)
    async def wait(self, args: ProcessWaitArgs) -> ProcessWaitResult:
        value = args.model_dump()
        return await self._rpc.call("processWait", value)

    @validate_call(validate_return=True)
    async def kill(self, args: ProcessKillArgs) -> None:
        value = args.model_dump()
        await self._rpc.call("processKill", value)


class AsyncSandboxDeno:
    def __init__(self, rpc: AsyncRpcClient):
        self._rpc = rpc

    @validate_call(validate_return=True)
    async def run(self, args: SpawnDenoByEntrypoint | SpawnDenoByCode) -> RunResult:
        value = args.model_dump()
        return await self._rpc.call("spawnDeno", value)

    @validate_call(validate_return=True)
    async def deno_http_wait(self, args: DenoHttpWaitArgs) -> bool:
        value = args.model_dump()
        return await self._rpc.call("denoHttpWait", value)

    @validate_call(validate_return=True)
    async def spawn_deno_repl(self, args: SpawnDenoReplArgs) -> SpawnDenoReplResult:
        value = args.model_dump()
        return await self._rpc.call("spawnDenoRepl", value)

    @validate_call(validate_return=True)
    async def deno_repl_close(self, args: DenoReplCloseArgs) -> None:
        value = args.model_dump()
        await self._rpc.call("denoReplClose", value)

    @validate_call(validate_return=True)
    async def deno_repl_eval(self, args: DenoReplEvalArgs) -> Any:
        value = args.model_dump()
        return await self._rpc.call("denoReplEval", value)

    @validate_call(validate_return=True)
    async def deno_repl_call(self, args: DenoReplCallArgs) -> Any:
        value = args.model_dump()
        return await self._rpc.call("denoReplCall", value)


class AsyncSandboxNet:
    def __init__(self, rpc: AsyncRpcClient):
        self._rpc = rpc

    @validate_call(validate_return=True)
    async def fetch(self, args: FetchArgs) -> FetchResult:
        value = args.model_dump()
        return await self._rpc.call("fetch", value)

    @validate_call(validate_return=True)
    async def expose_http(self, args: ExposeHttpByPort | ExposeHttpByPid) -> None:
        value = args.model_dump()
        await self._rpc.call("exposeHttp", value)


class AsyncSandboxVscode:
    def __init__(self, rpc: AsyncRpcClient):
        self._rpc = rpc

    @validate_call(validate_return=True)
    async def connect(self, args: VSCodeConnectArgs) -> VSCodeConnectResult:
        value = args.model_dump()
        return await self._rpc.call("connect", value)


class AsyncSandboxEnv:
    def __init__(self, rpc: AsyncRpcClient):
        self._rpc = rpc

    @validate_call(validate_return=True)
    async def get(self, args: EnvGetArgs) -> str:
        value = args.model_dump()
        return await self._rpc.call("envGet", value)

    @validate_call(validate_return=True)
    async def set(self, args: EnvSetArgs) -> None:
        value = args.model_dump()
        await self._rpc.call("envSet", value)

    @validate_call(validate_return=True)
    async def to_object(self, args: None) -> dict[str, str]:
        value = args.model_dump()
        return await self._rpc.call("envToObject", value)

    @validate_call(validate_return=True)
    async def delete(self, args: EnvDeleteArgs) -> None:
        value = args.model_dump()
        await self._rpc.call("envDelete", value)
