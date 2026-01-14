#!/usr/bin/env -S S_M_BASE_URL=http://localhost:2345 uv run python3

import asyncio

from agentica import spawn


def ignore(i: int) -> int:
    """Ignore this function."""
    return i


async def main():
    assert False, "JSON mode is not supported yet"
    agent1 = await spawn(model='openai:gpt-4o', mode='json')
    n: int = await agent1.call(int, "What is the meaning of life, numerically?")
    assert isinstance(n, int)
    print(f"Numeric meaning of life: {n}")

    n: int = await agent1.call(int, "repeat your previous answer", ignore=ignore, n=3)
    print(f"Repeated answer: {n}")


if __name__ == "__main__":
    asyncio.run(main())
