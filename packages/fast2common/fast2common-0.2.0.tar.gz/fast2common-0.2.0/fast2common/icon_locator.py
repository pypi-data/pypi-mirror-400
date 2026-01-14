#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图标定位器 - 使用AI视觉模型识别图标并返回坐标
"""

import json
import re
import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

# Setup logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class IconLocator:
    """图标定位器 - 使用AI视觉模型识别图标位置"""
    
    def __init__(self, api_key: str = None):
        """
        初始化图标定位器
        
        Args:
            api_key: 智谱 API Key，如果为None则从环境变量获取
        """
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY")
        if not self.api_key:
            raise ValueError("请设置 ZHIPU_API_KEY 环境变量或传入 api_key 参数")
        
        # 导入 AI 客户端
        try:
            from .ai_client import AIClient
            self.ai_client = AIClient(api_key=self.api_key, enable_analysis=True)
        except ImportError as e:
            logger.error(f"Failed to import AIClient: {e}")
            raise
    
    def find_icon_center(
        self,
        icon_description: str,
        position_description: Optional[str] = None,
        device_id: str = None,
        screenshot_path: Optional[Path] = None
    ) -> Optional[Tuple[int, int]]:
        """
        查找图标中心坐标
        
        Args:
            icon_description: 图标描述（如"齿轮"、"返回"、"设置"）
            position_description: 位置描述（如"底部"、"右上角"），可选
            device_id: 设备ID，如果提供了screenshot_path则不需要
            screenshot_path: 截图路径，如果为None则自动截图
        
        Returns:
            图标中心坐标 (x, y)，如果未找到则返回None
        """
        try:
            # 获取截图
            if screenshot_path is None:
                if not device_id:
                    raise ValueError("device_id is required when screenshot_path is not provided")
                
                screenshot_path = self._capture_screenshot(device_id)
                if not screenshot_path:
                    logger.error("Failed to capture screenshot")
                    return None
            else:
                if not screenshot_path.exists():
                    logger.error(f"Screenshot file not found: {screenshot_path}")
                    return None
            
            # 构建AI提示词
            prompt = self._build_prompt(icon_description, position_description)
            
            # 调用AI分析
            logger.info(f"🔍 Using AI to locate icon: {icon_description}" + (f" at {position_description}" if position_description else ""))
            analysis_result = self.ai_client.analyze_screen(
                screenshot_path,
                task=prompt,
                response_format="json_object"  # Request JSON format
            )
            
            if not analysis_result.get('success'):
                error = analysis_result.get('error', 'Unknown error')
                logger.error(f"❌ AI analysis failed: {error}")
                return None
            
            # 解析AI返回的JSON
            analysis_text = analysis_result.get('analysis', '')
            if not analysis_text:
                logger.error("❌ AI returned empty analysis")
                return None
            
            # 解析JSON响应
            coords = self._parse_ai_response(analysis_text)
            
            # 清理临时截图（如果是自动截图的）
            if screenshot_path and device_id:  # Only clean up if we created it
                try:
                    if screenshot_path.parent.name == "temp" or "/tmp" in str(screenshot_path):
                        screenshot_path.unlink()
                except:
                    pass
            
            return coords
            
        except Exception as e:
            logger.error(f"❌ Icon location failed: {e}", exc_info=True)
            return None
    
    def _capture_screenshot(self, device_id: str) -> Optional[Path]:
        """
        捕获设备截图
        
        Args:
            device_id: 设备ID
        
        Returns:
            截图文件路径
        """
        try:
            from .adb_controller import ADBController
            
            adb = ADBController(device_id=device_id)
            
            # 创建临时目录
            temp_dir = Path("/tmp") if Path("/tmp").exists() else Path.cwd() / "temp"
            temp_dir.mkdir(exist_ok=True)
            
            screenshot_path = temp_dir / f"icon_locate_{device_id}_{int(time.time())}.png"
            
            if adb.screenshot(screenshot_path):
                logger.debug(f"Screenshot saved: {screenshot_path}")
                return screenshot_path
            else:
                logger.error("Failed to capture screenshot")
                return None
                
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    def _build_prompt(self, icon_description: str, position_description: Optional[str] = None) -> str:
        """
        构建AI提示词
        
        Args:
            icon_description: 图标描述
            position_description: 位置描述
        
        Returns:
            提示词文本
        """
        position_text = position_description if position_description else "任意位置"
        
        prompt = f"""请分析这张手机应用截图，找到指定的图标并返回其中心坐标。

图标描述：{icon_description}
位置要求：{position_text}

要求：
1. 在截图中查找匹配描述的图标（如齿轮、返回、设置等）
2. 如果提供了位置要求，优先查找符合位置要求的图标
3. 返回图标可点击区域的中心坐标（像素坐标）
4. 返回 JSON 格式：{{"center_x": x, "center_y": y, "confidence": 0.0-1.0}}
5. 如果找不到图标，返回 {{"center_x": null, "center_y": null, "error": "未找到图标"}}

请直接返回 JSON，不要添加其他文字。"""
        
        return prompt
    
    def _parse_ai_response(self, analysis_text: str) -> Optional[Tuple[int, int]]:
        """
        解析AI返回的JSON响应
        
        Args:
            analysis_text: AI返回的文本
        
        Returns:
            坐标 (x, y)，如果解析失败则返回None
        """
        try:
            # 尝试提取JSON部分（如果被包裹在代码块中）
            json_match = re.search(r'```json\s*(.*?)\s*```', analysis_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接解析
                json_str = analysis_text.strip()
            
            # 解析JSON
            data = json.loads(json_str)
            
            # 检查是否有错误
            if data.get("error"):
                logger.warning(f"AI returned error: {data.get('error')}")
                return None
            
            # 提取坐标
            center_x = data.get("center_x")
            center_y = data.get("center_y")
            
            if center_x is None or center_y is None:
                logger.warning("AI returned null coordinates")
                return None
            
            # 转换为整数
            try:
                x = int(center_x)
                y = int(center_y)
                
                confidence = data.get("confidence", 1.0)
                logger.info(f"✅ Found icon at ({x}, {y}) with confidence {confidence}")
                
                return (x, y)
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid coordinate format: {e}")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.debug(f"Response text: {analysis_text[:500]}")
            return None
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return None

