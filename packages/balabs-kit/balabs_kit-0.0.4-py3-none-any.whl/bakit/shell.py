# ruff: noqa: T100
import asyncio
import os

from IPython.terminal.embed import InteractiveShellEmbed
from tortoise import Tortoise


def start_ipython_shell(orm_config, extra_ns=None, banner=None):
    """
    Async shell helper:
    - initializes Tortoise with orm_config
    - starts IPython if available (with top-level await support)
    - falls back to stdlib interactive shell otherwise
    - always closes DB connections when done
    """
    asyncio.run(Tortoise.init(config=orm_config))

    if banner is None:
        banner = "Tortoise shell. If IPython is installed, top-level await should work."

    ns = {
        "Tortoise": Tortoise,
        "os": os,
    }
    if extra_ns:
        ns.update(extra_ns)

    try:
        shell = InteractiveShellEmbed(banner2=banner)
        shell(local_ns=ns, global_ns=ns)
    finally:
        asyncio.run(Tortoise.close_connections())
