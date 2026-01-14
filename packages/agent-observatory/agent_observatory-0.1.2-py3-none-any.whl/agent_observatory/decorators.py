import asyncio
import functools
from collections.abc import Callable
from typing import Any, TypeVar

from .context import get_current_session

# Type variable for the decorated function
F = TypeVar("F", bound=Callable[..., Any])


def trace_agent_step(name: str) -> Callable[[F], F]:
    """
    Decorator to trace a function as an agent step.

    Heuristic:
    1. Check 'obs' or 'session' in kwargs.
    2. Check 'self.obs' or 'self.session' in first arg.
    3. Check ambient session in ContextVars.

    Supports both sync and async functions.
    """

    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                session = _find_session(args, kwargs)
                if session and hasattr(session, "agent_step"):
                    with session.agent_step(name):
                        return await func(*args, **kwargs)
                return await func(*args, **kwargs)

            return async_wrapper  # type: ignore
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                session = _find_session(args, kwargs)
                if session and hasattr(session, "agent_step"):
                    with session.agent_step(name):
                        return func(*args, **kwargs)
                return func(*args, **kwargs)

            return sync_wrapper  # type: ignore

    return decorator


def trace_tool_call(name: str) -> Callable[[F], F]:
    """
    Decorator to trace a function as a tool call.
    Supports both sync and async functions.
    """

    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                session = _find_session(args, kwargs)
                if session and hasattr(session, "tool_call"):
                    with session.tool_call(name):
                        return await func(*args, **kwargs)
                return await func(*args, **kwargs)

            return async_wrapper  # type: ignore
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                session = _find_session(args, kwargs)
                if session and hasattr(session, "tool_call"):
                    with session.tool_call(name):
                        return func(*args, **kwargs)
                return func(*args, **kwargs)

            return sync_wrapper  # type: ignore

    return decorator


def trace_llm_call(name: str) -> Callable[[F], F]:
    """
    Decorator to trace a function as an LLM call.
    Supports both sync and async functions.
    """

    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                session = _find_session(args, kwargs)
                if session and hasattr(session, "llm_call"):
                    with session.llm_call(name):
                        return await func(*args, **kwargs)
                return await func(*args, **kwargs)

            return async_wrapper  # type: ignore
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                session = _find_session(args, kwargs)
                if session and hasattr(session, "llm_call"):
                    with session.llm_call(name):
                        return func(*args, **kwargs)
                return func(*args, **kwargs)

            return sync_wrapper  # type: ignore

    return decorator


def _find_session(args: tuple, kwargs: dict) -> Any | None:
    """
    Heuristic to find an AgentSession in args, kwargs or ambient context.
    """
    # 1. Check known kwargs
    if "session" in kwargs:
        return kwargs["session"]
    if "obs" in kwargs:
        return kwargs["obs"]

    # 2. Check first arg (self) for .session or .obs
    if args:
        first_arg = args[0]
        if hasattr(first_arg, "session"):
            return first_arg.session
        if hasattr(first_arg, "obs"):
            return first_arg.obs

    # 3. Check ContextVars
    return get_current_session()
