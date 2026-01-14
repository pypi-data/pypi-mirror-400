#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI交互公共方法模块

提供通用的UI元素查找和点击功能
"""

import time
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import tempfile
import re


class UIInteraction:
    """UI交互工具类"""
    
    @staticmethod
    def check_adb_connection() -> bool:
        """检查ADB连接状态
        
        使用ADBController进行设备检查
        
        返回:
            bool - 设备是否已连接
        """
        try:
            from .adb_controller import ADBController
            # 尝试初始化ADBController，如果成功则设备已连接
            adb = ADBController()
            return True
        except Exception as e:
            print(f"  ⚠️  设备未连接: {e}")
            return False
    
    @staticmethod
    def click_element_by_text(target_text: str, timeout: int = 5, retry: int = 3) -> bool:
        """通过文本内容点击元素
        
        使用递归查找可点击父容器，解决文本分散问题
        
        参数:
            target_text: 目标文本内容
            timeout: 超时时间（秒）
            retry: 重试次数
        
        返回:
            bool - 是否点击成功
        """
        # 第一次尝试前检查设备连接
        if not UIInteraction.check_adb_connection():
            print(f"  ❌ 设备未连接，无法执行点击")
            return False
        
        for attempt in range(retry):
            try:
                if attempt > 0:
                    print(f"  🔄 第 {attempt + 1} 次尝试...")
                    time.sleep(1)  # 重试前等待
                
                # 获取UI dump
                temp_xml = Path(tempfile.gettempdir()) / f"ui_click_{int(time.time())}_{attempt}.xml"
                
                # 使用公共方法获取UI dump（重试时启用详细输出）
                verbose = (attempt > 0)  # 第二次尝试开始启用详细输出
                if not UIInteraction.get_ui_dump(temp_xml, timeout, verbose=verbose):
                    if not verbose:
                        print(f"  ⚠️  无法获取UI结构")
                    continue
                
                # 解析XML查找可点击元素
                tree = ET.parse(temp_xml)
                root = tree.getroot()
                
                # 查找包含目标文本的可点击元素
                clickable_element = UIInteraction._find_clickable_element_with_text(root, target_text)
                
                if clickable_element is not None:
                    # 获取元素坐标并点击
                    result = UIInteraction._click_element(clickable_element)
                    temp_xml.unlink(missing_ok=True)
                    return result
                else:
                    print(f"  ⚠️  未找到可点击元素: {target_text}")
                
                temp_xml.unlink(missing_ok=True)
                
            except ET.ParseError as e:
                print(f"  ⚠️  XML解析失败: {e}")
                continue
            except subprocess.TimeoutExpired:
                print(f"  ⚠️  命令执行超时")
                continue
            except Exception as e:
                print(f"  ⚠️  点击失败: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"  ❌ 经过 {retry} 次尝试仍然失败")
        return False
    
    @staticmethod
    def click_element_by_coordinates(x: int, y: int) -> bool:
        """通过坐标点击元素
        
        参数:
            x: X坐标
            y: Y坐标
        
        返回:
            bool - 是否点击成功
        """
        try:
            click_cmd = f"adb shell input tap {x} {y}"
            result = subprocess.run(click_cmd, shell=True, capture_output=True, timeout=3)
            return result.returncode == 0
        except Exception as e:
            print(f"  ⚠️  坐标点击失败: {e}")
            return False
    
    @staticmethod
    def click_element_by_bounds(target_text: str, fallback_coords: tuple = None, verbose: bool = False) -> bool:
        """通过查找bounds坐标再点击（封装三步流程）
        
        封装了完整的查找坐标 + 计算中心点 + 点击流程
        
        参数:
            target_text: 目标文本
            fallback_coords: 备用固定坐标 (x, y)，当动态查找失败时使用
            verbose: 是否输出详细信息
        
        返回:
            bool - 是否点击成功
        
        示例:
            # 基本用法
            UIInteraction.click_element_by_bounds("学习")
            
            # 带fallback
            UIInteraction.click_element_by_bounds("学习", fallback_coords=(324, 2316))
            
            # 启用详细输出
            UIInteraction.click_element_by_bounds("学习", verbose=True)
        """
        # 步顤1: 获取坐标（自动处理可点击父元素）
        bounds = UIInteraction.get_element_bounds(target_text, verbose=verbose)
        
        if bounds:
            # 步顤2: 计算中心点
            x1, y1, x2, y2 = bounds
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            if verbose:
                print(f"      ✅ 动态坐标: ({center_x}, {center_y})")
        elif fallback_coords:
            # 使用fallback坐标
            center_x, center_y = fallback_coords
            if verbose:
                print(f"      🔄 使用固定坐标: ({center_x}, {center_y})")
        else:
            if verbose:
                print(f"      ❌ 无法获取坐标")
            return False
        
        # 步顤3: 直接点击（快速稳定）
        return UIInteraction.click_element_by_coordinates(center_x, center_y)
    
    @staticmethod
    def click_bottom_tab(module_name: str) -> bool:
        """点击底部导航栏tab
        
        专门用于底部导航栏的快捷方法
        
        参数:
            module_name: 模块名称（如：背词、学习、AI、阅读、我的）
        
        返回:
            bool - 是否点击成功
        """
        return UIInteraction.click_element_by_text(module_name)
    
    @staticmethod
    def _find_clickable_element_with_text(element, target_text: str):
        """递归查找包含指定文本的可点击元素
        
        策略：
        1. 递归搜索子元素（深度优先）
        2. 检查当前元素是否可点击且包含目标文本
        3. 优先返回最内层的可点击元素
        
        参数:
            element: XML元素节点
            target_text: 目标文本
        
        返回:
            找到的元素或None
        """
        # 检查当前元素是否包含目标文本
        text = element.get('text', '')
        content_desc = element.get('content-desc', '')
        
        has_target_text = target_text in text or target_text in content_desc
        
        # 递归搜索子元素（优先搜索子元素）
        for child in element:
            result = UIInteraction._find_clickable_element_with_text(child, target_text)
            if result is not None:
                return result
        
        # 如果当前元素可点击且包含目标文本，返回它
        if has_target_text and element.get('clickable') == 'true':
            return element
        
        return None
    
    @staticmethod
    def _click_element(element) -> bool:
        """点击XML元素
        
        参数:
            element: XML元素节点
        
        返回:
            bool - 是否点击成功
        """
        try:
            bounds = element.get('bounds')
            if not bounds:
                return False
            
            # 解析bounds: [x1,y1][x2,y2]
            coords = re.findall(r'\d+', bounds)
            if len(coords) != 4:
                return False
            
            x1, y1, x2, y2 = map(int, coords)
            # 计算中心点
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            print(f"  🎯 点击坐标: ({center_x}, {center_y})")
            
            # 执行点击
            return UIInteraction.click_element_by_coordinates(center_x, center_y)
            
        except Exception as e:
            print(f"  ⚠️  元素点击失败: {e}")
            return False
    
    @staticmethod
    def get_element_bounds(target_text: str, verbose: bool = False) -> Optional[Tuple[int, int, int, int]]:
        """获取元素的边界坐标
        
        参数:
            target_text: 目标文本
            verbose: 是否输出详细信息
        
        返回:
            (x1, y1, x2, y2) 或 None
        """
        try:
            temp_xml = Path(tempfile.gettempdir()) / f"ui_bounds_{int(time.time())}.xml"
            
            # 使用公共方法获取UI dump
            if not UIInteraction.get_ui_dump(temp_xml, verbose=verbose):
                if verbose:
                    print(f"      ⚠️  无法获取UI结构")
                return None
            
            tree = ET.parse(temp_xml)
            root = tree.getroot()
            
            element = UIInteraction._find_clickable_element_with_text(root, target_text)
            
            if element is not None:
                bounds = element.get('bounds')
                if bounds:
                    coords = re.findall(r'\d+', bounds)
                    if len(coords) == 4:
                        temp_xml.unlink(missing_ok=True)
                        return tuple(map(int, coords))
                    elif verbose:
                        print(f"      ⚠️  bounds格式错误: {bounds}")
                elif verbose:
                    print(f"      ⚠️  元素没有bounds属性")
            elif verbose:
                print(f"      ⚠️  未找到包含 '{target_text}' 的可点击元素")
            
            temp_xml.unlink(missing_ok=True)
            return None
            
        except ET.ParseError as e:
            if verbose:
                print(f"      ⚠️  XML解析失败: {e}")
            return None
        except Exception as e:
            if verbose:
                print(f"      ⚠️  获取边界失败: {e}")
            return None
    
    @staticmethod
    def get_ui_dump(output_path: Path, timeout: int = 5, verbose: bool = False) -> bool:
        """获取UI dump到指定文件
        
        公共方法，避免重复代码
        
        参数:
            output_path: 输出文件路径
            timeout: 超时时间（秒）
            verbose: 是否输出详细错误信息
        
        返回:
            bool - 是否成功
        """
        try:
            # 检查设备状态
            screen_state = subprocess.run(
                "adb shell dumpsys power | grep 'mHoldingDisplay'",
                shell=True, capture_output=True, timeout=3, text=True
            )
            if verbose and "false" in screen_state.stdout.lower():
                print(f"  💡 提示：设备屏幕可能处于锁屏状态")
            
            # 尝试唤醒屏幕
            subprocess.run("adb shell input keyevent KEYCODE_WAKEUP", shell=True, capture_output=True, timeout=2)
            time.sleep(0.3)
            
            dump_cmd = "adb shell uiautomator dump /sdcard/ui_dump.xml"
            pull_cmd = f"adb pull /sdcard/ui_dump.xml {output_path}"
            
            # 执行dump命令
            dump_result = subprocess.run(dump_cmd, shell=True, capture_output=True, timeout=timeout, text=True)
            if dump_result.returncode != 0:
                if verbose:
                    stderr = dump_result.stderr.strip() if dump_result.stderr else "Unknown error"
                    print(f"  ⚠️  dump失败: {stderr}")
                    
                    # 尝试重启uiautomator服务
                    if "killed" in stderr.lower() or "error" in stderr.lower():
                        print(f"  🔄 尝试重启uiautomator服务...")
                        subprocess.run("adb shell pkill uiautomator", shell=True, capture_output=True, timeout=2)
                        time.sleep(1)
                        # 再次尝试
                        dump_result = subprocess.run(dump_cmd, shell=True, capture_output=True, timeout=timeout, text=True)
                        if dump_result.returncode != 0:
                            return False
                else:
                    return False
            
            # 等待dump完成
            time.sleep(0.5)
            
            # 拉取文件
            pull_result = subprocess.run(pull_cmd, shell=True, capture_output=True, timeout=timeout, text=True)
            if pull_result.returncode != 0:
                if verbose:
                    stderr = pull_result.stderr.strip() if pull_result.stderr else "Unknown error"
                    print(f"  ⚠️  pull失败: {stderr}")
                return False
            
            # 检查文件
            if not output_path.exists():
                if verbose:
                    print(f"  ⚠️  文件不存在: {output_path}")
                return False
            
            file_size = output_path.stat().st_size
            if file_size == 0:
                if verbose:
                    print(f"  ⚠️  文件为空")
                output_path.unlink(missing_ok=True)
                return False
            
            return True
            
        except subprocess.TimeoutExpired:
            if verbose:
                print(f"  ⚠️  命令执行超时")
            return False
        except Exception as e:
            if verbose:
                print(f"  ⚠️  异常: {e}")
            return False
    
    @staticmethod
    def wait_for_page_load(timeout: int = 10, stable_count: int = 2) -> bool:
        """等待页面加载完成
        
        检查策略：
        1. 等待基本时间（3秒）
        2. 检查UI层级结构是否稳定（连续2次相同）
        3. 超时保护
        
        参数:
            timeout: 超时时间（秒）
            stable_count: 稳定次数（连续几次相同）
        
        返回:
            bool - 是否加载完成
        """
        try:
            import hashlib
            
            # 第一阶段：基本等待
            time.sleep(3)
            
            # 第二阶段：检查UI稳定性
            start_time = time.time()
            previous_hash = None
            current_stable_count = 0
            
            while (time.time() - start_time) < timeout:
                # 获取UI dump
                temp_xml = Path(tempfile.gettempdir()) / f"ui_load_check_{int(time.time())}.xml"
                
                if UIInteraction.get_ui_dump(temp_xml, timeout=3):
                    # 计算UI结构hash
                    with open(temp_xml, 'rb') as f:
                        current_hash = hashlib.md5(f.read()).hexdigest()
                    
                    # 检查是否稳定
                    if current_hash == previous_hash:
                        current_stable_count += 1
                        if current_stable_count >= stable_count:
                            temp_xml.unlink(missing_ok=True)
                            return True
                    else:
                        current_stable_count = 0
                    
                    previous_hash = current_hash
                    temp_xml.unlink(missing_ok=True)
                
                time.sleep(1)
            
            # 超时，但也认为可以继续
            return True
            
        except Exception:
            # 异常情况也返回True，继续执行
            return True
    
    @staticmethod
    def take_scroll_screenshots(
        screenshot_dir: Path,
        module_id: str,
        page_name: str = "home",
        max_scrolls: int = 5,
        detect_list_page: bool = True,
        device_id: str = None,
        reverse_scroll: bool = False  # 新增：适配不同手机的滚动方向
    ) -> List[Path]:
        """
        通用滚动截图方法（捕获完整页面内容）
        
        这是一个完全独立的通用方法，可以在任何场景下使用。
        
        特性：
        1. 智能检测列表页，列表页只滚动一次
        2. 通过UI指纹检测是否达到底部
        3. 自动滚动回顶部
        4. 返回所有截图路径
        
        参数:
            screenshot_dir: 截图保存目录
            module_id: 模块ID（用于截图命名）
            page_name: 页面名称（默认"home"）
            max_scrolls: 最大滚动次数（默认5次）
            detect_list_page: 是否检测列表页（默认True）
            device_id: 设备ID（可选）
            reverse_scroll: 是否反向滚动（默认False）
                - False: 标准滚动，手指从下往上滑 (y1=80% → y2=20%)
                - True: 反向滚动，手指从上往下滑 (y1=20% → y2=80%)
        
        返回:
            List[Path] - 截图文件路径列表
        
        示例:
            # 基本用法
            screenshots = UIInteraction.take_scroll_screenshots(
                screenshot_dir=Path("screenshots"),
                module_id="recite",
                page_name="home"
            )
            
            # 完整参数
            screenshots = UIInteraction.take_scroll_screenshots(
                screenshot_dir=Path("laite_en/screenshots"),
                module_id="recite",
                page_name="home",
                max_scrolls=5,
                detect_list_page=True,
                device_id="PQY0221126044037",
                reverse_scroll=False  # 如果滚动方向不对，设为True
            )
        """
        try:
            from .adb_controller import ADBController
            from .ui_analyzer import UIAnalyzer
            from .exploration_strategy import ExplorationStrategy
            import tempfile
            
            print(f"    📸 开始滚动截图（捕获完整页面内容）...")
            
            # 创建截图目录
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            # 初始化必要的组件
            adb = ADBController(device_id=device_id)
            ui_analyzer = UIAnalyzer()
            strategy = ExplorationStrategy()
            
            screenshot_paths = []
            scroll_count = 0
            
            # 获取屏幕尺寸
            screen_width, screen_height = adb.get_screen_size()
            print(f"       屏幕尺寸: {screen_width}x{screen_height}")
            
            # 用于检测是否达到底部的UI指纹
            seen_fingerprints = set()
            is_list_page = False
            
            while scroll_count <= max_scrolls:
                # 截取当前屏幕
                timestamp = int(time.time() * 1000)  # 毫秒级时间戳
                if scroll_count == 0:
                    screenshot_name = f"{module_id}_{page_name}.png"
                else:
                    screenshot_name = f"{module_id}_{page_name}_scroll{scroll_count}_{timestamp}.png"
                
                screenshot_path = screenshot_dir / screenshot_name
                
                if adb.screenshot(screenshot_path):
                    screenshot_paths.append(screenshot_path)
                    print(f"       ✓ 第{scroll_count + 1}张截图: {screenshot_path.name}")
                else:
                    print(f"       ⚠️  截图失败")
                
                # 检查是否达到底部（通过UI指纹判断）
                if scroll_count < max_scrolls:
                    # 获取当前UI状态
                    xml_path = Path(tempfile.gettempdir()) / f"ui_dump_scroll_{timestamp}.xml"
                    if adb.get_ui_xml(xml_path):
                        current_elements = ui_analyzer.parse_xml(xml_path)
                        
                        # 检测是否为列表页（第一次滚动时检测）
                        if detect_list_page and scroll_count == 0:
                            is_list_page = UIInteraction._is_list_page_standalone(
                                current_elements,
                                ui_analyzer,
                                strategy.min_list_items
                            )
                            if is_list_page:
                                print(f"       📋 检测到列表页（相同元素重复），只滚动一次")
                        
                        # 生成页面指纹
                        fingerprint = ui_analyzer.generate_page_fingerprint(current_elements)
                        
                        if fingerprint in seen_fingerprints:
                            print(f"       ✅ 已达到页面底部（UI未变化）")
                            xml_path.unlink(missing_ok=True)
                            break
                        
                        seen_fingerprints.add(fingerprint)
                        xml_path.unlink(missing_ok=True)
                    
                    # 向下滚动（根据reverse_scroll参数选择方向）
                    x = int(screen_width * 0.5)
                    
                    if reverse_scroll:
                        # 反向滚动：手指从上往下滑
                        y1 = int(screen_height * 0.2)  # 起点：屏幕20%处（上方）
                        y2 = int(screen_height * 0.8)  # 终点：屏幕80%处（下方）
                        direction_note = "反向"
                    else:
                        # 标准滚动：手指从下往上滑
                        y1 = int(screen_height * 0.8)  # 起点：屏幕80%处（下方）
                        y2 = int(screen_height * 0.2)  # 终点：屏幕20%处（上方）
                        direction_note = "标准"
                    
                    success = adb.swipe(x, y1, x, y2, 300)
                    if success:
                        print(f"       ⇩ 向下滚动[{direction_note}]：手指 ({x},{y1}) → ({x},{y2})")
                    else:
                        print(f"       ⚠️  滚动失败")
                    
                    time.sleep(1)  # 等待滚动完成
                    scroll_count += 1
                    
                    # 如果是列表页，只滚动一次后停止
                    if is_list_page and scroll_count >= 1:
                        print(f"       ✅ 列表页已滚动一次，停止滚动")
                        break
                else:
                    break
            
            # 滚动回顶部
            print(f"    ↶️  滚动回顶部...")
            for i in range(3):
                x = int(screen_width * 0.5)
                y1 = int(screen_height * 0.2)
                y2 = int(screen_height * 0.8)
                adb.swipe(x, y1, x, y2, 200)
                time.sleep(0.5)
                print(f"       ⇧ 向上滚动 {i+1}/3")
            
            print(f"    ✅ 滚动截图完成: 共 {len(screenshot_paths)} 张")
            return screenshot_paths
            
        except Exception as e:
            print(f"    ⚠️  滚动截图失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def _is_list_page_standalone(
        elements: List[Dict],
        ui_analyzer,
        min_list_items: int = 3
    ) -> bool:
        """
        独立的列表页检测方法（不依赖ExplorationStrategy实例）
        
        参数:
            elements: UI元素列表
            ui_analyzer: UIAnalyzer实例
            min_list_items: 最小列表项数量（默认3）
            
        返回:
            True 如果是列表页，False 否则
        """
        if not elements or len(elements) < 3:
            return False
        
        # 使用与 filter_list_items 相同的逻辑检测列表
        grouped = {}
        
        for elem in elements:
            text = elem.get('text', '')
            resource_id = elem.get('resource_id', '')
            
            if not resource_id:
                continue
            
            # 检测文本模式
            pattern = ui_analyzer.extract_text_pattern(text)
            group_key = (resource_id, pattern)
            
            if group_key not in grouped:
                grouped[group_key] = 0
            grouped[group_key] += 1
        
        # 如果存在任何分组有 >= min_list_items 个相同元素，认为是列表页
        for count in grouped.values():
            if count >= min_list_items:
                return True
        
        return False
