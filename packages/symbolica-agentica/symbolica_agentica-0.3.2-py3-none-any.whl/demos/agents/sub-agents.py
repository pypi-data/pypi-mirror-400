#!/usr/bin/env -S S_M_BASE_URL=http://localhost:2345 uv run python3

import asyncio

from agentica import spawn


async def sub_agent[T](return_type: type[T], task: str) -> T:
    agent = await spawn(model="openai:gpt-4o")
    return await agent.call(return_type, task)


async def main():
    agent = await spawn(model="openai:gpt-4o")
    result = await agent.call(
        tuple[int, int],
        "Get one subagent to work out the 32nd power of 3, then another subagent to work out the 34th power, then return both results.",
        sub_agent=sub_agent,
    )
    assert result == (3**32, 3**34)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
