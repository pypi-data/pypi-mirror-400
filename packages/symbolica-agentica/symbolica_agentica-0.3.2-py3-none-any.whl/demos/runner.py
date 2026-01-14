"""demo runner: configure logging and env vars"""

import asyncio
import logging
import os
from argparse import ArgumentParser, Namespace
from typing import Any, Callable, Coroutine, Literal, get_args


def run(coro: Coroutine[Any, Any, Any]) -> None:
    args = parse_args()

    logging.basicConfig(level=args.log_level)
    asyncio.run(coro)


def run_sync[R](func: Callable[[], R]) -> R:
    args = parse_args()
    logging.basicConfig(level=args.log_level)
    return func()


type LogLevel = Literal['debug', 'info', 'warning', 'error', 'critical']
log_levels: tuple[LogLevel, ...] = get_args(LogLevel.__value__)


def parse_args() -> Namespace:
    base_url: str = os.getenv('S_M_BASE_URL', 'http://localhost:2345')
    log_level: str = os.getenv('LOG_LEVEL', 'warning').lower()
    assert log_level in log_levels, f"Invalid log level: {log_level}; expected one of {log_levels}"

    parser = ArgumentParser(description='Demo runner')
    parser.add_argument('--base-url', type=str, default=base_url)
    parser.add_argument(
        '--log-level',
        type=str,
        choices=log_levels,
        default=log_level,
    )
    args: Namespace = parser.parse_args()
    args.log_level = args.log_level.upper()
    return args
