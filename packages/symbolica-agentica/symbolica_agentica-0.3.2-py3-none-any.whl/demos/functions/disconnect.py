#!/usr/bin/env -S S_M_BASE_URL=http://localhost:2345 uv run python3

import asyncio
import os

from agentica.logging import set_default_agent_listener

set_default_agent_listener(None)

from art import text2art

from agentica import agentic


@agentic(text2art, model="anthropic:claude-sonnet-4.5")
async def greet(name: str) -> str:
    """
    Use the provided function to create a fancy greeting.
    """
    ...


async def main():
    async def crash():
        await asyncio.sleep(1.75)
        print("crashing")
        os._exit(0)

    async def invoke():
        print("invoking")
        return await greet("agentica")

    x = await asyncio.gather(invoke(), crash())
    print(f'{x=}')


if __name__ == "__main__":
    asyncio.run(main())
