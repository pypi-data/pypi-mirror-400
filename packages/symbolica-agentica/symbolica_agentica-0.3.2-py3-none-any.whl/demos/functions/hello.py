#!/usr/bin/env -S S_M_BASE_URL=http://localhost:2345 uv run python3

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
    result = await greet("agentica")
    print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
