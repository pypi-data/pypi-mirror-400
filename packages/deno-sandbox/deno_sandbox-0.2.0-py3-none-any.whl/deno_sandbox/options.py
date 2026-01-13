from dataclasses import dataclass
import os

from urllib.parse import urlparse

from pydantic_core import Url


@dataclass(frozen=True)
class Options:
    token: str | Url | None = None
    regions: list[str] | None = None


@dataclass
class InternalOptions:
    sandbox_ws_url: Url
    console_url: Url
    token: Url
    regions: list[str]


def get_internal_options(options: Options) -> InternalOptions:
    options = options or Options()

    url = urlparse(
        os.environ.get("DENO_DEPLOY_URL", "https://ams.sandbox-api.deno.net")
    )

    token = options.token or os.environ.get("DENO_DEPLOY_TOKEN", "")

    scheme = url.scheme.replace("http", "ws")
    sandbox_ws_url = Url(f"{scheme}://{url.netloc}/api/v2/sandbox/ws?format=json")

    console_url = os.environ.get("DENO_DEPLOY_CONSOLE_URL", "https://console.deno.com")
    parsed_console_url = urlparse(console_url)

    regions = options.regions or os.environ.get(
        "DENO_AVAILABLE_REGIONS", "ams1,ord"
    ).split(",")

    return InternalOptions(
        console_url=parsed_console_url,
        sandbox_ws_url=sandbox_ws_url,
        token=token,
        regions=regions,
    )
