"""
Base action class and data structures for test case step actions
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class ActionContext:
    """
    Context information for action execution

    Attributes:
        device_id: Android device ID
        package_name: Application package name
        main_activity: Main activity name
        task_id: Task ID for logging
        screenshot_dir: Directory for screenshots
        execution_id: Test case execution ID
        test_case_id: Test case ID
    """
    device_id: str
    package_name: Optional[str] = None
    main_activity: Optional[str] = None
    task_id: str = ""
    screenshot_dir: str = "screenshots"
    execution_id: str = ""
    test_case_id: str = ""

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionResult:
    """
    Result of action execution

    Attributes:
        success: Whether the action executed successfully
        message: Human-readable result message
        data: Additional result data (e.g., coordinates, screenshot path)
        error: Error message if action failed
        execution_time: Time taken to execute the action (seconds)
    """
    success: bool
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time
        }


class BaseAction(ABC):
    """
    Base class for all test case step actions

    All action implementations should inherit from this class and implement
    the execute() method.
    """

    # Action type identifier (e.g., "tap", "swipe", "launch_app")
    action_type: str = ""

    # Description of this action
    description: str = ""

    def __init__(self):
        """Initialize the action"""
        if not self.action_type:
            raise ValueError(f"{self.__class__.__name__} must define action_type")

    @abstractmethod
    async def execute(
        self,
        action_data: Dict[str, Any],
        context: ActionContext,
        send_log_callback: Optional[callable] = None
    ) -> ActionResult:
        """
        Execute the action

        Args:
            action_data: Action-specific parameters (e.g., coordinates, text)
            context: Execution context (device ID, package, etc.)
            send_log_callback: Optional callback for sending logs

        Returns:
            ActionResult with execution results
        """
        pass

    async def send_log(
        self,
        task_id: str,
        message: str,
        log_type: str = "stdout",
        callback: Optional[callable] = None
    ):
        """
        Send a log message if callback is available

        Args:
            task_id: Task ID
            message: Log message
            log_type: Log type (stdout, stderr)
            callback: Optional log callback function
        """
        if callback:
            try:
                await callback(task_id, message, log_type)
            except Exception as e:
                # Silently fail if logging fails
                pass

    def validate_action_data(self, action_data: Dict[str, Any], required_fields: list) -> None:
        """
        Validate that required fields are present in action_data

        Args:
            action_data: Action data to validate
            required_fields: List of required field names

        Raises:
            ValueError: If required fields are missing
        """
        missing_fields = [field for field in required_fields if field not in action_data]
        if missing_fields:
            raise ValueError(f"Missing required fields in action_data: {missing_fields}")

    def __repr__(self) -> str:
        """String representation"""
        return f"{self.__class__.__name__}(type={self.action_type})"
