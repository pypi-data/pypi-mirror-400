#!/usr/bin/env uv run python3

import asyncio

from agentica import spawn
from agentica.std.caption import CaptionLogger


async def main():
    agent1 = await spawn(model='openai:gpt-4o')
    agent2 = await spawn(model='openai:gpt-4.1')
    agent3 = await spawn(model='openai:gpt-4o')

    with CaptionLogger():
        _ = await asyncio.gather(
            agent1.call(
                "Think deeply about the meaning of life, breaking your points up into multiple paragraphs."
            ),
            agent2.call(
                list[int],
                "Calculate the first 100 prime numbers, showing your work and explaining your approach with detailed comments.",
            ),
            agent3.call(
                "Explain the concept of quantum entanglement, using simple analogies and examples."
            ),
        )


if __name__ == "__main__":
    from demos.runner import run

    run(main())
