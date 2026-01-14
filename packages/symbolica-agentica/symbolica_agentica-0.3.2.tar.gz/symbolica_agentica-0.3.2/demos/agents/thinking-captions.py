#!/usr/bin/env -S S_M_BASE_URL=http://localhost:2345 uv run python3

# Idea:
# wrap echo stream of an agent in gpt-3.5-turbo and
# every ~50 tokens ask to summarize what it has seen so far,
# and add a loading spinner in front of the summary with a '\r'
# the summarizer should be able to indicate that its last summary
# is still relevant (or is unable to make a summary) by saying NO-UPDATE

import asyncio
import sys
from textwrap import dedent

from agentica import spawn
from agentica.agent import Agent
from agentica.logging import set_default_agent_listener
from agentica.logging.loggers.stream_logger import StreamLogger

set_default_agent_listener(None)


async def thinking[T](agent: Agent, return_type: type[T], task: str) -> T:
    every_n_tokens = 60
    summarizer = await spawn(
        "Your job is to summarize chunks of text of another agent's current thought process"
        + " Start you sentence with a present participle verbs of the agent's thoughts/actions, such as \"Thinking about ...\" or \"Exploring ...\"."
        + " NEVER start you summary by referring to \"the agent\" or by referring to the agent in any way."
        + " Keep it short and concise. A single sentence is enough, no more than 15 words.",
        model='openai:gpt-3.5-turbo',
    )

    stream = StreamLogger()
    with stream:
        result = asyncio.create_task(agent.call(return_type, task))
    # get `summarizer` to summarize the stream

    summary = ""
    changed = False

    async def make_summaries() -> None:
        nonlocal summary, changed

        collated = ""
        n_tokens = 0

        async def summarize(collated: str) -> str:
            maybe_summary = await summarizer.call(
                dedent(f"""
                Summarize very briefly what has been thought so far by the agent, by observing THOUGHTS.
                If you believe your previous summary is still relevant or the THOUGHTS are empty, say NO-UPDATE.

                THOUGHTS:
                {collated}
                """).strip(),
            )
            if 'NO-UPDATE' not in maybe_summary:
                return maybe_summary
            return summary

        role = None
        async for chunk in stream:
            if role != chunk.role:
                collated += f'({chunk.role})\n'
                role = chunk.role

            if n_tokens % every_n_tokens == 0:
                changed = True
                summary = await summarize(collated)
                collated = ""

            collated += chunk.content
            n_tokens += 1

        # summarize remaining tokens
        summary = await summarize(collated)
        await asyncio.sleep(0.5)  # let us see the final summary briefly

    bg = asyncio.create_task(make_summaries())

    def clear_line():
        _ = sys.stdout.write('\033[2K\033[1G')
        _ = sys.stdout.flush()

    loading = '⣾⣽⣻⢿⡿⣟⣯⣷'
    i = 0
    line = ''
    while not bg.done():
        if summary:
            line = f'Thinking: {summary}'
        else:
            line = 'Thinking.'

        if changed:
            changed = False
            clear_line()

        print(f'\r{loading[i % len(loading)]} {line}', end='', flush=True)
        await asyncio.sleep(0.1)
        i += 1

    clear_line()
    return await result


async def main():
    agent = await spawn(model='openai:gpt-4o')
    res = await thinking(
        agent,
        str,
        "Think deeply about the meaning of life, breaking your points up into multiple paragraphs.",
    )
    print('-' * 30)
    print('Done:', res)


if __name__ == "__main__":
    asyncio.run(main())
