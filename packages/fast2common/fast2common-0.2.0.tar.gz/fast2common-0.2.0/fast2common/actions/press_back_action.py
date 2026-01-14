"""
Press back action for test case steps
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional
from .base import BaseAction, ActionContext, ActionResult

logger = logging.getLogger(__name__)


class PressBackAction(BaseAction):
    """
    Press back button action implementation

    Action data format: {} (no parameters needed)
    """

    action_type = "press_back"
    description = "Press Android back button"

    async def execute(
        self,
        action_data: Dict[str, Any],
        context: ActionContext,
        send_log_callback: Optional[callable] = None
    ) -> ActionResult:
        """Execute press back action"""
        start_time = time.time()

        await self.send_log(
            context.task_id,
            "🔙 [BACK] Pressing back button",
            "stdout",
            send_log_callback
        )

        try:
            # Execute back keyevent via ADB
            result = await self._execute_adb_press_back(context.device_id)

            execution_time = time.time() - start_time

            if result.get("success"):
                await self.send_log(
                    context.task_id,
                    f"✅ [BACK] Back button pressed successfully in {execution_time:.2f}s",
                    "stdout",
                    send_log_callback
                )
                return ActionResult(
                    success=True,
                    message="Pressed back button",
                    execution_time=execution_time
                )
            else:
                error_msg = result.get("error", "Unknown error")
                await self.send_log(context.task_id, f"❌ [BACK] {error_msg}", "stderr", send_log_callback)
                return ActionResult(
                    success=False,
                    error=error_msg,
                    execution_time=execution_time
                )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Press back action failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            await self.send_log(context.task_id, f"❌ [BACK] {error_msg}", "stderr", send_log_callback)
            return ActionResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )

    async def _execute_adb_press_back(self, device_id: str) -> Dict[str, Any]:
        """Execute ADB press back command (keyevent 4)"""
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

            # Build command (keyevent 4 = BACK)
            cmd = [adb_path]
            if device_id:
                cmd.extend(["-s", device_id])
            cmd.extend(["shell", "input", "keyevent", "4"])

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
            logger.error(f"ADB press back command failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
