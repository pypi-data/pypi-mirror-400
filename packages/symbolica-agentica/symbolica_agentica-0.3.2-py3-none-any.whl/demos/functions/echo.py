#!/usr/bin/env -S S_M_BASE_URL=http://localhost:2345 uv run python3

import asyncio

from agentica import agentic
from agentica.logging.loggers.stream_logger import StreamLogger


@agentic(model='openai:gpt-4o')
async def word_counter(corpus: str) -> int:
    """Returns the number of words in the corpus."""
    ...


async def main() -> None:
    stream = StreamLogger()
    with stream:
        res = asyncio.create_task(word_counter("There once was a man from Nantucket."))

    async for chunk in stream:
        if chunk.role == 'agent':
            print(chunk, end="", flush=True)
    print()

    print(await res)


if __name__ == "__main__":
    asyncio.run(main())
