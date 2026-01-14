#!/usr/bin/env -S S_M_BASE_URL=http://localhost:2345 uv run python3

import asyncio
import logging
import os

from agentica import spawn


async def main():
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    agent1 = await spawn(model='anthropic:claude-sonnet-4')
    n: int = await agent1.call(int, "What is the meaning of life?")
    assert isinstance(n, int)
    print(f"Numeric meaning of life: {n}")

    agent2 = await spawn(model='openai:gpt-4o')
    meaning: str = await agent2.call(str, "Describe the meaning of life?")
    assert isinstance(meaning, str)
    print(f"Worded meaning of life: {meaning}")


if __name__ == "__main__":
    asyncio.run(main())
