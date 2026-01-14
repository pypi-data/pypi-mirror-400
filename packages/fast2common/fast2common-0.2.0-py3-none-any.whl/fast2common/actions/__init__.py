"""
Test case step actions for automated testing

This module provides a collection of action implementations for test case steps.
Each action type is implemented in a separate file for easy maintenance and extension.

Action types:
- tap: Tap/click on screen coordinates or elements
- swipe: Swipe/drag gesture
- launch_app: Launch an application
- close_app: Close an application
- input: Input text
- wait: Wait for a specified duration
- press_back: Press back button
- screenshot: Take a screenshot
"""

from .base import BaseAction, ActionContext, ActionResult
from .executor import ActionExecutor

__all__ = [
    'BaseAction',
    'ActionContext',
    'ActionResult',
    'ActionExecutor',
]

# Import all action classes
from .tap_action import TapAction
from .swipe_action import SwipeAction
from .launch_app_action import LaunchAppAction
from .close_app_action import CloseAppAction
from .input_action import InputAction
from .wait_action import WaitAction
from .press_back_action import PressBackAction
from .screenshot_action import ScreenshotAction

__all__.extend([
    'TapAction',
    'SwipeAction',
    'LaunchAppAction',
    'CloseAppAction',
    'InputAction',
    'WaitAction',
    'PressBackAction',
    'ScreenshotAction',
])
