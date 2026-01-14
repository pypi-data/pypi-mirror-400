"""
Wait action for test case steps
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional
from .base import BaseAction, ActionContext, ActionResult

logger = logging.getLogger(__name__)


class WaitAction(BaseAction):
    """
    Wait action implementation

    Action data format:
    {
        "duration": 1  # Wait duration in seconds (default: 1)
    }
    """

    action_type = "wait"
    description = "Wait for a specified duration"

    async def execute(
        self,
        action_data: Dict[str, Any],
        context: ActionContext,
        send_log_callback: Optional[callable] = None
    ) -> ActionResult:
        """Execute wait action"""
        start_time = time.time()

        wait_time = action_data.get("duration", 1)

        await self.send_log(
            context.task_id,
            f"⏳ [WAIT] Waiting {wait_time}s",
            "stdout",
            send_log_callback
        )

        try:
            await asyncio.sleep(wait_time)

            execution_time = time.time() - start_time

            await self.send_log(
                context.task_id,
                f"✅ [WAIT] Wait completed in {execution_time:.2f}s",
                "stdout",
                send_log_callback
            )

            return ActionResult(
                success=True,
                message=f"Waited {wait_time}s",
                data={"duration": wait_time},
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Wait action failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            await self.send_log(context.task_id, f"❌ [WAIT] {error_msg}", "stderr", send_log_callback)
            return ActionResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
