#!/usr/bin/env -S S_M_BASE_URL=http://localhost:2345 uv run python3

import asyncio

from agentica import agentic


@agentic(mode='json')
async def run_report(company: str) -> dict[str, str]:
    """
    Create a brief company report for the given company name.

    Returns a dictionary with:
    - name: The official company name
    - blurb: A 1-2 sentence description of the company's main business focus
    """
    ...


async def main():
    assert False, "JSON mode is not supported yet"
    res = await run_report("IBM")
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
