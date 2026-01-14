#!/usr/bin/env -S S_M_BASE_URL=http://localhost:2345 uv run python3

import asyncio

from agentica import agentic


@agentic(model='openai:gpt-4o')
async def word_counter(corpus: str) -> int:
    """Returns the number of words in the corpus."""
    ...


async def main() -> None:
    res = await word_counter("There once was a man from Nantucket.")
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
