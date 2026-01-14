"""
Swipe action for test case steps
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional
from .base import BaseAction, ActionContext, ActionResult

logger = logging.getLogger(__name__)


class SwipeAction(BaseAction):
    """
    Swipe action implementation

    Action data format:
    {
        "start_x": 100,      # Starting X coordinate (or x1)
        "start_y": 200,      # Starting Y coordinate (or y1)
        "end_x": 300,        # Ending X coordinate (or x2)
        "end_y": 400,        # Ending Y coordinate (or y2)
        "duration_ms": 300,  # Swipe duration in milliseconds (optional, default 300)
        "duration": 300      # Same as duration_ms (alternative key)
    }
    """

    action_type = "swipe"
    description = "Swipe/drag gesture on screen"

    async def execute(
        self,
        action_data: Dict[str, Any],
        context: ActionContext,
        send_log_callback: Optional[callable] = None
    ) -> ActionResult:
        """Execute swipe action"""
        start_time = time.time()

        await self.send_log(
            context.task_id,
            f"👆 [SWIPE] Executing swipe gesture",
            "stdout",
            send_log_callback
        )

        try:
            # Extract coordinates (support both naming conventions)
            x1 = action_data.get("start_x") or action_data.get("x1")
            y1 = action_data.get("start_y") or action_data.get("y1")
            x2 = action_data.get("end_x") or action_data.get("x2")
            y2 = action_data.get("end_y") or action_data.get("y2")
            duration = action_data.get("duration_ms") or action_data.get("duration", 300)

            # Validate coordinates
            if not all(v is not None for v in [x1, y1, x2, y2]):
                error_msg = f"Missing coordinates in action_data: {action_data}"
                await self.send_log(context.task_id, f"❌ [SWIPE] {error_msg}", "stderr", send_log_callback)
                return ActionResult(
                    success=False,
                    error=error_msg,
                    execution_time=time.time() - start_time
                )

            await self.send_log(
                context.task_id,
                f"📍 [SWIPE] From ({x1}, {y1}) to ({x2}, {y2}), duration {duration}ms",
                "stdout",
                send_log_callback
            )

            # Execute swipe via ADB
            result = await self._execute_adb_swipe(
                context.device_id,
                x1, y1, x2, y2,
                duration
            )

            execution_time = time.time() - start_time

            if result.get("success"):
                await self.send_log(
                    context.task_id,
                    f"✅ [SWIPE] Swipe completed successfully in {execution_time:.2f}s",
                    "stdout",
                    send_log_callback
                )
                return ActionResult(
                    success=True,
                    message=f"Swiped from ({x1}, {y1}) to ({x2}, {y2})",
                    data={"x1": x1, "y1": y1, "x2": x2, "y2": y2, "duration": duration},
                    execution_time=execution_time
                )
            else:
                error_msg = result.get("error", "Unknown error")
                await self.send_log(context.task_id, f"❌ [SWIPE] {error_msg}", "stderr", send_log_callback)
                return ActionResult(
                    success=False,
                    error=error_msg,
                    execution_time=execution_time
                )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Swipe action failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            await self.send_log(context.task_id, f"❌ [SWIPE] {error_msg}", "stderr", send_log_callback)
            return ActionResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )

    async def _execute_adb_swipe(
        self,
        device_id: str,
        x1: int, y1: int,
        x2: int, y2: int,
        duration: int
    ) -> Dict[str, Any]:
        """Execute ADB swipe command"""
        try:
            import shutil
            adb_path = shutil.which("adb")

            if not adb_path:
                from pathlib import Path
                common_paths = [
                    Path("/usr/local/bin/adb"),
                    Path("/opt/homebrew/bin/adb"),
                    Path.home() / "Library" / "Android" / "sdk" / "platform-tools" / "adb",
                ]
                for path in common_paths:
                    if path.exists():
                        adb_path = str(path)
                        break

            if not adb_path:
                raise FileNotFoundError("ADB not found")

            # Build command
            cmd = [adb_path]
            if device_id:
                cmd.extend(["-s", device_id])
            cmd.extend(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)])

            # Execute
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return {"success": True, "output": stdout.decode('utf-8', errors='ignore')}
            else:
                return {"success": False, "error": stderr.decode('utf-8', errors='ignore')}

        except Exception as e:
            logger.error(f"ADB swipe command failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
