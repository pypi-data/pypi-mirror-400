from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

logger = logging.getLogger(__name__)

EventHandler = Callable[[dict[str, Any], str | None], Awaitable[None]]


class EventDispatcher:
    def __init__(self) -> None:
        self._specific_handlers: dict[str, list[EventHandler]] = {}
        self._wildcard_handlers: list[EventHandler] = []

    def add_handler(self, event_name: str | None, handler: EventHandler) -> None:
        if event_name is None:
            self._wildcard_handlers.append(handler)
        else:
            self._specific_handlers.setdefault(event_name, []).append(handler)

    def remove_handler(self, event_name: str | None, handler: EventHandler) -> None:
        if event_name is None:
            if handler in self._wildcard_handlers:
                self._wildcard_handlers.remove(handler)
        else:
            handlers = self._specific_handlers.get(event_name, [])
            if handler in handlers:
                handlers.remove(handler)

    async def dispatch(
        self, method: str, params: dict[str, Any], session_id: str | None
    ) -> bool:
        any_handled = False

        for handler in self._specific_handlers.get(method, []):
            if await self._invoke(handler, params, session_id):
                any_handled = True

        for handler in self._wildcard_handlers:
            if await self._invoke(handler, params, session_id):
                any_handled = True

        return any_handled

    async def _invoke(
        self, handler: EventHandler, params: dict[str, Any], session_id: str | None
    ) -> bool:
        try:
            await handler(params, session_id)
            return True
        except Exception as e:
            logger.exception(f"Event handler error: {e}")
            return False
