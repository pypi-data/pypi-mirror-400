from deno_sandbox.options import Options, get_internal_options
from deno_sandbox.sandbox import AsyncSandbox
from deno_sandbox.volumes import AsyncVolumes


class AsyncClient:
    def __init__(self, options: Options):
        self._options = get_internal_options(options or Options())
        self.sandbox = AsyncSandbox(options)
        self.volumes = AsyncVolumes(options)
