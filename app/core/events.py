"""
Event Bus — single inter-module communication channel.
No direct cross-module database writes allowed.
"""

import asyncio
import logging
from typing import Callable, Dict, List, Awaitable
from app.core.domain.events import BaseEvent, EventPriority

logger = logging.getLogger(__name__)

EventHandler = Callable[[BaseEvent], Awaitable[None]]


class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._dead_letter: List[BaseEvent] = []

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Subscribed {handler.__qualname__} to [{event_type}]")

    async def publish(self, event: BaseEvent) -> None:
        handlers = self._handlers.get(event.event_type, [])
        if not handlers:
            logger.warning(f"No handlers for [{event.event_type}] — dead letter.")
            self._dead_letter.append(event)
            return

        logger.info(
            f"Publishing [{event.event_type}] id={event.event_id} "
            f"from={event.source_module} to {len(handlers)} handler(s)"
        )

        for handler in handlers:
            try:
                if event.priority == EventPriority.CRITICAL:
                    await handler(event)
                else:
                    asyncio.create_task(self._safe_handle(handler, event))
            except Exception as e:
                logger.error(f"Error dispatching to {handler}: {e}")
                self._dead_letter.append(event)

    async def _safe_handle(self, handler: EventHandler, event: BaseEvent) -> None:
        try:
            await handler(event)
        except Exception as e:
            logger.error(
                f"Handler {handler.__qualname__} failed for [{event.event_type}]: {e}"
            )
            self._dead_letter.append(event)

    def get_dead_letters(self) -> List[BaseEvent]:
        return list(self._dead_letter)
