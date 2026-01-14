#!/usr/bin/env -S S_M_BASE_URL=http://localhost:2345 uv run python3

import asyncio

from agentica import agentic


async def anthropic_agent():
    # Anthropic Agent
    x = 3

    @agentic(
        x,
        model='anthropic:claude-sonnet-4',
        system="""
        COMMUNICATION:
        $COMMUNICATION

        DEV:
        $DEV

        EXECUTION:
        $EXECUTION

        FINAL:
        $FINAL

        FUNCTION_SPEC:
        $FUNCTION_SPEC

        STARTER:
        $STARTER
    """,
    )
    async def meaning_of_life() -> int: ...

    n: int = await meaning_of_life()
    assert isinstance(n, int)
    print(f"Numeric meaning of life: {n}")


async def openai_agent():
    # OpenAI Agent
    x = 3

    @agentic(
        x,
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
    async def meaning_of_life() -> int: ...

    n: int = await meaning_of_life()
    assert isinstance(n, int)
    print(f"Numeric meaning of life: {n}")


async def main():
    # await anthropic_agent()
    await openai_agent()


if __name__ == "__main__":
    asyncio.run(main())
