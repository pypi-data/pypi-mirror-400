#!/usr/bin/env -S S_M_BASE_URL=http://localhost:2345 uv run python3

import asyncio

from agentica import spawn


async def anthropic_agent():
    # Anthropic Agent
    agent1 = await spawn(
        model='anthropic:claude-sonnet-4',
        system="""
        DEV:
        $DEV

        FINAL:
        $FINAL

        INPUTS:
        $INPUTS

        PROCESS:
        $PROCESS

        RESOURCES:
        $RESOURCES

        STARTER:
        $STARTER
    """,
    )
    n: int = await agent1(
        int,
        """
        STUBS:
        $STUBS

        USER_PROMPT:
        $USER_PROMPT

        What is the meaning of life? Return an integer.
        """,
        x=3,
    )
    assert isinstance(n, int)
    print(f"Numeric meaning of life: {n}")


async def openai_agent():
    # OpenAI Agent
    agent2 = await spawn(
        model='openai:gpt-4.1',
        system="""
        INTERACTIONS:
        $INTERACTIONS

        NOTES:
        $NOTES

        OBJECTIVES:
        $OBJECTIVES

        OUTPUT:
        $OUTPUT

        STARTER:
        $STARTER

        WORKFLOW:
        $WORKFLOW
    """,
    )
    n: int = await agent2(
        int,
        """
        STUBS:
        $STUBS

        USER_PROMPT:
        $USER_PROMPT

        What is the meaning of life? Return an integer.
        """,
        x=3,
    )
    assert isinstance(n, int)
    print(f"Numeric meaning of life: {n}")


async def main():
    await anthropic_agent()
    await openai_agent()


if __name__ == "__main__":
    asyncio.run(main())
