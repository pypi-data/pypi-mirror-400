#!/usr/bin/env -S S_M_BASE_URL=http://localhost:2345 uv run python3

import os

from slack_sdk import WebClient

from agentica import agentic

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

# We know we will want to list users and send a message
slack_conn = WebClient(token=SLACK_BOT_TOKEN)
send_direct_message = slack_conn.chat_postMessage


@agentic(send_direct_message, model="openai:gpt-4.1")
async def send_morning_message(user_name: str) -> None:
    """
    Uses the Slack API to send the user a direct message. Light and cheerful!
    """
    ...


if __name__ == "__main__":
    import asyncio

    asyncio.run(send_morning_message('@Samuel'))
    print("Morning message sent!")
