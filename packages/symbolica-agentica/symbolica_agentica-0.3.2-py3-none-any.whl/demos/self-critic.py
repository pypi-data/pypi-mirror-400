import asyncio
import logging
from logging import getLogger

from agentica import Agent, spawn
from agentica.logging.loggers.stream_logger import StreamLogger

RED = "\033[91m"
GREEN = "\033[92m"
PURPLE = "\033[95m"
RESET = "\033[0m"
GREY = "\033[90m"

logger = getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

logging.getLogger("httpcore").setLevel(logging.INFO)


def read_file(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read()


def write_file(file_path: str, content: str) -> str:
    with open(file_path, 'w') as file:
        file.write(content)
    return "File written successfully"


from dataclasses import dataclass


@dataclass
class Failure:
    description: str
    reason: str
    warp_issue: bool
    user_expectation: float


async def get_response(agent: Agent, user_input: str) -> str:
    try:
        # Invoke agent against user prompt
        stream = StreamLogger()
        with stream:
            result = asyncio.create_task(
                agent.call(
                    str,
                    user_input,
                    read_file=read_file,
                    write_file=write_file,
                    Failure=Failure,
                )
            )

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


async def chat():
    logger.info("Starting chat")
    agent = await spawn(model='openai:gpt-4o')
    await get_response(
        agent,
        """
Your task is to read the following files, look for all instances of tests marked as xfail, and compile a list of Failure. You need to manually and carefully inspect each case to write an accurate description of what was being tested.

A WARP issue is a test that indicates that something is wrong with WARP.

The user expectation score is on a scale of 0 to 100, given what the test is assesing, how likely do you think it is that a user using the library will run into this issue and be disappointed.
To calibrate this, complicated async issues rank low, but passing file objects rank high.

When you have the list of Failures, write it to a file called failures.txt.

The list of files is:
../../tests/integration/test_stubs_signature.py
../../tests/integration/agentic/annot/test_namedtuple.py
../../tests/integration/agentic/annot/test_method.py
../../tests/integration/agentic/annot/test_class.py
../../tests/integration/agentic/annot/test_function_annots.py
../../tests/integration/agentic/args/test_enum.py
../../tests/integration/unit/test_dataclass.py
../../tests/integration/agentic/args/test_collections.py
../../tests/integration/unit/test_class.py
../../tests/integration/agentic/args/test_network.py
../../tests/integration/unit/test_instantiate.py
../../tests/integration/agentic/capability/test_read_file.py
../../tests/integration/unit/test_generic_alias.py
../../tests/integration/agentic/capability/test_write_file.py
../../tests/integration/agentic/args/test_iterable.py
""",
    )
    await asyncio.sleep(30)
    await get_response(agent, "now sort by score")
    while user_input := input(f"\n{PURPLE}User{RESET}: "):
        await get_response(agent, user_input)
    print("\nExiting...")


if __name__ == "__main__":
    asyncio.run(chat())
