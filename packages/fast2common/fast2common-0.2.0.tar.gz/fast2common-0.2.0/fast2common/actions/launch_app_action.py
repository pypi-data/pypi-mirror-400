"""
Launch app action for test case steps
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional
from .base import BaseAction, ActionContext, ActionResult

logger = logging.getLogger(__name__)


class LaunchAppAction(BaseAction):
    """
    Launch app action implementation

    Action data format:
    {
        "package_name": "com.example.app",      # Optional (uses context if not provided)
        "main_activity": ".MainActivity",       # Optional (uses context if not provided)
        "wait_time": 2                          # Optional: wait time after launch (seconds, default 2)
    }
    """

    action_type = "launch_app"
    description = "Launch an Android application"

    async def execute(
        self,
        action_data: Dict[str, Any],
        context: ActionContext,
        send_log_callback: Optional[callable] = None
    ) -> ActionResult:
        """Execute launch app action"""
        start_time = time.time()

        await self.send_log(
            context.task_id,
            "🚀 [LAUNCH] Starting application launch",
            "stdout",
            send_log_callback
        )

        try:
            # Get package info from action_data or context
            package_name = action_data.get("package_name") or context.package_name
            main_activity = action_data.get("main_activity") or context.main_activity
            wait_time = action_data.get("wait_time", 2)

            if not package_name or not main_activity:
                error_msg = "Missing package_name or main_activity"
                await self.send_log(context.task_id, f"❌ [LAUNCH] {error_msg}", "stderr", send_log_callback)
                return ActionResult(
                    success=False,
                    error=error_msg,
                    execution_time=time.time() - start_time
                )

            await self.send_log(
                context.task_id,
                f"📱 [LAUNCH] Launching {package_name}/{main_activity}",
                "stdout",
                send_log_callback
            )

            # Construct full activity path
            if '/' in main_activity:
                full_activity = main_activity
            elif main_activity.startswith('.'):
                full_activity = f"{package_name}/{main_activity}"
            else:
                full_activity = f"{package_name}/{main_activity}"

            # Execute launch command via ADB
            result = await self._execute_adb_launch(context.device_id, full_activity)

            if not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                await self.send_log(context.task_id, f"❌ [LAUNCH] {error_msg}", "stderr", send_log_callback)
                return ActionResult(
                    success=False,
                    error=error_msg,
                    execution_time=time.time() - start_time
                )

            # Wait for app to stabilize
            await self.send_log(
                context.task_id,
                f"⏳ [LAUNCH] Waiting {wait_time}s for app to stabilize",
                "stdout",
                send_log_callback
            )
            await asyncio.sleep(wait_time)

            execution_time = time.time() - start_time
            await self.send_log(
                context.task_id,
                f"✅ [LAUNCH] App launched successfully in {execution_time:.2f}s",
                "stdout",
                send_log_callback
            )

            return ActionResult(
                success=True,
                message=f"Launched {package_name}",
                data={"package_name": package_name, "main_activity": main_activity},
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Launch app action failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            await self.send_log(context.task_id, f"❌ [LAUNCH] {error_msg}", "stderr", send_log_callback)
            return ActionResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )

    async def _execute_adb_launch(self, device_id: str, full_activity: str) -> Dict[str, Any]:
        """Execute ADB launch command"""
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
            cmd.extend(["shell", "am", "start", "-n", full_activity])

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
            logger.error(f"ADB launch command failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
