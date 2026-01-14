import asyncio

import httpx

from agentica import agentic


def get_data() -> str:
    return httpx.get("https://example.com").text


@agentic(get_data, model="openai:gpt-4o")
async def get_url_data() -> str:
    """Run get_data and return the text"""


async def main():
    res = await get_url_data()
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
