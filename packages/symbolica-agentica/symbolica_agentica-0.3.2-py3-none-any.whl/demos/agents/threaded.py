#!/usr/bin/env uv run python3

import asyncio
import threading

from agentica import spawn

res = []


async def worker():
    agent = await spawn(model='openai:gpt-4.1')
    x = await agent.call(str, "Hello, world!")
    res.append(x)


async def main():
    thread1 = threading.Thread(target=lambda: asyncio.run(worker()))
    thread2 = threading.Thread(target=lambda: asyncio.run(worker()))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    print(res)


if __name__ == "__main__":
    from demos.runner import run

    run(main())
