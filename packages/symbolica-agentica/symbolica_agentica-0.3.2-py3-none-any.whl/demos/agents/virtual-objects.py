#!/usr/bin/env -S S_M_BASE_URL=http://localhost:2345 uv run python3

import asyncio
import os

from agentica import spawn


async def main():
    if not os.path.exists('secret.txt'):
        with open('secret.txt', 'w') as f:
            f.write('3405691582\n')

    agent = await spawn(model='openai:gpt-4o')

    with open('secret.txt', 'r') as f:
        n: int = await agent.call(int, "Fetch me the secret number?", file_handle=f)

    print(f"The secret number was: {n}")

    explainer = await agent.call("What is this number a reference to?")
    print(f"The explainer said: {explainer}")


if __name__ == "__main__":
    asyncio.run(main())
