#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 客户端 - 负责与智谱 AutoGLM-Phone API 交互
"""

import os
import base64
from pathlib import Path
from typing import Dict, Optional

try:
    from zhipuai import ZhipuAI
except ImportError:
    # Only show warning when actually needed, not on module import
    # The warning will be shown when AIClient is initialized with enable_analysis=True
    ZhipuAI = None

# 尝试导入配置加载器
get_config = None
try:
    from core.config.simple_loader import get_config
except ImportError:
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent / "auto-test"))
        from core.config.simple_loader import get_config
    except ImportError:
        pass


class AIClient:
    """智谱 AutoGLM-Phone AI 客户端"""
    
    def __init__(self, api_key: str = None, enable_analysis: bool = False, model: str = None):
        """
        初始化 AI 客户端
        
        Args:
            api_key: 智谱 API Key。如果不传，将尝试从 ZHIPU_API_KEY 环境变量获取
            enable_analysis: 是否启用AI分析
            model: 模型名称（如 "glm-4-flash", "autoglm-phone"），默认 "glm-4.6v"
        """
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY")
        self.enable_analysis = enable_analysis
        self.client = None
        self.model = model or "glm-4.6v"
        
        if enable_analysis:
            if not self.api_key:
                raise ValueError(
                    "请设置 ZHIPU_API_KEY 环境变量或传入 api_key 参数\n"
                    "获取 API Key: https://open.bigmodel.cn/"
                )
            
            if ZhipuAI is None:
                # Show warning only when actually trying to use AI
                print("⚠️  未安装 zhipuai，请运行: pip install zhipuai")
                raise ImportError("请先安装 zhipuai: pip install zhipuai")
            
            self.client = ZhipuAI(api_key=self.api_key)
            print(f"✅ AI 客户端初始化完成 (模型: {self.model})")
        else:
            print(f"✅ AI 客户端初始化完成（AI分析已关闭）")
    
    def _encode_image(self, image_path: Path, max_size: int = 1024) -> str:
        """
        压缩并编码图片为 base64
        
        Args:
            image_path: 图片路径
            max_size: 最大边长（像素），默认1024
            
        Returns:
            base64 编码字符串
        """
        try:
            from PIL import Image
            import io
            
            # 打开图片
            img = Image.open(image_path)
            original_size = img.size
            
            # 计算压缩比例
            width, height = img.size
            if width > max_size or height > max_size:
                # 保持宽高比，压缩到最大边长
                if width > height:
                    new_width = max_size
                    new_height = int(height * max_size / width)
                else:
                    new_height = max_size
                    new_width = int(width * max_size / height)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"  🗜️ 图片压缩: {original_size} → {img.size}")
            
            # 转换为 RGB 模式（如果是 RGBA）
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # 保存为 JPEG 格式（质量85，平衡质量和大小）
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)
            
            # 编码为 base64
            image_bytes = buffer.getvalue()
            original_kb = Path(image_path).stat().st_size / 1024
            compressed_kb = len(image_bytes) / 1024
            print(f"  📦 文件大小: {original_kb:.1f}KB → {compressed_kb:.1f}KB ({compressed_kb/original_kb*100:.1f}%)")
            
            return base64.b64encode(image_bytes).decode('utf-8')
            
        except ImportError:
            # 如果没有 Pillow，使用原始方法
            print("  ⚠️  未安装 Pillow，跳过压缩（安装: pip install Pillow）")
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            # 压缩失败，使用原始文件
            print(f"  ⚠️  图片压缩失败: {e}，使用原始文件")
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')
    
    def analyze_screen(self, screenshot_path: Path, task: str = None, response_format: str = None) -> Dict:
        """
        使用智谱 AutoGLM-Phone 分析屏幕
        
        Args:
            screenshot_path: 截图路径
            task: 分析任务，如果为None则进行通用分析
            response_format: 响应格式，可选 "json_object" 或 None（默认文本）
            
        Returns:
            分析结果
        """
        # 检查是否启用AI分析
        if not self.enable_analysis:
            return {
                'success': False,
                'error': 'AI分析功能已关闭',
                'screenshot': str(screenshot_path)
            }
        
        if not self.client:
            return {
                'success': False,
                'error': 'AI客户端未初始化',
                'screenshot': str(screenshot_path)
            }
        
        try:
            # 编码图片
            image_base64 = self._encode_image(screenshot_path)
            
            # 默认任务：分析界面元素
            if task is None:
                task = (
                    "请分析这个手机应用界面，列出所有可见的UI元素，"
                    "包括按钮、文本、输入框等，并说明它们的功能。"
                )
            
            # 调用智谱 AI API（支持 glm-4.6v 和 autoglm-phone 模型）
            # glm-4.6v 使用 data URI 格式传递图片，autoglm-phone 直接传base64字符串
            image_url = image_base64
            if self.model == "glm-4.6v":
                # glm-4.6v 需要 data URI 格式
                image_url = f"data:image/png;base64,{image_base64}"
            
            api_params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            },
                            {
                                "type": "text",
                                "text": task
                            }
                        ]
                    }
                ],
            }
            
            # 根据模型类型设置不同的参数
            if self.model == "glm-4.6v":
                # glm-4.6v 模型参数（参考 screenshot_feature_analyzer.py 的成功实现）
                api_params["temperature"] = 0.2  # 更低的温度以获得更一致和详细的结果
                api_params["max_tokens"] = 4096   # 增加最大token数以允许更详细的输出
                # glm-4.6v 不需要 stop 参数
            else:
                # autoglm-phone 等其他模型的参数
                api_params["stop"] = ["[finish]"]  # autoglm-phone 的终止标记
                api_params["temperature"] = 0.3    # 降低随机性，避免发散
                api_params["max_tokens"] = 2048    # 最大生成长度，防止无限生成
                # 注意：智谱API不支持 repetition_penalty，靠 stop+temperature 控制
            
            # glm-4.6v 和 autoglm-phone 模型都支持 response_format 参数
            if response_format == "json_object":
                api_params["response_format"] = {"type": "json_object"}
                print(f"  📄 使用JSON格式（模型: {self.model}）")
            
            # 添加速率限制重试逻辑
            max_retries = 3
            retry_delay = 10  # 秒
            
            for attempt in range(max_retries):
                try:
                    response = self.client.chat.completions.create(**api_params)
                    break  # 成功则跳出循环
                    
                except Exception as e:
                    error_str = str(e)
                    # 检查是否是速率限制错误（429）
                    if "429" in error_str or "1305" in error_str or "请求过多" in error_str:
                        if attempt < max_retries - 1:
                            wait_time = retry_delay * (attempt + 1)  # 递增等待时间
                            print(f"  ⚠️  API速率限制，等待{wait_time}秒后重试（{attempt + 1}/{max_retries}）...")
                            import time
                            time.sleep(wait_time)
                        else:
                            print(f"  ❌ 达到最大重试次数，仍然失败")
                            raise
                    else:
                        # 其他错误直接抛出
                        raise
            
            # 提取分析结果
            analysis = response.choices[0].message.content
            
            return {
                'success': True,
                'analysis': analysis,
                'model': self.model,
                'screenshot': str(screenshot_path)
            }
            
        except Exception as e:
            import traceback
            error_detail = str(e) if str(e) else type(e).__name__
            print(f"❌ AI分析失败: {error_detail}")
            print(f"🔍 错误详情:")
            traceback.print_exc()
            
            return {
                'success': False,
                'error': error_detail,
                'error_type': type(e).__name__,
                'error_traceback': traceback.format_exc(),
                'screenshot': str(screenshot_path)
            }
