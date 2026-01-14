"""
Action executor - unified interface for executing test case steps

This module provides a centralized executor that routes action requests
to the appropriate action implementation based on action type.
"""

import logging
from typing import Dict, Any, Optional, Type
from .base import BaseAction, ActionContext, ActionResult

# Import all action implementations
from .tap_action import TapAction
from .swipe_action import SwipeAction
from .launch_app_action import LaunchAppAction
from .close_app_action import CloseAppAction
from .input_action import InputAction
from .wait_action import WaitAction
from .press_back_action import PressBackAction
from .screenshot_action import ScreenshotAction

logger = logging.getLogger(__name__)


class ActionExecutor:
    """
    Unified executor for test case step actions

    This class maps action types to their implementations and provides
    a simple interface for executing any action type.
    """

    # Registry of action type -> action class mappings
    ACTION_REGISTRY: Dict[str, Type[BaseAction]] = {
        "tap": TapAction,
        "swipe": SwipeAction,
        "launch_app": LaunchAppAction,
        "close_app": CloseAppAction,
        "输入": InputAction,  # Chinese for backward compatibility
        "input": InputAction,  # English alias
        "wait": WaitAction,
        "press_back": PressBackAction,
        "screenshot": ScreenshotAction,
    }

    @classmethod
    def get_supported_actions(cls) -> list:
        """
        Get list of supported action types

        Returns:
            List of action type strings
        """
        return list(cls.ACTION_REGISTRY.keys())

    @classmethod
    def register_action(cls, action_type: str, action_class: Type[BaseAction]):
        """
        Register a custom action type

        Args:
            action_type: Action type identifier
            action_class: Action implementation class
        """
        cls.ACTION_REGISTRY[action_type] = action_class
        logger.info(f"Registered custom action: {action_type} -> {action_class.__name__}")

    @classmethod
    async def execute(
        cls,
        action_type: str,
        action_data: Dict[str, Any],
        context: ActionContext,
        send_log_callback: Optional[callable] = None
    ) -> ActionResult:
        """
        Execute an action by type

        Args:
            action_type: Type of action to execute (e.g., "tap", "swipe")
            action_data: Action-specific parameters
            context: Execution context (device ID, package, etc.)
            send_log_callback: Optional callback for sending logs

        Returns:
            ActionResult with execution results

        Raises:
            ValueError: If action_type is not supported
        """
        # Check if action type is supported
        action_class = cls.ACTION_REGISTRY.get(action_type)

        if not action_class:
            supported = ", ".join(cls.get_supported_actions())
            error_msg = f"Unknown action type: {action_type}. Supported types: {supported}"
            logger.error(error_msg)

            await cls._send_log_async(
                context.task_id,
                f"❌ Unknown action type: {action_type}",
                "stderr",
                send_log_callback
            )

            return ActionResult(
                success=False,
                error=error_msg
            )

        # Create action instance and execute
        try:
            action = action_class()

            logger.info(f"Executing {action_type} action on device {context.device_id}")
            result = await action.execute(action_data, context, send_log_callback)

            logger.info(
                f"Action {action_type} completed: "
                f"success={result.success}, "
                f"time={result.execution_time:.2f}s"
            )

            return result

        except Exception as e:
            error_msg = f"Action {action_type} execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)

            await cls._send_log_async(
                context.task_id,
                f"❌ Action execution error: {str(e)}",
                "stderr",
                send_log_callback
            )

            return ActionResult(
                success=False,
                error=error_msg
            )

    @classmethod
    async def _send_log_async(
        cls,
        task_id: str,
        message: str,
        log_type: str,
        callback: Optional[callable]
    ):
        """Helper to send log asynchronously"""
        if callback:
            try:
                # Check if callback is async
                import asyncio
                if asyncio.iscoroutinefunction(callback):
                    await callback(task_id, message, log_type)
                else:
                    # If sync callback, run in executor
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, callback, task_id, message, log_type)
            except Exception as e:
                logger.debug(f"Failed to send log: {e}")


# Convenience function for quick execution
async def execute_action(
    action_type: str,
    action_data: Dict[str, Any],
    context: ActionContext,
    send_log_callback: Optional[callable] = None
) -> ActionResult:
    """
    Convenience function for executing an action

    This is a shortcut for ActionExecutor.execute()

    Args:
        action_type: Type of action to execute
        action_data: Action-specific parameters
        context: Execution context
        send_log_callback: Optional log callback

    Returns:
        ActionResult with execution results
    """
    return await ActionExecutor.execute(
        action_type,
        action_data,
        context,
        send_log_callback
    )
