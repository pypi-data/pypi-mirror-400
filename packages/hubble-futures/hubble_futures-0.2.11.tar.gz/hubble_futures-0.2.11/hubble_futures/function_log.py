"""
Structured Function Call Logging Module

This module provides structured logging for function calls and results in container agents.
It tracks all trading-related function calls with timing, parameters, and results.

Usage:
    from hubble_futures import start_function_log, record_function_call, finish_function_call, export_function_log

    # Start logging at container entry
    start_function_log()

    # Record function calls
    record_function_call("open_position", {"symbol": "BTCUSDT", "side": "BUY"})
    finish_function_call("open_position", {"order_id": "12345", "status": "filled"})

    # Export and clear at container exit
    result = export_function_log(clear=True)
"""

import contextvars
import copy
import time
from datetime import datetime
from typing import Any


# Context variable for function log storage (async-safe)
_log_storage: contextvars.ContextVar[dict] = contextvars.ContextVar("_function_log_storage")


def _create_new_storage() -> dict:
    """Create a new log storage instance with fresh mutable containers."""
    return {
        "function_calls": [],
        "trading_summary": {},
        "warnings": [],
        "errors": [],
        "metadata": {
            "start_time": None,
            "end_time": None,
            "container_id": None,
        },
    }


def _get_log_storage() -> dict:
    """
    Get context-local log storage.

    Returns the storage for the current context. Must call start_function_log()
    before this to initialize the storage.

    Raises:
        LookupError: If start_function_log() has not been called
    """
    return _log_storage.get()


def start_function_log(container_id: str | None = None) -> None:
    """
    Initialize function logging for the current container execution.

    Must be called at the container entry point before any function calls.
    Creates a fresh storage instance to avoid sharing state across async tasks.

    Args:
        container_id: Optional container identifier for tracking

    Example:
        start_function_log(container_id="agent-abc-123")
    """
    # Create a fresh storage instance for this context
    storage = _create_new_storage()
    storage["metadata"]["start_time"] = datetime.utcnow().isoformat()
    storage["metadata"]["container_id"] = container_id
    _log_storage.set(storage)


def record_function_call(function_name: str, parameters: dict[str, Any]) -> None:
    """
    Record the start of a function call with parameters.

    Call this immediately before invoking a trading function.
    Silently does nothing if logging has not been started (non-container scenarios).

    Args:
        function_name: Name of the function being called (e.g., "open_position")
        parameters: Parameters passed to the function

    Example:
        record_function_call("open_position", {"symbol": "BTCUSDT", "side": "BUY", "amount": 0.001})
    """
    try:
        storage = _get_log_storage()
    except LookupError:
        # Logging not initialized (non-container scenario), silently ignore
        return

    call_record = {
        "function": function_name,
        "parameters": parameters,
        "start_time": datetime.utcnow().isoformat(),
        "end_time": None,
        "duration_ms": None,
        "result": None,
        "error": None,
        "status": "pending",
    }
    storage["function_calls"].append(call_record)


def finish_function_call(function_name: str, result: dict[str, Any] | None = None, error: str | None = None) -> None:
    """
    Record the completion of a function call with result or error.

    Call this immediately after a trading function returns.
    Silently does nothing if logging has not been started (non-container scenarios).

    Args:
        function_name: Name of the function that completed (must match record_function_call)
        result: Function return value (e.g., {"order_id": "12345", "status": "filled"})
        error: Error message if the function failed

    Example:
        # Success case
        finish_function_call("open_position", {"order_id": "12345", "status": "filled"})

        # Error case
        finish_function_call("open_position", error="Insufficient margin")
    """
    try:
        storage = _get_log_storage()
    except LookupError:
        # Logging not initialized (non-container scenario), silently ignore
        return

    end_time = datetime.utcnow().isoformat()

    # Find the most recent pending call for this function
    for call in reversed(storage["function_calls"]):
        if call["function"] == function_name and call["status"] == "pending":
            call["end_time"] = end_time
            call["result"] = result
            call["error"] = error

            # Calculate duration
            if call["start_time"]:
                try:
                    start = datetime.fromisoformat(call["start_time"])
                    end = datetime.fromisoformat(end_time)
                    call["duration_ms"] = int((end - start).total_seconds() * 1000)
                except Exception:
                    pass

            # Set status
            if error:
                call["status"] = "failed"
            else:
                call["status"] = "succeeded"
            break


def set_trading_summary(summary: dict[str, Any]) -> None:
    """
    Set the overall trading summary for this execution.

    Call this at the end of execution to summarize trading activity.
    Silently does nothing if logging has not been started (non-container scenarios).

    Args:
        summary: Trading summary dict with keys like:
            - executed: Total number of trades executed
            - orders: List of order IDs
            - final_position: Net position after all trades
            - total_pnl: Total profit/loss

    Example:
        set_trading_summary({
            "executed": 2,
            "orders": ["12345", "12346"],
            "final_position": {"BTCUSDT": 0.001},
            "total_pnl": 10.50,
        })
    """
    try:
        storage = _get_log_storage()
    except LookupError:
        # Logging not initialized (non-container scenario), silently ignore
        return
    storage["trading_summary"] = summary


def add_warning(message: str) -> None:
    """
    Add a warning message to the log.
    Silently does nothing if logging has not been started (non-container scenarios).

    Args:
        message: Warning message to record
    """
    try:
        storage = _get_log_storage()
    except LookupError:
        # Logging not initialized (non-container scenario), silently ignore
        return
    storage["warnings"].append({
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    })


def add_error(message: str) -> None:
    """
    Add an error message to the log.
    Silently does nothing if logging has not been started (non-container scenarios).

    Args:
        message: Error message to record
    """
    try:
        storage = _get_log_storage()
    except LookupError:
        # Logging not initialized (non-container scenario), silently ignore
        return
    storage["errors"].append({
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    })


def export_function_log(clear: bool = True) -> dict[str, Any]:
    """
    Export the current function log as a structured JSON dict.

    Call this at container exit to get the complete log.
    Returns a deep copy to prevent external modifications from affecting internal state.
    Returns empty log if logging has not been started.

    Args:
        clear: If True, clear the log after exporting (default: True)

    Returns:
        Structured log dict with keys:
            - metadata: Execution metadata (start_time, end_time, container_id)
            - function_calls: List of all function calls with timing and results
            - trading_summary: Trading summary (if set)
            - warnings: List of warnings
            - errors: List of errors

    Example:
        result = export_function_log(clear=True)
        # Returns: {"metadata": {...}, "function_calls": [...], ...}
    """
    try:
        storage = _get_log_storage()
        storage["metadata"]["end_time"] = datetime.utcnow().isoformat()

        # Build deep copy to avoid external modifications
        export = copy.deepcopy({
            "metadata": storage["metadata"],
            "function_calls": storage["function_calls"],
            "trading_summary": storage["trading_summary"],
            "warnings": storage["warnings"],
            "errors": storage["errors"],
        })
    except LookupError:
        # Logging not initialized, return empty log
        export = copy.deepcopy(_create_new_storage())

    # Clear if requested (create fresh mutable containers)
    if clear:
        _log_storage.set(_create_new_storage())

    return export


def get_function_log() -> dict[str, Any]:
    """
    Get the current function log without clearing it.
    Returns a deep copy to prevent external modifications from affecting internal state.
    Returns empty log if logging has not been started.

    Returns:
        Current log state (same structure as export_function_log)
    """
    try:
        storage = _get_log_storage()
        return copy.deepcopy({
            "metadata": storage["metadata"],
            "function_calls": storage["function_calls"],
            "trading_summary": storage["trading_summary"],
            "warnings": storage["warnings"],
            "errors": storage["errors"],
        })
    except LookupError:
        # Logging not initialized, return empty log
        return copy.deepcopy(_create_new_storage())


def clear_function_log() -> None:
    """Clear all function log data by creating a fresh storage instance."""
    _log_storage.set(_create_new_storage())
