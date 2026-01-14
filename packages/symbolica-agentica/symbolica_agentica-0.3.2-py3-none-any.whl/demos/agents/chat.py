#!/usr/bin/env -S S_M_BASE_URL=http://localhost:2345 uv run python3

import asyncio

from agentica import spawn
from agentica.logging import set_default_agent_listener
from agentica.logging.loggers.stream_logger import StreamLogger

RED = "\033[91m"
GREEN = "\033[92m"
PURPLE = "\033[95m"
RESET = "\033[0m"
GREY = "\033[90m"

set_default_agent_listener(None)


async def chat():
    agent = await spawn(model='openai:gpt-4o')

    while user_input := input(f"\n{PURPLE}User{RESET}: "):
        try:
            # Invoke agent against user prompt
            stream = StreamLogger()
            with stream:
                result = asyncio.create_task(agent.call(str, user_input))

            # Stream intermediate "thinking" to console
            print(GREY)
            async for chunk in stream:
                if chunk.role == 'agent':
                    print(chunk, end="", flush=True)
                else:
                    print()
            print(RESET)

            # Print final result
            print(f"\n{GREEN}Agent{RESET}: {await result}")

        except Exception as agent_error:
            print(f"\n{RED}AgentError: {agent_error}{RESET}")

    print("\nExiting...")


if __name__ == "__main__":
    asyncio.run(chat())
