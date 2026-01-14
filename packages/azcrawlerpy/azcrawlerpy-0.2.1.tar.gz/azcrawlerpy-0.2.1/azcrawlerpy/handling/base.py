"""
Base handler for chain of responsibility pattern.

Provides abstract base class for building handler chains where each handler
can process a request or pass it to the next handler in the chain.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any


class BaseHandler(ABC):
    """
    Abstract base class for chain of responsibility handlers.

    Handlers can be chained using set_next() and will pass requests along
    the chain if they cannot handle them. Supports both async and sync execution.
    """

    def __init__(self) -> None:
        self._next_handler: BaseHandler | None = None

    def set_next(self, handler: "BaseHandler") -> "BaseHandler":
        """
        Set the next handler in the chain.

        Args:
            handler: The handler to call after this one

        Returns:
            The handler that was passed in, enabling fluent chaining

        """
        self._next_handler = handler
        return handler

    @abstractmethod
    async def handle(self, request: Any, context: dict[str, Any] | None = None) -> Any:
        """
        Process the request or pass to next handler.

        Args:
            request: The request object to process
            context: Optional context dictionary for passing data between handlers

        Returns:
            The result of processing, or None if no handler processed the request

        """
        if self._next_handler:
            return await self._next_handler.handle(request, context)
        return None

    def handle_sync(self, request: Any, context: dict[str, Any] | None = None) -> Any:
        """
        Synchronous wrapper for handle().

        Args:
            request: The request object to process
            context: Optional context dictionary for passing data between handlers

        Returns:
            The result of processing

        """
        return asyncio.run(self.handle(request, context))

    def __repr__(self) -> str:
        next_handler_name = type(self._next_handler).__name__ if self._next_handler else "None"
        return f"{type(self).__name__}(next_handler={next_handler_name})"

    def get_chain_info(self) -> str:
        """
        Get a string representation of the handler chain.

        Returns:
            Arrow-separated list of handler class names in chain order

        """
        chain_info = [type(self).__name__]
        current_handler = self._next_handler
        while current_handler:
            chain_info.append(type(current_handler).__name__)
            current_handler = current_handler._next_handler
        return " -> ".join(chain_info)
