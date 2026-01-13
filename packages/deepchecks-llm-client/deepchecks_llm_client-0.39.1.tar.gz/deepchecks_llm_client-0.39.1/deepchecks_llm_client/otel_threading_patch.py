"""
OpenTelemetry Threading Context Propagation Patcher

This module provides a patcher for threading.Thread and concurrent.futures.ThreadPoolExecutor
to automatically propagate OpenTelemetry context across thread boundaries.
"""

import concurrent.futures
import logging
import threading
import typing as t

logger = logging.getLogger(__name__)

try:
    from opentelemetry import context
except ImportError:
    logger.error("OpenTelemetry dependencies are not installed. please install deepchecks-llm-client with otel extra - "
                 "\"pip install deepchecks-llm-client[otel]\"")
    raise


class _SingletonMeta(type):
    """Metaclass for singleton pattern."""
    _instances: t.Dict[type, t.Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class ThreadingContextPropagationPatcher(metaclass=_SingletonMeta):
    """
    Patches threading.Thread and concurrent.futures.ThreadPoolExecutor to automatically
    propagate OpenTelemetry context across thread boundaries.

    This ensures that trace context is maintained when agent frameworks (like CrewAI)
    use threading for timeout execution or parallel processing.

    Can be used as a context manager for block-scoped patching, or with explicit
    patch/unpatch calls for module-scoped patching.

    Example usage as context manager:
        with ThreadingContextPropagationPatcher():
            # Threading operations here will propagate context
            with ThreadPoolExecutor() as executor:
                executor.submit(some_function)

    Example usage with explicit patch/unpatch:
        patcher = ThreadingContextPropagationPatcher()
        patcher.patch()
        # ... do work ...
        patcher.unpatch()
    """

    def __init__(self):
        """Initialize the patcher."""
        self._is_patched = False
        self._original_submit: t.Optional[t.Callable] = None
        self._original_thread_init: t.Optional[t.Callable] = None

    def patch(self) -> None:
        """
        Apply patches to ThreadPoolExecutor and Thread to propagate OpenTelemetry context.

        This method is idempotent - calling it multiple times will only apply patches once.
        """
        if self._is_patched:
            logger.debug("Threading patches already applied, skipping")
            return

        try:
            # Store original methods
            self._original_submit = concurrent.futures.ThreadPoolExecutor.submit
            self._original_thread_init = threading.Thread.__init__

            # Patch ThreadPoolExecutor.submit
            def context_propagating_submit(executor_self, fn, /, *args, **kwargs):
                """Wrapper for ThreadPoolExecutor.submit that propagates OpenTelemetry context"""
                current_context = context.get_current()

                def wrapped_fn(*fn_args, **fn_kwargs):
                    token = context.attach(current_context)
                    try:
                        return fn(*fn_args, **fn_kwargs)
                    finally:
                        context.detach(token)

                return self._original_submit(executor_self, wrapped_fn, *args, **kwargs)

            concurrent.futures.ThreadPoolExecutor.submit = context_propagating_submit

            # Patch threading.Thread.__init__
            def patched_thread_init(thread_self, *args, **kwargs):
                """Wrapper for Thread.__init__ that propagates OpenTelemetry context"""
                current_context = context.get_current()

                # Thread.__init__ signature: __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None)
                # target can be passed as:
                # 1. Keyword argument: Thread(target=func)
                # 2. Positional argument: Thread(None, func) - group, target

                target = None
                target_in_kwargs = 'target' in kwargs
                target_in_args = len(args) >= 2  # args[0] is group, args[1] is target

                if target_in_kwargs and kwargs['target'] is not None:
                    target = kwargs['target']
                elif target_in_args and args[1] is not None:
                    target = args[1]

                # If target function is provided, wrap it
                if target is not None:
                    def wrapped_target(*target_args, **target_kwargs):
                        token = context.attach(current_context)
                        try:
                            return target(*target_args, **target_kwargs)
                        finally:
                            context.detach(token)

                    # Replace target with wrapped version
                    if target_in_kwargs:
                        kwargs['target'] = wrapped_target
                    elif target_in_args:
                        # Convert args to list, replace target, convert back to tuple
                        args_list = list(args)
                        args_list[1] = wrapped_target
                        args = tuple(args_list)

                self._original_thread_init(thread_self, *args, **kwargs)

            threading.Thread.__init__ = patched_thread_init

            self._is_patched = True
            logger.info("✓ Threading patches applied: Thread and ThreadPoolExecutor now propagate OpenTelemetry context")

        except Exception as e:
            logger.warning(f"Failed to apply threading patches for OpenTelemetry context propagation: {e}")
            raise

    def unpatch(self) -> None:
        """
        Remove patches and restore original threading behavior.

        This method is idempotent - calling it multiple times is safe.
        """
        if not self._is_patched:
            logger.debug("Threading patches not applied, nothing to unpatch")
            return

        try:
            # Restore original methods
            if self._original_submit is not None:
                concurrent.futures.ThreadPoolExecutor.submit = self._original_submit
                self._original_submit = None

            if self._original_thread_init is not None:
                threading.Thread.__init__ = self._original_thread_init
                self._original_thread_init = None

            self._is_patched = False
            logger.info("✓ Threading patches removed: Thread and ThreadPoolExecutor restored to original behavior")

        except Exception as e:
            logger.warning(f"Failed to remove threading patches: {e}")
            raise

    def is_patched(self) -> bool:
        """
        Check if patches are currently applied.

        Returns:
            bool: True if patches are applied, False otherwise
        """
        return self._is_patched


def patch_threading_for_context_propagation() -> None:
    patcher = ThreadingContextPropagationPatcher()
    patcher.patch()


def unpatch_threading_for_context_propagation() -> None:
    patcher = ThreadingContextPropagationPatcher()
    patcher.unpatch()

