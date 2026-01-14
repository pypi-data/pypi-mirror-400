#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图布局分析工具 - 统一实现
分析已生成的截图，检测UI bug和明显不合理的地方
"""

import os
import sys
import json
import base64
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from zhipuai import ZhipuAI

# Setup logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class ScreenshotAnalyzer:
    """截图布局分析器"""
    
    def __init__(self, api_key: str = None, base_dir: Path = None):
        """
        初始化分析器
        
        Args:
            api_key: 智谱 API Key
            base_dir: 基础目录（用于截图和报告目录），如果为None则使用当前文件所在目录
        """
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY")
        if not self.api_key:
            raise ValueError("请设置 ZHIPU_API_KEY 环境变量或传入 api_key 参数")
        
        # 初始化智谱客户端
        self.client = ZhipuAI(api_key=self.api_key)
        
        # 强制使用 glm-4.6v 模型进行截图分析
        # glm-4.6v 是视觉理解模型，最适合截图分析任务
        self.model = "glm-4.6v"
        
        # 目录配置
        if base_dir is None:
            # 尝试从调用者目录推断，否则使用当前文件所在目录
            import inspect
            frame = inspect.currentframe()
            try:
                caller_file = frame.f_back.f_globals.get('__file__')
                if caller_file:
                    self.base_dir = Path(caller_file).parent
                else:
                    self.base_dir = Path(__file__).parent
            finally:
                del frame
        else:
            self.base_dir = Path(base_dir)
        
        self.screenshot_dir = self.base_dir / "screenshots"
        self.report_dir = self.base_dir / "analysis_reports"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ 截图布局分析器初始化完成")
        logger.info(f"   截图目录: {self.screenshot_dir}")
        logger.info(f"   报告目录: {self.report_dir}")
    
    def _encode_image(self, image_path: Path) -> str:
        """将图片编码为 base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def _merge_images(self, image_paths: List[Path], max_images_per_row: int = 3, 
                     max_single_width: int = 400, max_single_height: int = 800,
                     max_merged_width: int = 2000, max_merged_height: int = 3000,
                     jpeg_quality: int = 85, padding: int = 20) -> Path:
        """
        将多张图片合并成一张大图（网格布局），并进行压缩优化
        
        Args:
            image_paths: 图片路径列表
            max_images_per_row: 每行最多显示几张图片（默认3张）
            max_single_width: 单张图片的最大宽度（默认400px，用于压缩）
            max_single_height: 单张图片的最大高度（默认800px，用于压缩）
            max_merged_width: 合并后图片的最大宽度（默认2000px）
            max_merged_height: 合并后图片的最大高度（默认3000px）
            jpeg_quality: JPEG压缩质量（1-100，默认85，平衡质量和大小）
            padding: 图片之间的间距（像素，默认20px，用于分隔独立页面）
        
        Returns:
            合并后的图片路径
        """
        try:
            from PIL import Image
            import io
        except ImportError:
            raise ImportError("请安装 Pillow: pip install Pillow")
        
        if not image_paths:
            raise ValueError("图片列表为空")
        
        # 读取所有图片并压缩
        images = []
        total_original_size = 0
        for img_path in image_paths:
            try:
                img = Image.open(img_path)
                total_original_size += img_path.stat().st_size
                
                # 转换为 RGB 模式（如果是 RGBA）
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                # 压缩单张图片：限制最大尺寸
                width, height = img.size
                if width > max_single_width or height > max_single_height:
                    # 保持宽高比，压缩到最大尺寸内
                    ratio = min(max_single_width / width, max_single_height / height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    logger.info(f"  🗜️  压缩单张图片: {img_path.name} {width}x{height} → {new_width}x{new_height}")
                
                images.append((img, img_path.name))
            except Exception as e:
                logger.warning(f"无法读取图片 {img_path}: {e}")
                continue
        
        if not images:
            raise ValueError("没有有效的图片可以合并")
        
        # 计算网格布局
        num_images = len(images)
        num_rows = (num_images + max_images_per_row - 1) // max_images_per_row
        num_cols = min(num_images, max_images_per_row)
        
        # 获取单张图片的尺寸（使用压缩后的尺寸）
        max_width = max(img.width for img, _ in images)
        max_height = max(img.height for img, _ in images)
        
        # 统一图片尺寸（居中放置）
        resized_images = []
        for img, name in images:
            # 保持宽高比，缩放到统一尺寸
            ratio = min(max_width / img.width, max_height / img.height)
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 创建统一尺寸的画布（居中放置，白色背景）
            canvas = Image.new('RGB', (max_width, max_height), (255, 255, 255))
            x_offset = (max_width - new_width) // 2
            y_offset = (max_height - new_height) // 2
            canvas.paste(resized, (x_offset, y_offset))
            resized_images.append((canvas, name))
        
        # 计算合并后的画布尺寸（包含间距）
        # 总宽度 = 列数 × 单张宽度 + (列数 + 1) × 左右间距
        # 总高度 = 行数 × 单张高度 + (行数 + 1) × 上下间距
        merged_width = max_width * num_cols + padding * (num_cols + 1)
        merged_height = max_height * num_rows + padding * (num_rows + 1)
        
        # 如果合并后的图片太大，进一步压缩（考虑间距）
        if merged_width > max_merged_width or merged_height > max_merged_height:
            # 计算可用空间（减去间距）
            available_width = max_merged_width - padding * (num_cols + 1)
            available_height = max_merged_height - padding * (num_rows + 1)
            
            # 计算压缩比例
            ratio_width = available_width / (max_width * num_cols) if num_cols > 0 else 1
            ratio_height = available_height / (max_height * num_rows) if num_rows > 0 else 1
            ratio = min(ratio_width, ratio_height, 1.0)  # 不放大，只缩小
            
            if ratio < 1.0:
                max_width = int(max_width * ratio)
                max_height = int(max_height * ratio)
                merged_width = max_width * num_cols + padding * (num_cols + 1)
                merged_height = max_height * num_rows + padding * (num_rows + 1)
                logger.info(f"  🗜️  压缩合并尺寸: {max_width * num_cols + padding * (num_cols + 1)}x{max_height * num_rows + padding * (num_rows + 1)} → {merged_width}x{merged_height}")
                
                # 重新调整所有图片尺寸
                resized_images = []
                for img, name in images:
                    ratio_single = min(max_width / img.width, max_height / img.height)
                    new_width = int(img.width * ratio_single)
                    new_height = int(img.height * ratio_single)
                    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    canvas = Image.new('RGB', (max_width, max_height), (255, 255, 255))
                    x_offset = (max_width - new_width) // 2
                    y_offset = (max_height - new_height) // 2
                    canvas.paste(resized, (x_offset, y_offset))
                    resized_images.append((canvas, name))
        
        # 创建合并后的画布（白色背景，间距区域也是白色）
        merged_image = Image.new('RGB', (merged_width, merged_height), (255, 255, 255))
        
        # 将图片按网格排列，每张图片之间留出间距
        for idx, (img, name) in enumerate(resized_images):
            row = idx // num_cols
            col = idx % num_cols
            # 计算位置：左边距 + 列索引 × (图片宽度 + 间距) + 图片宽度
            x = padding + col * (max_width + padding)
            y = padding + row * (max_height + padding)
            merged_image.paste(img, (x, y))
        
        # 保存合并后的图片（使用JPEG格式以获得更好的压缩比）
        temp_dir = Path("/tmp") if Path("/tmp").exists() else Path.cwd() / "temp"
        temp_dir.mkdir(exist_ok=True)
        merged_path = temp_dir / f"merged_screenshots_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        # 使用JPEG格式保存（更好的压缩比）
        merged_image.save(merged_path, "JPEG", quality=jpeg_quality, optimize=True)
        
        # 记录压缩效果
        merged_size = merged_path.stat().st_size
        compression_ratio = (merged_size / total_original_size * 100) if total_original_size > 0 else 0
        logger.info(f"  📦 合并图片大小: {merged_size / 1024:.1f}KB (原始总大小: {total_original_size / 1024:.1f}KB, 压缩率: {compression_ratio:.1f}%)")
        logger.info(f"  📐 合并图片尺寸: {merged_width}x{merged_height}")
        
        return merged_path
    
    def analyze_screenshots_batch(self, screenshot_paths: List[Path], batch_size: int = 6) -> List[Dict]:
        """
        批量分析多张截图（合并后统一分析）
        
        Args:
            screenshot_paths: 截图路径列表
            batch_size: 每批合并的图片数量（默认6张，即2行3列）
        
        Returns:
            分析结果列表，每个元素对应一张截图
        """
        results = []
        
        # 分批处理
        for batch_start in range(0, len(screenshot_paths), batch_size):
            batch_paths = screenshot_paths[batch_start:batch_start + batch_size]
            batch_num = batch_start // batch_size + 1
            total_batches = (len(screenshot_paths) + batch_size - 1) // batch_size
            
            logger.info(f"📸 批量分析第 {batch_num}/{total_batches} 批 ({len(batch_paths)} 张截图)")
            
            try:
                # 合并图片
                merged_path = self._merge_images(batch_paths, max_images_per_row=3)
                logger.info(f"  ✅ 图片已合并: {merged_path.name}")
                
                # 分析合并后的图片
                merged_analysis = self.analyze_screenshot_layout(merged_path, is_merged=True, image_count=len(batch_paths))
                
                # 将分析结果分配给每张原图
                # 如果AI返回了每张图片的分析，直接使用；否则使用合并分析结果
                if isinstance(merged_analysis.get('individual_analyses'), list):
                    # AI返回了每张图片的独立分析
                    for idx, (img_path, analysis) in enumerate(zip(batch_paths, merged_analysis['individual_analyses'])):
                        analysis['screenshot'] = str(img_path)
                        analysis['filename'] = img_path.name
                        analysis['batch_number'] = batch_num
                        results.append(analysis)
                else:
                    # 使用合并分析结果（所有图片共享分析结果）
                    for img_path in batch_paths:
                        result = merged_analysis.copy()
                        result['screenshot'] = str(img_path)
                        result['filename'] = img_path.name
                        result['batch_number'] = batch_num
                        result['note'] = "此分析基于合并图片，可能与单张分析略有差异"
                        results.append(result)
                
                # 清理临时文件
                try:
                    merged_path.unlink()
                except:
                    pass
                    
            except Exception as e:
                logger.error(f"  ❌ 批量分析失败: {e}")
                # 如果批量分析失败，回退到单张分析
                logger.info(f"  🔄 回退到单张分析模式")
                for img_path in batch_paths:
                    try:
                        result = self.analyze_screenshot_layout(img_path)
                        results.append(result)
                    except Exception as e2:
                        logger.error(f"  ❌ 单张分析也失败 {img_path.name}: {e2}")
                        results.append({
                            "success": False,
                            "error": str(e2),
                            "screenshot": str(img_path),
                            "filename": img_path.name
                        })
        
        return results
    
    def analyze_screenshot_layout(self, screenshot_path: Path, is_merged: bool = False, image_count: int = 1) -> Dict:
        """
        分析单个截图的布局，检测 bug 和不合理之处
        
        Args:
            screenshot_path: 截图路径
            is_merged: 是否为合并后的图片（默认False）
            image_count: 合并图片中的图片数量（仅在is_merged=True时有效）
            
        Returns:
            分析结果
        """
        print(f"\n🔍 分析截图: {screenshot_path.name}")
        
        try:
            # 编码图片
            image_base64 = self._encode_image(screenshot_path)
            
            # 设计详细的分析任务
            if is_merged and image_count > 1:
                # 合并图片的分析提示
                task = f"""
请作为专业的UI/UX设计师和测试工程师，对这张合并图片中的 {image_count} 个移动应用界面进行全面的布局分析。

**重要提示：**
这是一张合并图片，包含 {image_count} 个独立的界面截图，按网格排列。请分别分析每个界面，并在返回结果中为每个界面提供独立的分析。

**分析要求：**
1. 按从左到右、从上到下的顺序，依次分析每个界面
2. 为每个界面提供独立的分析结果
3. 如果某个界面有问题，请明确指出是第几个界面（从1开始计数）

请作为专业的UI/UX设计师和测试工程师，对每个界面进行全面的布局分析，重点检测以下问题：
"""
            else:
                task = """
请作为专业的UI/UX设计师和测试工程师，对这个移动应用界面进行全面的布局分析，重点检测以下问题：

**1. 布局Bug检测：**
- 元素重叠或遮挡
- 文本截断或显示不完整
- 按钮或图标错位
- 间距不一致或过大/过小
- 元素超出屏幕边界
- 布局错乱或变形

**2. 视觉问题：**
- 颜色对比度不足（文字不清晰）
- 图片缺失或加载失败
- 图标或图片变形、拉伸
- 背景色与前景色冲突

**3. 交互问题：**
- 按钮或链接太小（不易点击）
- 可点击区域不明确
- 重要操作缺少视觉反馈
- 导航不清晰或缺失

**4. 内容问题：**
- 文本错误或乱码
- 空白页面或空状态
- 数据显示异常（如：负数进度、超过100%）
- 提示信息不明确或缺失

**5. 可用性问题：**
- 信息层级不清晰
- 重要功能不突出
- 操作流程不合理
- 缺少必要的引导

**请按以下JSON格式返回分析结果：**

{"is_merged": true, "image_count": image_count, "individual_analyses": [...]} 格式（合并图片）：
```json
{
  "is_merged": true,
  "image_count": {image_count},
  "individual_analyses": [
    {{
      "image_index": 1,
      "overall_score": 85,
      "overall_assessment": "整体布局良好，但存在一些小问题",
      "issues": [
        {{
          "severity": "high|medium|low",
          "category": "布局|视觉|交互|内容|可用性",
          "title": "问题标题",
          "description": "详细描述",
          "location": "问题位置（页面哪个区域）",
          "suggestion": "修复建议"
        }}
      ],
      "positive_points": [
        "优点1：布局清晰，层次分明",
        "优点2：色彩搭配协调"
      ],
      "recommendations": [
        "建议1：增加按钮点击区域",
        "建议2：优化文字大小"
      ]
    }},
    ...
  ]
}
```

单张图片格式：
```json
{{
  "overall_score": 85,
  "overall_assessment": "整体布局良好，但存在一些小问题",
  "issues": [
    {{
      "severity": "high|medium|low",
      "category": "布局|视觉|交互|内容|可用性",
      "title": "问题标题",
      "description": "详细描述",
      "location": "问题位置（页面哪个区域）",
      "suggestion": "修复建议"
    }}
  ],
  "positive_points": [
    "优点1：布局清晰，层次分明",
    "优点2：色彩搭配协调"
  ],
  "recommendations": [
    "建议1：增加按钮点击区域",
    "建议2：优化文字大小"
  ]
}}
```

如果界面完美无问题，issues 数组为空，但仍需给出评分和优点。
"""
            
            # 调用智谱 AI API (glm-4.6v)
            logger.info(f"  🤖 正在调用 AI API 进行分析 (模型: {self.model})...")
            print("  🤖 正在调用 AI 分析...")
            
            # 根据模型类型设置参数
            api_params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
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
            
            # glm-4.6v 模型参数优化
            if self.model == "glm-4.6v":
                api_params["temperature"] = 0.2  # 更低的温度以获得更一致的结果
                api_params["max_tokens"] = 4096    # 增加最大token数以允许更详细的输出
                # glm-4.6v 不需要 stop 参数
            else:
                # 其他模型的参数（如autoglm-phone）
                api_params["temperature"] = 0.7
                api_params["max_tokens"] = 3000
                api_params["stop"] = ["[finish]"]  # autoglm-phone 的终止标记
            
            logger.info(f"  📡 调用 AI API (模型: {self.model}, max_tokens: {api_params.get('max_tokens', 'N/A')})...")
            response = self.client.chat.completions.create(**api_params)
            logger.info(f"  ✅ AI API 调用成功，收到响应")
            
            # 提取分析结果
            analysis_text = response.choices[0].message.content
            logger.info(f"  📝 AI 返回分析文本长度: {len(analysis_text)} 字符")
            
            # 尝试解析 JSON
            logger.info(f"  🔍 解析 AI 返回的 JSON 数据...")
            result = self._parse_analysis_result(analysis_text)
            
            # Check if JSON parsing actually succeeded
            if isinstance(result, dict) and result.get('parse_error'):
                logger.warning(f"  ⚠️  JSON 解析失败: {result.get('parse_error')}")
                logger.warning(f"  ⚠️  AI 返回文本长度: {len(analysis_text)} 字符")
                logger.warning(f"  ⚠️  AI 返回文本前500字符: {analysis_text[:500]}")
                # Return the error result directly
                result['screenshot'] = str(screenshot_path)
                result['filename'] = screenshot_path.name
                result['timestamp'] = datetime.now().isoformat()
                result['raw_analysis'] = analysis_text
                self._print_analysis_summary(result)
                return result
            else:
                logger.info(f"  ✅ JSON 解析成功")
            
            # Debug: Log parsed result structure
            result_keys = list(result.keys()) if isinstance(result, dict) else "Not a dict"
            result_success = result.get('success') if isinstance(result, dict) else None
            logger.info(f"  🔍 Parsed result keys: {result_keys}")
            logger.info(f"  🔍 Parsed result success: {result_success}")
            
            # Check if result has required fields
            if isinstance(result, dict):
                if not result.get('success', True):
                    logger.warning(f"  ⚠️  Parsed result has success=False, error field: {result.get('error', 'NOT SET')}")
                    logger.warning(f"  ⚠️  Full result structure: {list(result.keys())}")
                else:
                    # Check for missing fields
                    if not result.get('is_merged'):
                        # Single image format - check for required fields
                        if 'overall_score' not in result:
                            logger.warning(f"  ⚠️  Missing 'overall_score' field in result. Available keys: {list(result.keys())}")
                            logger.warning(f"  ⚠️  This may indicate the AI returned an unexpected format")
                            logger.warning(f"  ⚠️  Raw analysis preview: {analysis_text[:500]}")
                        if 'overall_assessment' not in result:
                            logger.warning(f"  ⚠️  Missing 'overall_assessment' field in result. Available keys: {list(result.keys())}")
                    else:
                        # Merged image format - check individual_analyses
                        if 'individual_analyses' not in result:
                            logger.warning(f"  ⚠️  Merged image format but missing 'individual_analyses' field")
                        else:
                            logger.info(f"  📊 Merged image format: {len(result.get('individual_analyses', []))} individual analyses")
            
            result['screenshot'] = str(screenshot_path)
            result['filename'] = screenshot_path.name
            result['timestamp'] = datetime.now().isoformat()
            result['raw_analysis'] = analysis_text
            
            # 显示摘要
            self._print_analysis_summary(result)
            
            return result
            
        except Exception as e:
            import traceback
            import sys
            
            # 强制刷新输出，确保错误信息显示
            sys.stdout.flush()
            sys.stderr.flush()
            
            error_detail = str(e) if str(e) else type(e).__name__
            print(f"\n  ❌ 分析失败: {error_detail}", flush=True)
            print(f"  🔍 错误类型: {type(e).__name__}", flush=True)
            print(f"  🔍 完整错误信息:", flush=True)
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
            
            return {
                'success': False,
                'error': error_detail,
                'error_type': type(e).__name__,
                'error_traceback': traceback.format_exc(),
                'screenshot': str(screenshot_path),
                'filename': screenshot_path.name,
                'timestamp': datetime.now().isoformat()
            }
    
    def _parse_analysis_result(self, text: str) -> Dict:
        """解析 AI 返回的分析结果"""
        import re
        
        # 尝试提取 JSON 部分
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 如果没有找到 JSON，尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # 返回原始文本
            return {
                'success': False,
                'raw_text': text,
                'parse_error': 'Unable to parse JSON from AI response'
            }
    
    def _print_analysis_summary(self, result: Dict):
        """打印分析摘要"""
        if not result.get('success', True):
            error_msg = result.get('error') or result.get('parse_error') or 'Unknown error'
            print(f"  ❌ 分析失败: {error_msg}")
            # Log additional debug info
            logger.warning(f"  ⚠️  Analysis failed. Result keys: {list(result.keys())}")
            logger.warning(f"  ⚠️  Error field: {result.get('error')}, Parse error: {result.get('parse_error')}")
            return
        
        # Handle merged image format (is_merged: true)
        if result.get('is_merged') and result.get('individual_analyses'):
            # For merged images, show summary of all individual analyses
            individual_analyses = result.get('individual_analyses', [])
            total_score = 0
            total_issues = 0
            valid_analyses = 0
            
            for idx, analysis in enumerate(individual_analyses, 1):
                if isinstance(analysis, dict):
                    score = analysis.get('overall_score', 0)
                    issues = analysis.get('issues', [])
                    if score > 0:  # Only count valid scores
                        total_score += score
                        valid_analyses += 1
                    total_issues += len(issues)
            
            if valid_analyses > 0:
                avg_score = total_score / valid_analyses
                score_emoji = "🟢" if avg_score >= 90 else "🟡" if avg_score >= 70 else "🔴"
                print(f"  {score_emoji} 综合评分: {avg_score:.0f}/100 (平均，共 {valid_analyses} 张图片)")
                print(f"  ⚠️  发现 {total_issues} 个问题（共 {len(individual_analyses)} 张图片）")
            else:
                print(f"  🔴 综合评分: 0/100 (无法获取有效评分)")
                print(f"  N/A")
        else:
            # Single image format
            score = result.get('overall_score', 0)
            issues = result.get('issues', [])
            
            # Check if score is actually 0 or just missing
            if score == 0 and 'overall_score' not in result:
                # Score field is missing, not actually 0
                logger.warning(f"  ⚠️  Missing 'overall_score' field in result. Available keys: {list(result.keys())}")
                print(f"  ⚠️  综合评分: 0/100 (字段缺失)")
                print(f"  {result.get('overall_assessment', 'N/A')}")
            else:
                # Score is present (may be 0 or actual value)
                # 评分颜色
                if score >= 90:
                    score_emoji = "🟢"
                elif score >= 70:
                    score_emoji = "🟡"
                else:
                    score_emoji = "🔴"
                
                print(f"  {score_emoji} 综合评分: {score}/100")
                assessment = result.get('overall_assessment', 'N/A')
                if assessment == 'N/A' and 'overall_assessment' not in result:
                    logger.warning(f"  ⚠️  Missing 'overall_assessment' field in result. Available keys: {list(result.keys())}")
                print(f"  {assessment}")
            
            if issues:
                print(f"\n  ⚠️  发现 {len(issues)} 个问题：")
                for i, issue in enumerate(issues[:3], 1):  # 只显示前3个
                    severity_emoji = {
                        'high': '🔴',
                        'medium': '🟡',
                        'low': '🟢'
                    }.get(issue.get('severity', 'low'), '⚪')
                    
                    print(f"    {severity_emoji} [{issue.get('category', 'N/A')}] {issue.get('title', 'N/A')}")
                
                if len(issues) > 3:
                    print(f"    ... 还有 {len(issues) - 3} 个问题")
            else:
                print(f"  ✅ 未发现明显问题")
    
    def analyze_directory(self, session_id: str = None) -> List[Dict]:
        """
        分析指定会话的所有截图
        
        Args:
            session_id: 会话ID（例如：20241226_143000），如果为None则分析最新的
            
        Returns:
            所有分析结果列表
        """
        print(f"\n{'='*60}")
        print("  📸 批量截图布局分析")
        print(f"{'='*60}\n")
        
        # 查找截图文件（在独立会话目录中）
        if session_id:
            # 使用指定会话的目录
            session_screenshot_dir = self.base_dir / "output" / session_id / "screenshots"
            
            if not session_screenshot_dir.exists():
                print(f"❌ 未找到会话 {session_id} 的截图目录: {session_screenshot_dir}")
                return []
            
            screenshots = sorted(session_screenshot_dir.glob("*.png"))
        else:
            # 查找最新的会话目录
            output_dir = self.base_dir / "output"
            if not output_dir.exists():
                print("❌ 未找到 output 目录")
                return []
            
            # 获取所有会话目录，按时间排序
            session_dirs = sorted([d for d in output_dir.iterdir() if d.is_dir()])
            if not session_dirs:
                print("❌ 未找到任何会话目录")
                return []
            
            # 使用最新的会话
            latest_session_dir = session_dirs[-1]
            session_id = latest_session_dir.name
            session_screenshot_dir = latest_session_dir / "screenshots"
            
            if not session_screenshot_dir.exists():
                print(f"❌ 最新会话 {session_id} 没有截图目录")
                return []
            
            screenshots = sorted(session_screenshot_dir.glob("*.png"))
        
        if not screenshots:
            print(f"❌ 未找到会话 {session_id} 的截图")
            return []
        
        print(f"📁 找到 {len(screenshots)} 个截图文件")
        print(f"📅 会话ID: {session_id}")
        print(f"📂 目录: {session_screenshot_dir}\n")
        
        # 分析所有截图
        results = []
        for i, screenshot in enumerate(screenshots, 1):
            print(f"[{i}/{len(screenshots)}]", end=" ")
            result = self.analyze_screenshot_layout(screenshot)
            results.append(result)
        
        # 生成汇总报告
        self._generate_summary_report(results, session_id)
        
        return results
    
    def _generate_summary_report(self, results: List[Dict], session_id: str):
        """生成汇总报告"""
        print(f"\n{'='*60}")
        print("  📊 分析汇总报告")
        print(f"{'='*60}\n")
        
        # 统计
        total = len(results)
        successful = sum(1 for r in results if r.get('success', True))
        
        # 收集所有问题
        all_issues = []
        scores = []
        
        for result in results:
            if result.get('overall_score'):
                scores.append(result['overall_score'])
            
            for issue in result.get('issues', []):
                all_issues.append({
                    **issue,
                    'screenshot': result.get('filename', 'Unknown')
                })
        
        # 按严重程度分类
        high_issues = [i for i in all_issues if i.get('severity') == 'high']
        medium_issues = [i for i in all_issues if i.get('severity') == 'medium']
        low_issues = [i for i in all_issues if i.get('severity') == 'low']
        
        print(f"📈 总体统计：")
        print(f"  - 分析截图数: {total}")
        print(f"  - 成功分析: {successful}")
        print(f"  - 平均评分: {sum(scores)/len(scores):.1f}/100" if scores else "  - 平均评分: N/A")
        print(f"  - 发现问题总数: {len(all_issues)}")
        print(f"    🔴 严重: {len(high_issues)}")
        print(f"    🟡 中等: {len(medium_issues)}")
        print(f"    🟢 轻微: {len(low_issues)}")
        
        # 显示严重问题
        if high_issues:
            print(f"\n🔴 严重问题列表：")
            for i, issue in enumerate(high_issues[:10], 1):
                print(f"  {i}. [{issue.get('category', 'N/A')}] {issue.get('title', 'N/A')}")
                print(f"     位置: {issue.get('location', 'N/A')}")
                print(f"     截图: {issue.get('screenshot', 'N/A')}")
                print()
        
        # 保存详细报告
        report_file = self.report_dir / f"analysis_report_{session_id}.json"
        report_data = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_screenshots': total,
                'successful_analysis': successful,
                'average_score': sum(scores)/len(scores) if scores else 0,
                'total_issues': len(all_issues),
                'high_severity': len(high_issues),
                'medium_severity': len(medium_issues),
                'low_severity': len(low_issues)
            },
            'high_priority_issues': high_issues[:20],  # 前20个严重问题
            'all_results': results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 详细报告已保存: {report_file.name}")
        
        # 生成 Markdown 报告
        md_file = self._generate_markdown_report(report_data, session_id)
        print(f"📄 Markdown 报告: {md_file.name}")
        
        print(f"\n{'='*60}")
    
    def _generate_markdown_report(self, report_data: Dict, session_id: str) -> Path:
        """生成 Markdown 格式的报告"""
        md_file = self.report_dir / f"analysis_report_{session_id}.md"
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# 截图布局分析报告\n\n")
            f.write(f"**会话ID**: {session_id}\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 汇总统计
            summary = report_data['summary']
            f.write(f"## 📊 汇总统计\n\n")
            f.write(f"| 指标 | 数值 |\n")
            f.write(f"|------|------|\n")
            f.write(f"| 分析截图数 | {summary['total_screenshots']} |\n")
            f.write(f"| 成功分析 | {summary['successful_analysis']} |\n")
            f.write(f"| 平均评分 | {summary['average_score']:.1f}/100 |\n")
            f.write(f"| 发现问题总数 | {summary['total_issues']} |\n")
            f.write(f"| 🔴 严重问题 | {summary['high_severity']} |\n")
            f.write(f"| 🟡 中等问题 | {summary['medium_severity']} |\n")
            f.write(f"| 🟢 轻微问题 | {summary['low_severity']} |\n")
            f.write(f"\n")
            
            # 严重问题详情
            high_issues = report_data['high_priority_issues']
            if high_issues:
                f.write(f"## 🔴 严重问题详情\n\n")
                for i, issue in enumerate(high_issues, 1):
                    f.write(f"### {i}. {issue.get('title', 'N/A')}\n\n")
                    f.write(f"- **类别**: {issue.get('category', 'N/A')}\n")
                    f.write(f"- **位置**: {issue.get('location', 'N/A')}\n")
                    f.write(f"- **截图**: {issue.get('screenshot', 'N/A')}\n")
                    f.write(f"- **描述**: {issue.get('description', 'N/A')}\n")
                    f.write(f"- **建议**: {issue.get('suggestion', 'N/A')}\n")
                    f.write(f"\n")
            
            # 每个截图的详细分析
            f.write(f"## 📸 详细分析结果\n\n")
            for result in report_data['all_results']:
                if not result.get('success', True):
                    continue
                
                f.write(f"### {result.get('filename', 'N/A')}\n\n")
                f.write(f"**评分**: {result.get('overall_score', 'N/A')}/100\n\n")
                f.write(f"**评估**: {result.get('overall_assessment', 'N/A')}\n\n")
                
                issues = result.get('issues', [])
                if issues:
                    f.write(f"**发现的问题** ({len(issues)}个):\n\n")
                    for issue in issues:
                        severity_emoji = {
                            'high': '🔴',
                            'medium': '🟡',
                            'low': '🟢'
                        }.get(issue.get('severity', 'low'), '⚪')
                        f.write(f"- {severity_emoji} **[{issue.get('category', 'N/A')}]** {issue.get('title', 'N/A')}\n")
                        f.write(f"  - 描述: {issue.get('description', 'N/A')}\n")
                        f.write(f"  - 位置: {issue.get('location', 'N/A')}\n")
                        f.write(f"  - 建议: {issue.get('suggestion', 'N/A')}\n")
                
                positive_points = result.get('positive_points', [])
                if positive_points:
                    f.write(f"\n**优点**:\n\n")
                    for point in positive_points:
                        f.write(f"- ✅ {point}\n")
                
                f.write(f"\n---\n\n")
        
        return md_file

