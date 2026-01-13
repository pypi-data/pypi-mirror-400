"""
Execution context for plugin actions.

The Context provides access to:
- Logging methods (debug, info, warn, error)
- Input arguments ($.args.*)
- Context variables ($.ctx.*)
- Return values ($.return.*)
- Trace information
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
import logging


class Context(ABC):
    """
    Abstract context interface for action execution.

    Provides logging, variable access, and trace information.
    """

    @abstractmethod
    def debug(self, msg: str, *args: Any) -> None:
        """Log a debug message."""
        pass

    @abstractmethod
    def info(self, msg: str, *args: Any) -> None:
        """Log an info message."""
        pass

    @abstractmethod
    def warn(self, msg: str, *args: Any) -> None:
        """Log a warning message."""
        pass

    @abstractmethod
    def error(self, msg: str, *args: Any) -> None:
        """Log an error message."""
        pass

    @abstractmethod
    def arg(self, name: str) -> Any:
        """Get an input argument ($.args.*)."""
        pass

    @abstractmethod
    def ctx(self, name: str) -> Any:
        """Get a context variable ($.ctx.*)."""
        pass

    @abstractmethod
    def set_ctx(self, name: str, value: Any) -> None:
        """Set a context variable ($.ctx.*)."""
        pass

    @abstractmethod
    def set_return(self, name: str, value: Any) -> None:
        """Set a return value ($.return.*)."""
        pass

    @property
    @abstractmethod
    def trace_id(self) -> str:
        """Get the trace ID for this execution."""
        pass

    @property
    @abstractmethod
    def step_name(self) -> str:
        """Get the current step name."""
        pass


class BaseContext(Context):
    """
    Base implementation of the execution context.

    Provides a simple in-memory implementation that can be used
    for testing or as a base for custom contexts.
    """

    def __init__(
        self,
        trace_id: str = "",
        step_name: str = "",
        args: Optional[dict[str, Any]] = None,
        ctx: Optional[dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self._trace_id = trace_id
        self._step_name = step_name
        self._args = args or {}
        self._ctx = ctx or {}
        self._return: dict[str, Any] = {}
        self._logger = logger or logging.getLogger("app4.plugin")

    def debug(self, msg: str, *args: Any) -> None:
        """Log a debug message."""
        self._logger.debug(f"[{self._trace_id}] {msg}", *args)

    def info(self, msg: str, *args: Any) -> None:
        """Log an info message."""
        self._logger.info(f"[{self._trace_id}] {msg}", *args)

    def warn(self, msg: str, *args: Any) -> None:
        """Log a warning message."""
        self._logger.warning(f"[{self._trace_id}] {msg}", *args)

    def error(self, msg: str, *args: Any) -> None:
        """Log an error message."""
        self._logger.error(f"[{self._trace_id}] {msg}", *args)

    def arg(self, name: str) -> Any:
        """Get an input argument ($.args.*)."""
        return self._args.get(name)

    def ctx(self, name: str) -> Any:
        """Get a context variable ($.ctx.*)."""
        return self._ctx.get(name)

    def set_ctx(self, name: str, value: Any) -> None:
        """Set a context variable ($.ctx.*)."""
        self._ctx[name] = value

    def set_return(self, name: str, value: Any) -> None:
        """Set a return value ($.return.*)."""
        self._return[name] = value

    @property
    def trace_id(self) -> str:
        """Get the trace ID for this execution."""
        return self._trace_id

    @property
    def step_name(self) -> str:
        """Get the current step name."""
        return self._step_name

    @property
    def return_values(self) -> dict[str, Any]:
        """Get all return values."""
        return self._return

    @property
    def context_values(self) -> dict[str, Any]:
        """Get all context values."""
        return self._ctx

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            "traceId": self._trace_id,
            "stepName": self._step_name,
            "args": self._args,
            "ctx": self._ctx,
            "return": self._return,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseContext":
        """Create context from dictionary."""
        return cls(
            trace_id=data.get("traceId", ""),
            step_name=data.get("stepName", ""),
            args=data.get("args", {}),
            ctx=data.get("ctx", {}),
        )
