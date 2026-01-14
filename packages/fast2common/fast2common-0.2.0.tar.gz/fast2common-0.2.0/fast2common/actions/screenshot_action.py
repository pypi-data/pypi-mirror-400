"""
Screenshot action for test case steps
"""

import logging
import time
from typing import Dict, Any, Optional
from .base import BaseAction, ActionContext, ActionResult

logger = logging.getLogger(__name__)


class ScreenshotAction(BaseAction):
    """
    Screenshot action implementation

    This action doesn't take a screenshot itself - it's a marker step
    that indicates a screenshot should be captured as part of the step execution flow.
    The actual screenshot is taken by the test case executor after each step.

    Action data format: {} (no parameters needed)
    """

    action_type = "screenshot"
    description = "Take a screenshot (marker action)"

    async def execute(
        self,
        action_data: Dict[str, Any],
        context: ActionContext,
        send_log_callback: Optional[callable] = None
    ) -> ActionResult:
        """Execute screenshot action (marker only)"""
        start_time = time.time()

        await self.send_log(
            context.task_id,
            "📸 [SCREENSHOT] Screenshot marker step",
            "stdout",
            send_log_callback
        )

        # This is just a marker - the actual screenshot is taken
        # by the test case executor
        return ActionResult(
            success=True,
            message="Screenshot marker step (actual screenshot taken by executor)",
            execution_time=time.time() - start_time
        )
