"""
Lightweight Hook System - Inspired by epub.js

Provides a simple event system for extensibility without breaking existing APIs.
"""

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, List

logger = logging.getLogger(__name__)


class Hook:
    """
    A simple hook system for extensibility.

    Allows registering callbacks that get triggered at specific points
    in the EPUB processing pipeline.
    """

    def __init__(self):
        self._handlers: List[Callable[..., Any]] = []
        self._async_handlers: List[Callable[..., Awaitable[Any]]] = []

    def register(self, handler: Callable[..., Any]) -> None:
        """
        Register a synchronous handler.

        Args:
            handler: Function to call when hook is triggered
        """
        if handler not in self._handlers:
            self._handlers.append(handler)

    def register_async(self, handler: Callable[..., Awaitable[Any]]) -> None:
        """
        Register an asynchronous handler.

        Args:
            handler: Async function to call when hook is triggered
        """
        if handler not in self._async_handlers:
            self._async_handlers.append(handler)

    def unregister(self, handler: Callable[..., Any]) -> None:
        """
        Remove a handler from this hook.

        Args:
            handler: Handler function to remove
        """
        if handler in self._handlers:
            self._handlers.remove(handler)
        if handler in self._async_handlers:
            self._async_handlers.remove(handler)

    def trigger(self, *args, **kwargs) -> None:
        """
        Trigger synchronous handlers.

        Args:
            *args: Positional arguments to pass to handlers
            **kwargs: Keyword arguments to pass to handlers
        """
        for handler in self._handlers:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Hook handler failed: {e}")

    async def trigger_async(self, *args, **kwargs) -> None:
        """
        Trigger asynchronous handlers.

        Args:
            *args: Positional arguments to pass to handlers
            **kwargs: Keyword arguments to pass to handlers
        """
        for handler in self._async_handlers:
            try:
                await handler(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Async hook handler failed: {e}")

    def clear(self) -> None:
        """Remove all handlers."""
        self._handlers.clear()
        self._async_handlers.clear()

    def has_handlers(self) -> bool:
        """Check if any handlers are registered."""
        return bool(self._handlers or self._async_handlers)

    def __len__(self) -> int:
        """Return the number of registered handlers."""
        return len(self._handlers) + len(self._async_handlers)


class HookManager:
    """
    Manages multiple hooks for different EPUB processing events.

    Provides predefined hooks for common EPUB processing events.
    """

    def __init__(self):
        # Content processing hooks
        self.content_parsed = Hook()      # After chapter content is parsed
        self.chapter_loaded = Hook()      # After chapter is loaded from disk

        # TOC processing hooks
        self.toc_built = Hook()           # After TOC is built
        self.toc_parsed = Hook()          # After TOC structure is parsed

        # Metadata hooks
        self.metadata_extracted = Hook()  # After metadata is extracted

        # Layout hooks
        self.layout_parsed = Hook()       # After layout properties are parsed

        # Spine processing hooks
        self.spine_processed = Hook()     # After spine items are processed

    def clear_all(self) -> None:
        """Clear all hooks."""
        for hook in self.__dict__.values():
            if isinstance(hook, Hook):
                hook.clear()

    async def trigger_async_hooks(self, hook_name: str, *args, **kwargs) -> None:
        """
        Trigger async handlers for a specific hook by name.

        Args:
            hook_name: Name of the hook to trigger
            *args: Arguments to pass to handlers
            **kwargs: Keyword arguments to pass to handlers
        """
        hook = getattr(self, hook_name, None)
        if isinstance(hook, Hook):
            await hook.trigger_async(*args, **kwargs)

    def get_hook(self, name: str) -> Hook:
        """
        Get a hook by name.

        Args:
            name: Name of the hook

        Returns:
            The hook object
        """
        return getattr(self, name, None)

    def list_hooks(self) -> Dict[str, int]:
        """
        List all hooks and their handler counts.

        Returns:
            Dictionary mapping hook names to handler counts
        """
        return {
            name: len(hook)
            for name, hook in self.__dict__.items()
            if isinstance(hook, Hook)
        }
