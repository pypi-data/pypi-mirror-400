#!/usr/bin/env -S S_M_BASE_URL=http://localhost:2345 uv run python3

import asyncio
import os

from agentica import spawn
from agentica.std.web import web_search

assert os.getenv("EXA_API_KEY"), "You need a key!"


async def main():
    agent = await spawn()
    souls: int = await agent.call(
        int,
        "On the 3rd August 1975 a Boeing 707 crashed. How many people were killed?",
        web_search=web_search,
    )
    print(f"Souls onboard: {souls}")


if __name__ == "__main__":
    asyncio.run(main())
