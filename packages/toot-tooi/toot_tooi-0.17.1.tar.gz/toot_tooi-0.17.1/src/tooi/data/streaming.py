import json
import logging
from typing import AsyncGenerator
from tooi import http
from tooi.entities import Notification
from tooi.utils.from_dict import from_dict

logger = logging.getLogger(__name__)


async def stream_notifications() -> AsyncGenerator[Notification, None]:
    async for event in stream_events("/api/v1/streaming/user/notification"):
        yield event


# TODO: implement retry with exponential backoff


async def stream_events(stream_path: str):
    try:
        event: str | None = None
        async for line in http.stream_sse(stream_path):
            if not line or line.startswith(":"):
                continue
            if line.startswith("event: "):
                event = line.removeprefix("event: ")
            elif line.startswith("data: "):
                line = line.removeprefix("data: ")
                data = json.loads(line)
                if event == "notification":
                    yield from_dict(Notification, data)
                else:
                    logger.warning("Event '{event} not handled'")
            else:
                logger.warning("Don't know how to parse line:\n{line}")
    except Exception:
        logger.exception("Failed streaming notifications")
