#!/usr/bin/env -S S_M_BASE_URL=http://localhost:2345 uv run python3

import asyncio

from agentica import spawn
from agentica.logging.loggers.stream_logger import StreamLogger


async def main():
    agent = await spawn(model='openai:gpt-4o')

    stream = StreamLogger()
    with stream:
        n = asyncio.create_task(agent.call(int, 'Hello World! Give me a fun number.'))

    role = None
    async for chunk in stream:
        if role is None and chunk.role == 'user':
            continue  # Skip first user message
        if role != chunk.role:
            print(f"\n\n--- {chunk.role} ---")
            role = chunk.role
        print(chunk, end='', flush=True)
    print('\n')

    print('n =', await n)


if __name__ == "__main__":
    asyncio.run(main())
