"""
Tap/click action for test case steps

Supports multiple coordinate resolution methods:
- Direct coordinates (x, y)
- Icon description (icon_description) with AI-based icon matching
- Text keyword (text_keyword) with OCR-based text matching
- Element ID (element_id) with UI element lookup
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from .base import BaseAction, ActionContext, ActionResult

logger = logging.getLogger(__name__)


class TapAction(BaseAction):
    """
    Tap/click action implementation

    Action data format:
    {
        "x": 100,              # Optional: direct X coordinate
        "y": 200,              # Optional: direct Y coordinate
        "icon_description": "...",  # Optional: AI icon matching
        "text_keyword": "...",     # Optional: OCR text matching
        "element_id": "...",       # Optional: UI element lookup
        "lookup_method": "auto"    # Optional: "auto", "icon", "text", "coordinate"
    }
    """

    action_type = "tap"
    description = "Tap/click on screen"

    async def execute(
        self,
        action_data: Dict[str, Any],
        context: ActionContext,
        send_log_callback: Optional[callable] = None
    ) -> ActionResult:
        """
        Execute tap action

        Args:
            action_data: Tap action parameters
            context: Execution context
            send_log_callback: Optional log callback

        Returns:
            ActionResult with tap execution result
        """
        import time
        start_time = time.time()

        await self.send_log(
            context.task_id,
            f"📍 [TAP] Starting tap action resolution...",
            "stdout",
            send_log_callback
        )

        # Log action data for debugging
        lookup_info = {
            "lookup_method": action_data.get("lookup_method", "auto"),
            "icon_description": action_data.get("icon_description"),
            "text_keyword": action_data.get("text_keyword"),
            "has_fallback_coords": bool(action_data.get("x") and action_data.get("y"))
        }
        await self.send_log(
            context.task_id,
            f"📍 [TAP] Lookup info: {lookup_info}",
            "stdout",
            send_log_callback
        )

        try:
            # Resolve coordinates using the provided method
            await self.send_log(
                context.task_id,
                f"📍 [TAP] Resolving coordinates...",
                "stdout",
                send_log_callback
            )

            x, y = await self._resolve_coordinates(action_data, context, send_log_callback)

            if x is None or y is None:
                error_msg = f"Failed to resolve coordinates. action_data: {action_data}"
                await self.send_log(context.task_id, f"❌ [TAP] {error_msg}", "stderr", send_log_callback)
                return ActionResult(
                    success=False,
                    error=error_msg,
                    execution_time=time.time() - start_time
                )

            await self.send_log(
                context.task_id,
                f"✅ [TAP] Coordinates resolved: ({x}, {y})",
                "stdout",
                send_log_callback
            )

            # Execute tap command via ADB
            await self.send_log(
                context.task_id,
                f"🔘 [TAP] Executing: adb shell input tap {x} {y}",
                "stdout",
                send_log_callback
            )

            result = await self._execute_adb_tap(context.device_id, x, y)

            execution_time = time.time() - start_time

            if result.get("success"):
                await self.send_log(
                    context.task_id,
                    f"✅ [TAP] Tap executed successfully at ({x}, {y}) in {execution_time:.2f}s",
                    "stdout",
                    send_log_callback
                )
                return ActionResult(
                    success=True,
                    message=f"Tapped at ({x}, {y})",
                    data={"x": x, "y": y},
                    execution_time=execution_time
                )
            else:
                error_msg = result.get("error", "Unknown error")
                await self.send_log(context.task_id, f"❌ [TAP] {error_msg}", "stderr", send_log_callback)
                return ActionResult(
                    success=False,
                    error=error_msg,
                    data={"x": x, "y": y},
                    execution_time=execution_time
                )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Tap action failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            await self.send_log(context.task_id, f"❌ [TAP] {error_msg}", "stderr", send_log_callback)
            return ActionResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )

    async def _resolve_coordinates(
        self,
        action_data: Dict[str, Any],
        context: ActionContext,
        send_log_callback: Optional[callable]
    ) -> tuple:
        """
        Resolve tap coordinates using various methods

        Returns:
            Tuple of (x, y) coordinates or (None, None) if failed
        """
        # Direct coordinates
        if "x" in action_data and "y" in action_data:
            return action_data["x"], action_data["y"]

        # Try icon/text-based resolution (requires node_service reference)
        # This is a placeholder - actual implementation should call the appropriate method
        # from node_service or a dedicated coordinate resolver
        try:
            # Import the coordinate resolution method from node_service
            # This will need to be refactored to a standalone function/class
            from node_service import AutoTestNodeService
            import tempfile

            # Create a temporary config for the service
            from node_config import NodeConfig
            config = NodeConfig()
            service = AutoTestNodeService(config)

            # Call the existing coordinate resolution method
            return await service._resolve_tap_coordinates(
                action_data,
                context.device_id,
                context.task_id
            )
        except Exception as e:
            logger.error(f"Failed to resolve coordinates using AI methods: {e}")
            return None, None

    async def _execute_adb_tap(self, device_id: str, x: int, y: int) -> Dict[str, Any]:
        """
        Execute ADB tap command

        Args:
            device_id: Android device ID
            x: X coordinate
            y: Y coordinate

        Returns:
            Dict with success status and output/error
        """
        try:
            import shutil
            adb_path = shutil.which("adb")

            if not adb_path:
                # Try common paths
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
            cmd.extend(["shell", "input", "tap", str(x), str(y)])

            # Execute
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return {
                    "success": True,
                    "output": stdout.decode('utf-8', errors='ignore')
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode('utf-8', errors='ignore')
                }

        except Exception as e:
            logger.error(f"ADB tap command failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
