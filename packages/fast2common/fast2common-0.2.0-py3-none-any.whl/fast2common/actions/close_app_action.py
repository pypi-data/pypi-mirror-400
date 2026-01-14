"""
Close app action for test case steps
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional
from .base import BaseAction, ActionContext, ActionResult

logger = logging.getLogger(__name__)


class CloseAppAction(BaseAction):
    """
    Close app action implementation

    Action data format:
    {
        "package_name": "com.example.app"  # Optional (uses context if not provided)
    }
    """

    action_type = "close_app"
    description = "Close an Android application"

    async def execute(
        self,
        action_data: Dict[str, Any],
        context: ActionContext,
        send_log_callback: Optional[callable] = None
    ) -> ActionResult:
        """Execute close app action"""
        start_time = time.time()

        await self.send_log(
            context.task_id,
            "🔴 [CLOSE] Closing application",
            "stdout",
            send_log_callback
        )

        try:
            # Get package name from action_data or context
            package_name = action_data.get("package_name") or context.package_name

            if not package_name:
                error_msg = "Missing package_name"
                await self.send_log(context.task_id, f"❌ [CLOSE] {error_msg}", "stderr", send_log_callback)
                return ActionResult(
                    success=False,
                    error=error_msg,
                    execution_time=time.time() - start_time
                )

            await self.send_log(
                context.task_id,
                f"📱 [CLOSE] Force-stopping {package_name}",
                "stdout",
                send_log_callback
            )

            # Execute force-stop command via ADB
            result = await self._execute_adb_force_stop(context.device_id, package_name)

            execution_time = time.time() - start_time

            if result.get("success"):
                await self.send_log(
                    context.task_id,
                    f"✅ [CLOSE] App closed successfully in {execution_time:.2f}s",
                    "stdout",
                    send_log_callback
                )
                return ActionResult(
                    success=True,
                    message=f"Closed {package_name}",
                    data={"package_name": package_name},
                    execution_time=execution_time
                )
            else:
                error_msg = result.get("error", "Unknown error")
                await self.send_log(context.task_id, f"❌ [CLOSE] {error_msg}", "stderr", send_log_callback)
                return ActionResult(
                    success=False,
                    error=error_msg,
                    execution_time=execution_time
                )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Close app action failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            await self.send_log(context.task_id, f"❌ [CLOSE] {error_msg}", "stderr", send_log_callback)
            return ActionResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )

    async def _execute_adb_force_stop(self, device_id: str, package_name: str) -> Dict[str, Any]:
        """Execute ADB force-stop command"""
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
            cmd.extend(["shell", "am", "force-stop", package_name])

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
            logger.error(f"ADB force-stop command failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
