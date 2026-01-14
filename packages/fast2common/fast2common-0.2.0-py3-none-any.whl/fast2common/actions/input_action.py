"""
Input text action for test case steps
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional
from .base import BaseAction, ActionContext, ActionResult

logger = logging.getLogger(__name__)


class InputAction(BaseAction):
    """
    Input text action implementation

    Action data format:
    {
        "text": "Hello World"  # Text to input
    }
    """

    action_type = "输入"  # Keeping Chinese for backward compatibility
    description = "Input text into device"

    async def execute(
        self,
        action_data: Dict[str, Any],
        context: ActionContext,
        send_log_callback: Optional[callable] = None
    ) -> ActionResult:
        """Execute input text action"""
        start_time = time.time()

        await self.send_log(
            context.task_id,
            "⌨️  [INPUT] Inputting text",
            "stdout",
            send_log_callback
        )

        try:
            text = action_data.get("text")

            if not text:
                error_msg = "Missing 'text' in action_data"
                await self.send_log(context.task_id, f"❌ [INPUT] {error_msg}", "stderr", send_log_callback)
                return ActionResult(
                    success=False,
                    error=error_msg,
                    execution_time=time.time() - start_time
                )

            await self.send_log(
                context.task_id,
                f"📝 [INPUT] Text: {text[:50]}{'...' if len(text) > 50 else ''}",
                "stdout",
                send_log_callback
            )

            # Check device state first
            check_result = await self._check_device_state(context.device_id)
            if not check_result.get("success") or check_result.get("output", "").strip() != "device":
                error_msg = f"Device {context.device_id} is not ready (state: {check_result.get('output', '').strip()})"
                await self.send_log(context.task_id, f"❌ [INPUT] {error_msg}", "stderr", send_log_callback)
                return ActionResult(
                    success=False,
                    error=error_msg,
                    execution_time=time.time() - start_time
                )

            # Execute input text command via ADB
            result = await self._execute_adb_input_text(context.device_id, text)

            execution_time = time.time() - start_time

            if result.get("success"):
                await self.send_log(
                    context.task_id,
                    f"✅ [INPUT] Text input successfully in {execution_time:.2f}s",
                    "stdout",
                    send_log_callback
                )
                return ActionResult(
                    success=True,
                    message=f"Input text: {text[:50]}",
                    data={"text": text},
                    execution_time=execution_time
                )
            else:
                error_msg = result.get("error", "Unknown error")
                await self.send_log(context.task_id, f"❌ [INPUT] {error_msg}", "stderr", send_log_callback)
                return ActionResult(
                    success=False,
                    error=error_msg,
                    execution_time=execution_time
                )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Input action failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            await self.send_log(context.task_id, f"❌ [INPUT] {error_msg}", "stderr", send_log_callback)
            return ActionResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )

    async def _check_device_state(self, device_id: str) -> Dict[str, Any]:
        """Check if device is ready"""
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
            cmd.extend(["get-state"])

            # Execute
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return {"success": True, "output": stdout.decode('utf-8', errors='ignore').strip()}
            else:
                return {"success": False, "error": stderr.decode('utf-8', errors='ignore')}

        except Exception as e:
            logger.error(f"ADB get-state command failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def _execute_adb_input_text(self, device_id: str, text: str) -> Dict[str, Any]:
        """Execute ADB input text command"""
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
            cmd.extend(["shell", "input", "text", text])

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
            logger.error(f"ADB input text command failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
