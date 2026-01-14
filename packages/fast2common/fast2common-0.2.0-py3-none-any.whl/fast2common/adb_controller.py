#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADB 控制器 - 负责所有 ADB 命令的执行和设备交互
"""

import os
import time
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple


class ADBController:
    """ADB 命令控制器"""
    
    def __init__(self, device_id: str = None, adb_timeout: int = 30, retry_count: int = 2, 
                 terminal_id: str = None, executor = None):
        """
        初始化 ADB 控制器
        
        Args:
            device_id: 设备ID，如果为None则自动检测
            adb_timeout: ADB命令超时时间（秒）
            retry_count: 重试次数
            terminal_id: 远程终端ID（可选，用于远程执行）
            executor: 执行器实例（可选，用于远程执行ADB命令）
        """
        self.adb_path = self._find_adb()
        self.device_id = device_id or self._detect_device()
        self.adb_timeout = adb_timeout
        self.retry_count = retry_count
        self.terminal_id = terminal_id
        self.executor = executor
        self._cached_screen_size = None
        
        # print(f"✅ ADB 控制器初始化完成")
        # print(f"   ADB 路径: {self.adb_path}")
        # print(f"   设备 ID: {self.device_id}")
        # if self.executor:
        #     print(f"   远程终端: {self.terminal_id or 'N/A'}")
    
    def _find_adb(self) -> str:
        """查找 ADB 路径"""
        common_paths = [
            "/Users/fansc/Library/Android/sdk/platform-tools/adb",
            "/usr/local/bin/adb",
            "/opt/homebrew/bin/adb",
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        try:
            result = subprocess.run(["which", "adb"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        raise FileNotFoundError("无法找到 ADB")
    
    def _detect_device(self) -> str:
        """自动检测连接的设备"""
        try:
            result = subprocess.run([self.adb_path, "devices"], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')[1:]
            devices = [line.split()[0] for line in lines if '\tdevice' in line]
            
            if not devices:
                raise RuntimeError("未检测到连接的设备")
            
            return devices[0]
        except Exception as e:
            raise RuntimeError(f"设备检测失败: {e}")
    
    def run(self, args: List[str], timeout: int = None, retry: int = None) -> subprocess.CompletedProcess:
        """
        运行 ADB 命令（带重试和超时控制）
        
        Args:
            args: ADB命令参数列表
            timeout: 超时时间（秒），默认使用配置值
            retry: 重试次数，默认使用配置值
            
        Returns:
            subprocess.CompletedProcess 对象（本地执行）或类似对象（远程执行）
        """
        if timeout is None:
            timeout = self.adb_timeout
        if retry is None:
            retry = self.retry_count
        
        # If executor is available, use remote execution
        if self.executor:
            return self._run_remote(args, timeout, retry)
        else:
            return self._run_local(args, timeout, retry)
    
    def _run_local(self, args: List[str], timeout: int, retry: int) -> subprocess.CompletedProcess:
        """Run ADB command locally"""
        cmd = [self.adb_path, "-s", self.device_id] + args
        last_error = None
        
        for attempt in range(retry):
            try:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=timeout
                )
                
                # 检查常见错误
                if result.stderr:
                    stderr_lower = result.stderr.lower()
                    
                    # 设备离线错误
                    if "device offline" in stderr_lower or "device not found" in stderr_lower:
                        if attempt < retry - 1:
                            print(f"  ⚠️  设备离线，尝试重连... ({attempt + 1}/{retry})")
                            time.sleep(1)
                            continue
                
                return result
                
            except subprocess.TimeoutExpired as e:
                last_error = e
                if attempt < retry - 1:
                    print(f"  ⚠️  ADB 命令超时，重试 {attempt + 1}/{retry}...")
                    time.sleep(1)
                    continue
                else:
                    print(f"  ❌ ADB 命令超时失败: {' '.join(cmd)}")
                    raise
            
            except Exception as e:
                last_error = e
                if attempt < retry - 1:
                    print(f"  ⚠️  ADB 命令失败: {e}，重试 {attempt + 1}/{retry}...")
                    time.sleep(1)
                    continue
                else:
                    raise
        
        # 如果所有重试都失败
        if last_error:
            raise last_error
        
        return result
    
    def _run_remote(self, args: List[str], timeout: int, retry: int):
        """Run ADB command remotely via SSH executor"""
        # Build ADB command: adb -s device_id args...
        cmd = [self.adb_path, "-s", self.device_id] + args
        
        last_error = None
        
        for attempt in range(retry):
            try:
                # Execute command via SSH executor
                result = self.executor.execute_command(cmd, timeout=timeout)
                
                # Convert result to subprocess-like object
                class RemoteResult:
                    def __init__(self, result_dict):
                        self.returncode = result_dict.get("returncode", 0)
                        self.stdout = result_dict.get("stdout", "")
                        self.stderr = result_dict.get("stderr", "")
                        self.success = result_dict.get("success", False)
                
                remote_result = RemoteResult(result)
                
                # 检查常见错误
                if remote_result.stderr:
                    stderr_lower = remote_result.stderr.lower()
                    
                    # 设备离线错误
                    if "device offline" in stderr_lower or "device not found" in stderr_lower:
                        if attempt < retry - 1:
                            print(f"  ⚠️  设备离线，尝试重连... ({attempt + 1}/{retry})")
                            time.sleep(1)
                            continue
                
                return remote_result
                
            except Exception as e:
                last_error = e
                if attempt < retry - 1:
                    print(f"  ⚠️  远程 ADB 命令失败: {e}，重试 {attempt + 1}/{retry}...")
                    time.sleep(1)
                    continue
                else:
                    raise
        
        # 如果所有重试都失败
        if last_error:
            raise last_error
        
        return remote_result
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        获取并缓存屏幕尺寸
        
        Returns:
            (width, height) 屏幕宽高元组
        """
        if self._cached_screen_size is not None:
            return self._cached_screen_size
        
        result = self.run(["shell", "wm", "size"])
        # 解析屏幕尺寸（例：Physical size: 1080x2400）
        import re
        match = re.search(r'(\d+)x(\d+)', result.stdout)
        if match:
            self._cached_screen_size = (int(match.group(1)), int(match.group(2)))
        else:
            # 默认值
            self._cached_screen_size = (1080, 2400)
            print(f"  ⚠️  无法获取屏幕尺寸，使用默认值: {self._cached_screen_size}")
        
        return self._cached_screen_size
    
    def screenshot(self, save_path: Path) -> bool:
        """
        截图并保存到本地
        
        Args:
            save_path: 本地保存路径
            
        Returns:
            是否成功
        """
        device_path = f"/sdcard/screenshot_temp.png"
        
        try:
            # Ensure parent directory exists
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 截图
            print(f"  📸 Taking screenshot on device: {device_path}")
            print(f"     Device ID: {self.device_id}")
            print(f"     Save path: {save_path}")
            
            result = self.run(["shell", "screencap", "-p", device_path])
            if result.returncode != 0:
                print(f"  ⚠️  screencap 失败:")
                print(f"     Return code: {result.returncode}")
                print(f"     stderr: {result.stderr}")
                print(f"     stdout: {result.stdout}")
                
                # Check for common errors
                stderr_lower = (result.stderr or "").lower()
                if "permission denied" in stderr_lower:
                    print(f"  ❌ Permission denied - device may require root access")
                elif "device offline" in stderr_lower or "device not found" in stderr_lower:
                    print(f"  ❌ Device offline or not found")
                elif "no such file" in stderr_lower:
                    print(f"  ❌ Device path not accessible")
                
                return False
            print(f"  ✅ Screenshot captured on device successfully")
            
            # 拉取到本地
            print(f"  📥 Pulling screenshot from device to local: {save_path}")
            result = self.run(["pull", device_path, str(save_path)])
            if result.returncode != 0:
                print(f"  ⚠️  pull 截图失败:")
                print(f"     Return code: {result.returncode}")
                print(f"     stderr: {result.stderr}")
                print(f"     stdout: {result.stdout}")
                
                # Check for common errors
                stderr_lower = (result.stderr or "").lower()
                if "no such file" in stderr_lower:
                    print(f"  ❌ Screenshot file not found on device")
                elif "permission denied" in stderr_lower:
                    print(f"  ❌ Permission denied when pulling file")
                
                return False
            print(f"  ✅ Screenshot pulled to local successfully")
            
            # 验证文件是否存在
            if not save_path.exists():
                print(f"  ⚠️  截图文件不存在: {save_path}")
                print(f"     Parent directory exists: {save_path.parent.exists()}")
                print(f"     Parent directory: {save_path.parent}")
                return False
            
            # 获取文件大小
            file_size = save_path.stat().st_size
            print(f"  📊 Screenshot file size: {file_size / 1024:.1f}KB")
            
            # Validate file is not empty
            if file_size == 0:
                print(f"  ⚠️  截图文件为空 (0 bytes)")
                save_path.unlink()  # Remove empty file
                return False
            
            # 清理设备端文件
            print(f"  🗑️  Cleaning up device screenshot file...")
            cleanup_result = self.run(["shell", "rm", device_path])
            if cleanup_result.returncode == 0:
                print(f"  ✅ Device screenshot file cleaned up")
            else:
                print(f"  ⚠️  Failed to clean up device file (non-critical)")
            
            print(f"  ✅ Screenshot process completed successfully")
            return True
        except subprocess.TimeoutExpired as e:
            print(f"  ❌ 截图超时: {e}")
            print(f"     Command timeout after {e.timeout} seconds")
            return False
        except FileNotFoundError as e:
            print(f"  ❌ 文件路径错误: {e}")
            print(f"     Save path: {save_path}")
            return False
        except PermissionError as e:
            print(f"  ❌ 权限错误: {e}")
            print(f"     Save path: {save_path}")
            print(f"     Parent directory writable: {save_path.parent.exists() and os.access(save_path.parent, os.W_OK)}")
            return False
        except Exception as e:
            print(f"  ❌ 截图异常: {e}")
            print(f"     Exception type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False
    
    def tap(self, x: int, y: int) -> bool:
        """
        点击屏幕坐标
        
        Args:
            x: X坐标
            y: Y坐标
            
        Returns:
            是否成功
        """
        try:
            result = self.run(["shell", "input", "tap", str(x), str(y)])
            return result.returncode == 0
        except Exception as e:
            print(f"  ❌ 点击失败: {e}")
            return False
    
    def click(self, x: int, y: int) -> bool:
        """
        点击屏幕坐标（tap 的别名）
        
        Args:
            x: X坐标
            y: Y坐标
            
        Returns:
            是否成功
        """
        return self.tap(x, y)
    
    def show_coordinate_marker(self, x: int, y: int, duration: float = 2.0) -> bool:
        """
        在设备屏幕上显示坐标点标记
        
        通过以下方式实现：
        1. 在坐标点执行一个短暂的 tap（产生视觉反馈）
        2. 使用 toast 消息显示坐标信息
        
        Args:
            x: X坐标
            y: Y坐标
            duration: 显示持续时间（秒），默认2秒
            
        Returns:
            是否成功
        """
        try:
            # Method 1: Show toast message with coordinates
            toast_text = f"坐标: ({x}, {y})"
            # Use am broadcast to show toast (requires accessibility or root)
            # Alternative: use input tap to create visual feedback
            result = self.run([
                "shell", "am", "broadcast", "-a", "android.intent.action.SHOW_TOAST",
                "--es", "message", toast_text
            ])
            
            # Method 2: Create visual feedback by tapping the coordinate
            # This will show a brief ripple effect at the coordinate
            if self.tap(x, y):
                print(f"  ✅ 已在坐标 ({x}, {y}) 显示标记（点击反馈）")
                return True
            else:
                print(f"  ⚠️  无法在坐标 ({x}, {y}) 显示标记")
                return False
                
        except Exception as e:
            print(f"  ❌ 显示坐标标记失败: {e}")
            return False
    
    def mark_coordinate_on_screenshot(
        self, 
        screenshot_path: Path, 
        x: int, 
        y: int,
        marker_radius: int = 30,
        marker_color: Tuple[int, int, int] = (255, 0, 0),
        save_path: Optional[Path] = None
    ) -> Optional[Path]:
        """
        在截图上标记坐标点
        
        Args:
            screenshot_path: 截图文件路径
            x: X坐标
            y: Y坐标
            marker_radius: 标记圆圈半径（像素），默认30
            marker_color: 标记颜色 RGB，默认红色 (255, 0, 0)
            save_path: 保存路径，如果为None则覆盖原文件
            
        Returns:
            标记后的截图路径，失败返回None
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Open image
            img = Image.open(screenshot_path)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create drawing context
            draw = ImageDraw.Draw(img)
            
            # Draw outer circle (thicker border)
            left = x - marker_radius
            top = y - marker_radius
            right = x + marker_radius
            bottom = y + marker_radius
            
            # Draw outer circle
            draw.ellipse(
                [left, top, right, bottom],
                outline=marker_color,
                width=3
            )
            
            # Draw inner circle (semi-transparent)
            inner_radius = marker_radius - 3
            inner_left = x - inner_radius
            inner_top = y - inner_radius
            inner_right = x + inner_radius
            inner_bottom = y + inner_radius
            
            # Create semi-transparent overlay
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.ellipse(
                [inner_left, inner_top, inner_right, inner_bottom],
                fill=(*marker_color, 80)  # Semi-transparent fill
            )
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            
            # Draw center point
            point_size = 5
            draw.ellipse(
                [x - point_size, y - point_size, 
                 x + point_size, y + point_size],
                fill=marker_color
            )
            
            # Draw coordinate text
            try:
                # Try to use default font
                font = ImageFont.load_default()
            except:
                font = None
            
            text = f"({x}, {y})"
            text_bbox = draw.textbbox((0, 0), text, font=font) if font else None
            text_width = text_bbox[2] - text_bbox[0] if text_bbox else len(text) * 6
            text_height = text_bbox[3] - text_bbox[1] if text_bbox else 12
            
            # Draw text background
            text_x = x - text_width // 2
            text_y = y + marker_radius + 5
            draw.rectangle(
                [text_x - 4, text_y - 2, text_x + text_width + 4, text_y + text_height + 2],
                fill=(0, 0, 0, 200)
            )
            
            # Draw text
            draw.text(
                (text_x, text_y),
                text,
                fill=(255, 255, 255),
                font=font
            )
            
            # Save marked image
            output_path = save_path if save_path else screenshot_path
            img.save(output_path, quality=95)
            
            print(f"  ✅ 已在截图上标记坐标 ({x}, {y}): {output_path}")
            return output_path
            
        except ImportError:
            print(f"  ⚠️  PIL (Pillow) 未安装，无法在截图上标记坐标")
            print(f"     请安装: pip install Pillow")
            return None
        except Exception as e:
            print(f"  ❌ 在截图上标记坐标失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def click_by_text(self, text: str) -> bool:
        """
        通过文本点击元素
        
        Args:
            text: 元素文本
            
        Returns:
            是否成功
        """
        try:
            # 获取 UI 元素（使用 ADBController 自己的方法）
            elements = self.get_ui_dump()
            if not elements:
                return False
            
            # 查找匹配文本的元素（支持可点击父容器）
            target_elem = None
            for elem in elements:
                # 精确匹配
                if elem.get('text') == text and elem.get('clickable'):
                    target_elem = elem
                    break
            
            # 如果没找到精确匹配，尝试查找可点击的父容器
            if not target_elem:
                for elem in elements:
                    if elem.get('text') == text:
                        # 向上查找可点击的父元素
                        parent_idx = elem.get('parent_idx')
                        while parent_idx is not None and parent_idx < len(elements):
                            parent = elements[parent_idx]
                            if parent.get('clickable'):
                                target_elem = parent
                                break
                            parent_idx = parent.get('parent_idx')
                        if target_elem:
                            break
            
            if not target_elem:
                return False
            
            # 解析坐标并点击
            bounds_str = target_elem.get('bounds', '')
            if bounds_str:
                import re
                matches = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
                if len(matches) == 2:
                    x1, y1 = int(matches[0][0]), int(matches[0][1])
                    x2, y2 = int(matches[1][0]), int(matches[1][1])
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    return self.click(center_x, center_y)
            
            return False
        except Exception as e:
            print(f"  ❌ 通过文本点击失败: {e}")
            return False
    
    def click_by_resource_id(self, resource_id: str) -> bool:
        """
        通过 resource-id 点击元素
        
        Args:
            resource_id: 元素的 resource-id
            
        Returns:
            是否成功
        """
        try:
            # 获取 UI 元素
            elements = self.get_ui_dump()
            if not elements:
                return False
            
            # 查找匹配 resource_id 的元素
            for elem in elements:
                if elem.get('resource_id') == resource_id and elem.get('clickable'):
                    bounds_str = elem.get('bounds', '')
                    if bounds_str:
                        # 解析坐标并点击
                        import re
                        matches = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
                        if len(matches) == 2:
                            x1, y1 = int(matches[0][0]), int(matches[0][1])
                            x2, y2 = int(matches[1][0]), int(matches[1][1])
                            center_x = (x1 + x2) // 2
                            center_y = (y1 + y2) // 2
                            return self.click(center_x, center_y)
            
            return False
        except Exception as e:
            print(f"  ❌ 通过 resource_id 点击失败: {e}")
            return False
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """
        滑动屏幕
        
        Args:
            x1, y1: 起点坐标
            x2, y2: 终点坐标
            duration: 持续时间（毫秒）
            
        Returns:
            是否成功
        """
        try:
            result = self.run([
                "shell", "input", "swipe", 
                str(x1), str(y1), str(x2), str(y2), str(duration)
            ])
            return result.returncode == 0
        except Exception as e:
            print(f"  ❌ 滑动失败: {e}")
            return False
    
    def press_back(self) -> bool:
        """
        按返回键
        
        Returns:
            是否成功
        """
        try:
            result = self.run(["shell", "input", "keyevent", "4"])
            return result.returncode == 0
        except Exception as e:
            print(f"  ❌ 按返回键失败: {e}")
            return False
    
    def get_ui_xml(self, save_path: Path) -> bool:
        """
        获取 UI XML 并保存到本地
        
        Args:
            save_path: 本地保存路径
            
        Returns:
            是否成功
        """
        try:
            # Ensure parent directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 获取 UI 层次结构
            dump_result = self.run(["shell", "uiautomator", "dump", "/sdcard/window_dump.xml"])
            if dump_result.returncode != 0:
                print(f"  ❌ uiautomator dump failed: {dump_result.stderr}")
                return False
            
            # 拉取 XML 文件
            pull_result = self.run(["pull", "/sdcard/window_dump.xml", str(save_path)])
            if pull_result.returncode != 0:
                print(f"  ❌ adb pull failed: {pull_result.stderr}")
                return False
            
            # Verify file was actually saved
            if not save_path.exists():
                print(f"  ❌ UI XML file not found after pull: {save_path}")
                return False
            
            # Verify file is not empty
            if save_path.stat().st_size == 0:
                print(f"  ❌ UI XML file is empty: {save_path}")
                return False
            
            return True
        except Exception as e:
            print(f"  ❌ 获取 UI XML 失败: {e}")
            return False
    
    def get_ui_dump(self) -> list:
        """
        获取 UI 层次结构并解析为元素列表
        
        Returns:
            元素列表，每个元素是一个字典包含属性信息
        """
        try:
            import tempfile
            import xml.etree.ElementTree as ET
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
                tmp_path = Path(tmp.name)
            
            # 获取 UI XML
            if not self.get_ui_xml(tmp_path):
                return []
            
            # 解析 XML
            tree = ET.parse(tmp_path)
            root = tree.getroot()
            
            # 递归提取节点，保留父子关系
            elements = []
            def extract_node(node, parent_idx=None):
                current_idx = len(elements)
                elem = {
                    'tag': node.tag,
                    'resource_id': node.get('resource-id', ''),
                    'text': node.get('text', ''),
                    'class': node.get('class', ''),
                    'bounds': node.get('bounds', ''),
                    'clickable': node.get('clickable', 'false') == 'true',
                    'enabled': node.get('enabled', 'false') == 'true',
                    'content_desc': node.get('content-desc', ''),
                    'parent_idx': parent_idx,  # 保存父节点索引
                    'xml_node': node  # 保存原始节点引用（用于查找父节点）
                }
                elements.append(elem)
                
                # 递归处理子节点
                for child in node:
                    extract_node(child, current_idx)
            
            extract_node(root)
            
            # 删除临时文件
            tmp_path.unlink(missing_ok=True)
            
            return elements
            
        except Exception as e:
            print(f"  ❌ 获取 UI 层次结构失败: {e}")
            return []
    
    def start_app(self, activity: str) -> bool:
        """
        启动应用
        
        Args:
            activity: Activity 名称（完整路径）
            
        Returns:
            是否成功
        """
        try:
            result = self.run(["shell", "am", "start", "-n", activity])
            return result.returncode == 0
        except Exception as e:
            print(f"  ❌ 启动应用失败: {e}")
            return False
    
    def launch_app(self, package: str, activity: str) -> bool:
        """
        启动应用（使用包名和 Activity）
        
        Args:
            package: 应用包名 (例如: com.jiaming.en)
            activity: Activity 名称 (例如: com.jiaming.bdc.EntryActivity 或 .MainActivity)
            
        Returns:
            是否成功
        """
        # 构造完整的 Activity 路径
        if '/' in activity:
            # 已经是完整路径 (package/activity)，直接使用
            # 例如: com.jiaming.en/com.jiaming.bdc.EntryActivity
            full_activity = activity
        elif activity.startswith('.'):
            # 相对路径 (.MainActivity)，需要拼接包名
            full_activity = f"{package}/{activity}"
        else:
            # 完整类名 (com.jiaming.bdc.EntryActivity)
            # 注意：Activity 的完整类名可能不在应用包名下
            # 例如：com.jiaming.bdc.EntryActivity 在 com.jiaming.en 应用中
            # 启动命令应该是: com.jiaming.en/com.jiaming.bdc.EntryActivity
            full_activity = f"{package}/{activity}"
        
        # 调用 start_app
        return self.start_app(full_activity)
    
    def stop_app(self, package: str) -> bool:
        """
        强制停止应用
        
        Args:
            package: 应用包名
            
        Returns:
            是否成功
        """
        try:
            result = self.run(["shell", "am", "force-stop", package])
            return result.returncode == 0
        except Exception as e:
            print(f"  ❌ 停止应用失败: {e}")
            return False
    
    def get_current_focus(self) -> str:
        """
        获取当前焦点窗口
        
        Returns:
            当前焦点信息
        """
        try:
            result = self.run(["shell", "dumpsys", "window", "|", "grep", "mCurrentFocus"])
            return result.stdout
        except Exception as e:
            print(f"  ❌ 获取焦点失败: {e}")
            return ""
    
    def get_current_package(self) -> str:
        """
        获取当前前台应用包名
        
        Returns:
            当前应用包名，失败返回空字符串
        """
        try:
            # 方法1: 使用 dumpsys window（更可靠）
            result = self.run(["shell", "dumpsys", "window", "windows", "|", "grep", "-E", "mCurrentFocus"])
            if result.returncode == 0 and result.stdout:
                # 解析格式: mCurrentFocus=Window{... u0 com.example.app/com.example.Activity}
                import re
                match = re.search(r'\s+(\S+)/(\S+)\}', result.stdout)
                if match:
                    return match.group(1)
            
            # 方法2: 使用 dumpsys activity（备用）
            result = self.run(["shell", "dumpsys", "activity", "activities", "|", "grep", "mResumedActivity"])
            if result.returncode == 0 and result.stdout:
                # 解析格式: mResumedActivity: ActivityRecord{... u0 com.example.app/.MainActivity t123}
                import re
                match = re.search(r'\s+(\S+)/', result.stdout)
                if match:
                    return match.group(1)
            
            return ""
        except Exception as e:
            print(f"  ❌ 获取当前包名失败: {e}")
            return ""
