#!/usr/bin/env uv run python3

import asyncio
from concurrent.futures import ThreadPoolExecutor

from agentica import spawn


async def worker() -> str:
    agent = await spawn(model='openai:gpt-4.1')
    return await agent.call(str, "Hello, world!")


def run_worker() -> str:
    """Wrapper to run async worker in a thread's own event loop."""
    return asyncio.run(worker())


def main():
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(run_worker) for _ in range(4)]
        results = [f.result() for f in futures]

    print(results)


if __name__ == "__main__":
    from demos.runner import run_sync

    run_sync(main)
