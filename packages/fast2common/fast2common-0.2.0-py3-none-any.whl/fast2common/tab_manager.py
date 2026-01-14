#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
底部Tab管理器 - 使用AI自动识别和管理底部Tab元素
解决模拟Tab（非真实组件）的检测和点击问题
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class TabElement:
    """Tab元素数据类"""
    name: str  # Tab名称（如：背词、学习、AI）
    module_id: str  # 模块ID（如：recite、learning、ai）
    bounds: Tuple[int, int, int, int]  # 坐标 (x1, y1, x2, y2)
    center_x: int  # 中心点X坐标
    center_y: int  # 中心点Y坐标
    description: str  # AI分析的功能描述
    confidence: float  # AI识别置信度
    last_updated: str  # 最后更新时间
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TabElement':
        """从字典创建"""
        return cls(**data)


class TabManager:
    """底部Tab管理器 - AI驱动的智能Tab识别和管理"""
    
    def __init__(self, app_code: str, laite_dir: Path):
        """
        初始化Tab管理器
        
        参数:
            app_code: 应用代码（如：laite_en）
            laite_dir: 应用目录
        """
        self.app_code = app_code
        self.laite_dir = laite_dir
        
        # Tab数据存储路径
        self.tab_data_file = laite_dir / "config" / "bottom_tabs.json"
        self.tab_data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载已保存的Tab数据
        self.tabs: Dict[str, TabElement] = self._load_tabs()
        
        # 界面描述（AI分析的原始文本）
        self.screen_description: Optional[str] = None
        
        print(f"📱 Tab管理器初始化完成")
        print(f"   应用: {app_code}")
        print(f"   存储: {self.tab_data_file}")
        print(f"   已加载: {len(self.tabs)} 个Tab")
    
    def _load_tabs(self) -> Dict[str, TabElement]:
        """从文件加载Tab数据"""
        if not self.tab_data_file.exists():
            return {}
        
        try:
            with open(self.tab_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tabs = {}
            for module_id, tab_data in data.get('tabs', {}).items():
                tabs[module_id] = TabElement.from_dict(tab_data)
            
            return tabs
        except Exception as e:
            print(f"  ⚠️  加载Tab数据失败: {e}")
            return {}
    
    def _save_tabs(self):
        """保存Tab数据到文件"""
        try:
            data = {
                'app_code': self.app_code,
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S'),
                'tabs': {
                    module_id: tab.to_dict() 
                    for module_id, tab in self.tabs.items()
                }
            }
            
            with open(self.tab_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"  ⚠️  保存Tab数据失败: {e}")
            return False
    
    def _save_page_description(self, page_id: str = 'page_01', page_name: str = '首页底部Tab栏', related_file: str = 'bottom_tabs.json'):
        """保存页面描述到专用文件
        
        参数:
            page_id: 页面ID（如：page_01, page_02）
            page_name: 页面名称（如：首页底部Tab栏）
            related_file: 关联的数据文件
        
        返回:
            是否成功
        """
        if not self.screen_description:
            return False
        
        try:
            # 动态生成文件路径
            page_file = self.laite_dir / "config" / f"{page_id}.json"
            
            page_data = {
                'page_id': page_id,
                'page_name': page_name,
                'analysis_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'description': self.screen_description,
                'data_source': 'AI视觉分析',
                'related_file': related_file
            }
            
            with open(page_file, 'w', encoding='utf-8') as f:
                json.dump(page_data, f, ensure_ascii=False, indent=2)
            
            print(f"   📄 页面描述保存到: {page_file}")
            return True
        except Exception as e:
            print(f"  ⚠️  保存页面描述失败: {e}")
            return False
    
    def analyze_and_store_tabs(self, screenshot_path: Path, ai_client, y_range: tuple = None) -> bool:
        """
        使用AI分析截图中的底部Tab并存储
        
        参数:
            screenshot_path: 首页截图路径
            ai_client: AI客户端实例
            y_range: Tab区域Y坐标范围 (y_min, y_max)，None则自动检测
        
        返回:
            是否成功
        """
        print(f"\n🤖 使用AI分析Tab区域...")
        
        # 获取屏幕尺寸用于提示
        from .adb_controller import ADBController
        adb_temp = ADBController()
        screen_width, screen_height = adb_temp.get_screen_size()
        tab_y_start = int(screen_height * 0.83)  # 底部Tab区域起始位置
        
        # 构建AI分析任务（反幻觉优化版本）
        task = f"""你是一个严格的UI分析员，只报告你直接观察到的内容，绝不推测。

🔴 **第一步：数清楚底部Tab栏有几个图标**
- 请从左到右仔细数一遍，屏幕最底部（Y坐标 > {tab_y_start}px）有几个图标
- 不要猜测，不要根据常识填充，只数你直接看到的
- **关键：确认数量后，在心里记住这个数字**

🔵 **第二步：逐个识别每个图标**
- 根据第一步数出的数量，逐个识别每个图标的名称和位置
- **绝对不能超过第一步数出的数量**

🟢 **第三步：输出JSON**
- tabs数组的长度 = 第一步数出的数量
- **绝对不能多，也不能少**

👁️ **请分析这张截图（{screen_width}x{screen_height}px）**

📊 **底部区域定义**：
- Y坐标 > {tab_y_start}px 的区域
- 只关注这个区域的图标，忽略页面内容

📋 **输出格式**（仅为格式参考）：
{{
  "tabs": [
    {{"name": "实际Tab名称1", "module_id": "对应id", "description": "功能描述", "position": "bottom", "center_x": X坐标, "center_y": Y坐标}},
    {{"name": "实际Tab名称2", "module_id": "对应id", "description": "功能描述", "position": "bottom", "center_x": X坐标, "center_y": Y坐标}}
  ]
}}

💡 **module_id命名规则**：
- 英文转小写（AI → ai）
- 中文转拼音/英文（背词 → recite，我的 → my）
- 多词用下划线（个人中心 → personal_center）

🚨 **严禁的行为**：
- ✖️ **禁止根据常识添加Tab**（即使你觉得“应该有首页”，但如果没看到就不要加）
- ✖️ **禁止根据示例数量返回**（示例是2个，但实际可能是3个、4个、5个）
- ✖️ **禁止添加分析过程文字**（只输出纯JSON）

✅ **正确示例**：
如果你数出5个图标，那么tabs数组就必须有且只有 5 个元素
如果你数出3个图标，那么tabs数组就必须有且只有 3 个元素

📌 **坐标要求**：
- center_x: 0-{screen_width} 之间的整数
- center_y: {tab_y_start}-{screen_height} 之间的整数

🛡️ **最后提醒**：
请严格按照"数清楚 → 识别 → 输出JSON"的顺序，不要跳过第一步！

⚠️ **强格式约束（万能模板）**：
请直接输出分析结果的纯JSON格式，不要输出任何无关的开场白、结束语、分析过程。
不要出现[finish]相关内容，不要出现"好的，我来分析"等话术。
回答简洁精准，只返回符合格式的JSON数据。
"""
        
        # 调用AI分析（启用JSON响应模式）
        try:
            analysis_result = ai_client.analyze_screen(
                screenshot_path, 
                task,
                response_format="json_object"  # 启用JSON响应模式
            )
            
            if not analysis_result.get('success'):
                print(f"  ❌ AI分析失败: {analysis_result.get('error')}")
                return False
            
            # 解析AI返回的JSON
            analysis_text = analysis_result['analysis']
            tabs_data, raw_analysis = self._parse_ai_response(analysis_text, ai_client)
            
            if not tabs_data:
                print(f"  ⚠️  未能从 AI响应中提取Tab数据")
                return False
            
            # 保存原始分析文本作为界面描述
            self.screen_description = raw_analysis if raw_analysis else analysis_text
            
            # 获取每个Tab的精确坐标
            from .adb_controller import ADBController
            from .ui_analyzer import UIAnalyzer
            import tempfile
            
            adb = ADBController()
            ui_analyzer = UIAnalyzer()
            
            # 获取UI dump
            temp_xml = Path(tempfile.gettempdir()) / f"tab_analysis_{int(time.time())}.xml"
            if not adb.get_ui_xml(temp_xml):
                print(f"  ⚠️  无法获取UI dump")
                return False
            
            # 为每个Tab查找坐标（优先使用XML中可点击元素的坐标）
            updated_count = 0
            # 计算底部Tab区域（Y轴 > 83%屏幕高度）
            screen_width, screen_height = adb.get_screen_size()
            tab_y_min = int(screen_height * 0.83)
            
            for tab_info in tabs_data:
                name = tab_info['name']
                module_id = tab_info['module_id']
                description = tab_info.get('description', '')
                
                # 🔑 策略：优先从 XML 查找可点击元素
                print(f"\n🔍 查找 Tab: {name}")
                
                # 第一步：尝试从 XML 中查找可点击元素
                result = ui_analyzer.find_clickable_element_by_text(
                    temp_xml,
                    name,
                    y_range=(tab_y_min, screen_height)
                )
                
                if result:
                    # 找到可点击元素，使用XML坐标（最可靠）
                    bounds_str, match_type, element = result
                    import re
                    coords = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
                    
                    if len(coords) == 2:
                        x1, y1 = int(coords[0][0]), int(coords[0][1])
                        x2, y2 = int(coords[1][0]), int(coords[1][1])
                        
                        # 使用XML的中心点
                        center_coords = ui_analyzer.parse_bounds(bounds_str)
                        if center_coords:
                            center_x, center_y = center_coords
                            
                            tab_element = TabElement(
                                name=name,
                                module_id=module_id,
                                bounds=(x1, y1, x2, y2),
                                center_x=center_x,
                                center_y=center_y,
                                description=description,
                                confidence=0.95,  # XML可点击元素，置信度最高
                                last_updated=time.strftime('%Y-%m-%d %H:%M:%S')
                            )
                            
                            self.tabs[module_id] = tab_element
                            updated_count += 1
                            print(f"  ✅ {name} → ({center_x}, {center_y}) [📝XML可点击元素] | {description}")
                            continue
                
                # 第二步：如果没找到可点击元素，尝试查找可点击的父容器
                print(f"  ⚠️  未找到直接可点击元素，尝试查找可点击父容器...")
                parent_result = ui_analyzer.find_clickable_parent_by_text(
                    temp_xml,
                    name,
                    y_range=(tab_y_min, screen_height)
                )
                
                if parent_result:
                    # 找到可点击父容器
                    bounds_str, match_type, element = parent_result
                    import re
                    coords = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
                    
                    if len(coords) == 2:
                        x1, y1 = int(coords[0][0]), int(coords[0][1])
                        x2, y2 = int(coords[1][0]), int(coords[1][1])
                        
                        center_coords = ui_analyzer.parse_bounds(bounds_str)
                        if center_coords:
                            center_x, center_y = center_coords
                            
                            tab_element = TabElement(
                                name=name,
                                module_id=module_id,
                                bounds=(x1, y1, x2, y2),
                                center_x=center_x,
                                center_y=center_y,
                                description=description,
                                confidence=0.9,  # XML父容器，置信度较高
                                last_updated=time.strftime('%Y-%m-%d %H:%M:%S')
                            )
                            
                            self.tabs[module_id] = tab_element
                            updated_count += 1
                            print(f"  ✅ {name} → ({center_x}, {center_y}) [📝可点击父容器] | {description}")
                            continue
                
                # 第三步：如果AI返回了坐标，使用AI坐标作为后备
                ai_center_x = tab_info.get('center_x')
                ai_center_y = tab_info.get('center_y')
                
                if ai_center_x and ai_center_y:
                    print(f"  ⚠️  XML未找到，使用AI识别的坐标...")
                    center_x = int(ai_center_x)
                    center_y = int(ai_center_y)
                    
                    # 使用估算的bounds
                    x1 = max(0, center_x - 50)
                    x2 = min(screen_width, center_x + 50)
                    y1 = max(0, center_y - 40)
                    y2 = min(screen_height, center_y + 40)
                    
                    tab_element = TabElement(
                        name=name,
                        module_id=module_id,
                        bounds=(x1, y1, x2, y2),
                        center_x=center_x,
                        center_y=center_y,
                        description=description,
                        confidence=0.6,  # AI坐标 + 估算bounds，置信度较低
                        last_updated=time.strftime('%Y-%m-%d %H:%M:%S')
                    )
                    
                    self.tabs[module_id] = tab_element
                    updated_count += 1
                    print(f"  ✅ {name} → ({center_x}, {center_y}) [🤖AI坐标+估算Bounds] | {description}")
                else:
                    print(f"  ❌ 未找到'{name}'的坐标（XML和AI都没有）")
            
            # 清理临时文件
            temp_xml.unlink(missing_ok=True)
            
            # 保存到文件
            if updated_count > 0:
                # 保存Tab数据
                self._save_tabs()
                print(f"\n💾 已保存 {updated_count} 个Tab到: {self.tab_data_file}")
                
                # 保存页面描述到专用文件（默认page_01）
                if self.screen_description:
                    desc_preview = self.screen_description[:80] + "..." if len(self.screen_description) > 80 else self.screen_description
                    print(f"   📝 页面描述: {desc_preview}")
                    self._save_page_description()  # 使用默认参数 page_01
                
                return True
            else:
                print(f"\n⚠️  未成功识别任何Tab")
                return False
                
        except Exception as e:
            print(f"  ❌ 分析失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _parse_ai_response(self, response: str, ai_client=None) -> tuple[List[Dict], Optional[str]]:
        """解析AI响应中的JSON数据
        
        参数:
            response: AI响应文本
            ai_client: AI客户端实例（用于二次转换）
        
        返回:
            (tabs_data, raw_analysis): Tab数据列表 + 原始分析文本
        """
        try:
            print(f"\n🔍 AI原始响应:")
            print("="*70)
            print(response[:500] if len(response) > 500 else response)  # 显示前500字符
            if len(response) > 500:
                print(f"... (共{len(response)}字符)")
            print("="*70)
            
            # 保存原始分析文本（用于界面描述）
            raw_analysis = response
            
            # 查找JSON块
            import re
            
            # 尝试多种JSON提取模式（按优先级）
            json_str = None
            
            # 模式1: 标准的 ```json ... ```
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                print(f"  ✓ 使用模式1提取JSON (```json块)")
            
            # 模式2: 只有代码块 ``` ... ```
            if not json_str:
                json_match = re.search(r'```\s*(\{.*?\})\s*```', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    print(f"  ✓ 使用模式2提取JSON (```块)")
            
            # 模式3: 查找最后一个完整的JSON对象（处理混合文本+JSON的情况）
            if not json_str:
                # 从后向前查找完整的JSON对象
                # 匹配 {"tabs": [...]} 格式
                json_match = re.search(r'(\{\s*"tabs"\s*:\s*\[.*?\]\s*\})', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    print(f"  ✓ 使用模式3提取JSON (tabs对象)")
            
            # 模式4: 直接查找JSON数组或对象（最宽松的匹配）
            if not json_str:
                # 先尝试查找数组 [...]
                array_match = re.search(r'(\[.*\])', response, re.DOTALL)
                if array_match:
                    json_str = array_match.group(1)
                    print(f"  ✓ 使用模式4提取JSON (数组)")
                else:
                    # 再尝试查找对象 {...}（从最后一个{开始）
                    # 反向查找最后一个有效的JSON对象
                    brace_positions = [m.start() for m in re.finditer(r'\{', response)]
                    for start_pos in reversed(brace_positions):
                        end_pos = response.find('}', start_pos)
                        if end_pos > start_pos:
                            candidate = response[start_pos:end_pos + 1]
                            # 检查是否包含tabs字段
                            if '"tabs"' in candidate or '"name"' in candidate:
                                json_str = candidate
                                print(f"  ✓ 使用模式4提取JSON (最后的对象)")
                                break
            
            if not json_str:
                print(f"  ❌ 未找到有效的JSON结构")
                
                # 尝试二次请求：将分析文本转换为JSON
                print(f"\n🔄 发起二次请求：将分析文本转换为标准JSON...")
                json_str = self._convert_text_to_json(response, ai_client)
                
                if not json_str:
                    print(f"  ❌ 二次请求也失败，无法提取JSON")
                    return ([], None)
            
            print(f"\n📄 提取的JSON字符串:")
            print(json_str[:300] if len(json_str) > 300 else json_str)
            if len(json_str) > 300:
                print(f"... (共{len(json_str)}字符)")
            
            # 尝试修复常见的JSON格式问题
            json_str = self._fix_json_format(json_str)
            
            # 解析JSON
            data = json.loads(json_str)
            print(f"\n✅ JSON解析成功")
            
            # 检查数据类型
            if not isinstance(data, dict):
                print(f"   ⚠️  顶层数据类型错误: {type(data).__name__}")
                print(f"   期望: dict, 实际: {type(data).__name__}")
                
                # 如果是数组，可能是AI返回了纯坐标数组，需要二次转换
                if isinstance(data, list):
                    print(f"   🔄 检测到纯数组格式，触发二次转换...")
                    print(f"\n🔄 发起二次请求：将坐标数组转换为标准JSON...")
                    json_str = self._convert_text_to_json(response, ai_client)
                    
                    if not json_str:
                        print(f"  ❌ 二次请求也失败，无法提取JSON")
                        return ([], None)
                    
                    # 重新解析
                    data = json.loads(json_str)
                    if not isinstance(data, dict):
                        print(f"   ❌ 二次转换后仍然不是对象类型")
                        return ([], None)
                else:
                    return ([], None)
            
            print(f"   数据结构: {list(data.keys())}")
            
            # 检查是否是示例模板响应或分析文本
            if 'answer' in data and 'tabs' not in data:
                print(f"\n⚠️  AI返回了示例模板而非实际分析结果")
                print(f"   返回内容: {data}")
                print(f"\n💡 可能原因:")
                print(f"   - glm-4.6v 模型可能需要更明确的指令")
                print(f"   - 请确认截图中确实有底部Tab栏")
                print(f"   - 尝试再次运行分析")
                return ([], None)
            
            # 检查是否返回了分析过程而不是最终JSON
            if 'tabs' not in data and len(data.keys()) > 0:
                print(f"\n⚠️  AI返回的JSON格式不符合预期")
                print(f"   返回的键: {list(data.keys())}")
                print(f"   期望的格式: {{\"tabs\": [...]}}")
                print(f"\n💡 尝试手动提取Tab信息...")
                # 尝试从响应文本中手动提取Tab信息
                manual_tabs = self._manual_extract_tabs(response)
                if manual_tabs:
                    return (manual_tabs, raw_analysis)
                return ([], None)
            
            tabs = data.get('tabs', [])
            print(f"   Tab数量: {len(tabs)}")
            
            # 调试：检查tabs的类型
            if tabs:
                print(f"   tabs类型: {type(tabs).__name__}")
                if len(tabs) > 0:
                    print(f"   第一个元素类型: {type(tabs[0]).__name__}")
                    if isinstance(tabs[0], dict):
                        print(f"   第一个元素键: {list(tabs[0].keys())}")
                    else:
                        print(f"   第一个元素内容: {str(tabs[0])[:100]}")
            
            if tabs:
                print(f"\n📋 识别到的Tab:")
                for i, tab in enumerate(tabs, 1):
                    # 检查tab是否为字典
                    if isinstance(tab, dict):
                        print(f"   {i}. {tab.get('name', '?')} ({tab.get('module_id', '?')})")
                    else:
                        print(f"   {i}. [Invalid tab format: {type(tab).__name__}] {str(tab)[:50]}")
                        print(f"\n⚠️  检测到无效的Tab格式，尝试修复...")
                        # 过滤掉非字典的元素
                        tabs = [t for t in tabs if isinstance(t, dict)]
                        print(f"   过滤后剩余 {len(tabs)} 个有效Tab")
                        break
            
            return (tabs, raw_analysis)
            
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON解析错误: {e}")
            print(f"     错误位置: 第{e.lineno}行, 第{e.colno}列")
            print(f"     问题内容: {e.msg}")
            print(f"\n⚠️  AI返回的JSON格式不正确，请检查AI响应格式")
            print(f"\n💡 提示: 确保AI严格按照示例格式返回，包括：")
            print(f"   - 所有属性名和属性值都用双引号包裹")
            print(f"   - 每个属性后加冒号和逗号")
            print(f"   - module_id必须是英文标识符（如learning、recite、ai）")
            print(f"\n🔄 建议: 删除配置文件后重新运行AI分析")
            return ([], None)
        except Exception as e:
            print(f"  ⚠️  解析AI响应失败: {e}")
            import traceback
            traceback.print_exc()
            return ([], None)
    
    def _convert_text_to_json(self, analysis_text: str, ai_client=None) -> Optional[str]:
        """将AI返回的分析文本转换为标准JSON格式
        
        参数:
            analysis_text: AI返回的分析文本
            ai_client: AI客户端实例（如果为None则创建新实例）
        
        返回:
            JSON字符串，失败返回 None
        """
        try:
            # 如果没有传入ai_client，则创建新实例
            if ai_client is None:
                from .ai_client import AIClient
                ai_client = AIClient()
            
            # 检查AI客户端是否启用
            if not ai_client.enable_analysis or not ai_client.client:
                print(f"  ❌ AI分析未启用，无法进行二次转换")
                return None
            
            # 构建转换任务（强约束、防幻觉）
            conversion_task = f"""你是一个JSON数据提取器，仅负责从TR中提取Tab信息并输出标准JSON。

📝 **原始文本**：
{analysis_text}

🎯 **你的任务**：
从上述文本中提取所有Tab的以下信息：
1. name：Tab名称（如：背词、学习、AI、阅读、我的）
2. center_x：X坐标（整数）
3. center_y：Y坐标（整数）

📊 **输出格式**（严格遵守）：
{{
  "tabs": [
    {{
      "name": "背词",
      "module_id": "recite",
      "description": "背词功能",
      "position": "bottom",
      "center_x": 100,
      "center_y": 2400
    }}
  ]
}}

📌 **module_id命名规则**：
- 中文转英文：背词→recite、学习→learning、我的→my、阅读→reading
- 英文转小写：AI→ai
- 多词用下划线：个人中心→personal_center

⚠️ **严格约束**：
1. 只输出纯JSON，不要任何解释性文字
2. center_x和center_y必须是整数，不是字符串
3. 只提取文本中实际提到的Tab，不要添加或遗漏
4. 不要出现[finish]、“好的”、“让我”等话术
5. 直接输出JSON，不要分析过程
"""
            
            # 直接调用底层API（与analyze_screen类似）
            api_params = {
                "model": ai_client.model,
                "messages": [
                    {
                        "role": "user",
                        "content": conversion_task
                    }
                ],
                "response_format": {"type": "json_object"},  # 强制JSON格式
                # 关键参数：与主分析保持一致
                "stop": ["[finish]"],
                "temperature": 0.3,
                "max_tokens": 2048,
            }
            
            print(f"  🔄 调用AI转换服务 (模型: {ai_client.model})...")
            response = ai_client.client.chat.completions.create(**api_params)
            
            # 提取转换结果
            converted_text = response.choices[0].message.content
            
            if not converted_text:
                print(f"  ❌ 转换结果为空")
                return None
            
            print(f"\n✅ 二次请求成功，获得JSON数据")
            print(f"   转换后长度: {len(converted_text)} 字符")
            
            # 尝试从转换结果中提取JSON
            import re
            
            # 查找 {"tabs": [...]} 格式
            json_match = re.search(r'(\{\s*"tabs"\s*:\s*\[.*?\]\s*\})', converted_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                print(f"  ✓ 提取到tabs对象")
                return json_str
            
            # 如果没有代码块，直接返回原文本（可能本身就是JSON）
            print(f"  ✓ 直接使用转换结果")
            return converted_text
            
        except Exception as e:
            print(f"  ❌ 转换过程失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _manual_extract_tabs(self, response: str) -> List[Dict]:
        """从分析文本中手动提取Tab信息（后备方案）
        
        参数:
            response: AI响应文本
        
        返回:
            Tab信息列表
        """
        import re
        
        print(f"\n🔧 尝试从响应文本中提取Tab信息...")
        tabs = []
        
        # 匹配模式：第X个tab（名称）：中心X约XXX，中心Y约XXX
        # 或：- 第一个tab（首页）：中心X约XX
        pattern = r'第[\u4e00二三四五六\d]+个tab（([^）]+)）.*?中心X约(\d+).*?中心Y约(\d+)'
        matches = re.findall(pattern, response)
        
        # 名称到module_id的映射
        name_to_id = {
            '首页': 'home',
            '学习': 'learning',
            '背词': 'recite',
            'AI': 'ai',
            '阅读': 'reading',
            '我的': 'my',
            '个人': 'my'
        }
        
        for name, x, y in matches:
            name = name.strip()
            module_id = name_to_id.get(name, name.lower().replace(' ', '_'))
            
            tab_info = {
                'name': name,
                'module_id': module_id,
                'description': f'{name}功能模块',
                'position': 'bottom',
                'center_x': int(x),
                'center_y': int(y)
            }
            tabs.append(tab_info)
            print(f"  ✓ 提取: {name} ({module_id}) -> ({x}, {y})")
        
        if tabs:
            print(f"\n✅ 手动提取成功，共 {len(tabs)} 个Tab")
        else:
            print(f"\n⚠️  手动提取失败，未找到匹配的Tab信息")
        
        return tabs
    
    def get_tab(self, module_id: str) -> Optional[TabElement]:
        """获取指定模块的Tab元素"""
        return self.tabs.get(module_id)
    
    def click_tab(self, module_id: str, adb, verify: bool = True) -> bool:
        """
        点击指定的Tab
        
        参数:
            module_id: 模块ID
            adb: ADB控制器实例
            verify: 是否验证切换成功（通过UI变化检测）
        
        返回:
            是否成功
        """
        import time
        import tempfile
        from pathlib import Path
        
        tab = self.get_tab(module_id)
        if not tab:
            print(f"  ⚠️  未找到模块'{module_id}'的Tab数据")
            return False
        
        print(f"  👆 点击Tab: {tab.name} ({tab.center_x}, {tab.center_y})")
        
        # 如需验证，先获取当前UI指纹
        before_fingerprint = None
        if verify:
            from .ui_analyzer import UIAnalyzer
            
            temp_xml = Path(tempfile.gettempdir()) / f"tab_before_{int(time.time())}.xml"
            if adb.get_ui_xml(temp_xml):
                ui_analyzer = UIAnalyzer()
                elements = ui_analyzer.parse_xml(temp_xml)
                before_fingerprint = ui_analyzer.generate_page_fingerprint(elements)
                temp_xml.unlink(missing_ok=True)
        
        # 直接点击中心坐标
        success = adb.tap(tab.center_x, tab.center_y)
        
        if not success:
            print(f"  ❌ Tab点击失败")
            return False
        
        # 等待页面切换
        time.sleep(1.5)
        
        # 验证是否切换成功
        if verify and before_fingerprint:
            from .ui_analyzer import UIAnalyzer
            
            temp_xml = Path(tempfile.gettempdir()) / f"tab_after_{int(time.time())}.xml"
            if adb.get_ui_xml(temp_xml):
                ui_analyzer = UIAnalyzer()
                elements = ui_analyzer.parse_xml(temp_xml)
                after_fingerprint = ui_analyzer.generate_page_fingerprint(elements)
                temp_xml.unlink(missing_ok=True)
                
                if before_fingerprint == after_fingerprint:
                    print(f"  ⚠️  Tab点击后页面未变化，可能切换失败")
                    print(f"     建议：检查坐标 ({tab.center_x}, {tab.center_y}) 是否准确")
                    return False
                else:
                    print(f"  ✅ Tab切换成功（页面已变化）")
        else:
            print(f"  ✅ Tab点击成功")
        
        return True
    
    def has_tabs(self) -> bool:
        """是否已有Tab数据"""
        return len(self.tabs) > 0
    
    def get_all_tabs(self) -> Dict[str, Dict]:
        """获取所有Tab数据
        
        返回:
            字典，键为module_id，值为Tab信息字典 {'text': '名称', 'center_x': x, 'center_y': y}
        """
        return {
            module_id: {
                'text': tab.name,
                'center_x': tab.center_x,
                'center_y': tab.center_y,
                'description': tab.description
            }
            for module_id, tab in self.tabs.items()
        }
    
    def verify_tab_coordinate(self, module_id: str, adb) -> bool:
        """
        验证Tab坐标是否准确
        
        参数:
            module_id: 模块ID
            adb: ADB控制器实例
        
        返回:
            坐标是否在Tab区域内
        """
        tab = self.get_tab(module_id)
        if not tab:
            return False
        
        # 检查坐标是否在底部Tab区域
        screen_width, screen_height = adb.get_screen_size()
        tab_y_min = int(screen_height * 0.83)
        
        if tab.center_y < tab_y_min:
            print(f"  ⚠️  {tab.name}的Y坐标({tab.center_y})低于Tab区域起始位置({tab_y_min})")
            return False
        
        if tab.center_x < 0 or tab.center_x > screen_width:
            print(f"  ⚠️  {tab.name}的X坐标({tab.center_x})超出屏幕范围(0-{screen_width})")
            return False
        
        print(f"  ✅ {tab.name}的坐标({tab.center_x}, {tab.center_y})在有效范围内")
        return True
    
    def list_tabs(self):
        """列出所有Tab"""
        if not self.tabs:
            print("  ℹ️  暂无Tab数据")
            return
        
        print(f"\n📋 已存储的Tab ({len(self.tabs)} 个):")
        print("="*70)
        for module_id, tab in self.tabs.items():
            print(f"  • {tab.name} ({module_id})")
            print(f"    坐标: ({tab.center_x}, {tab.center_y})")
            print(f"    描述: {tab.description}")
            print(f"    置信度: {tab.confidence:.2f}")
            print(f"    更新时间: {tab.last_updated}")
            print()
    
    def _fix_json_format(self, json_str: str) -> str:
        """修复常见的JSON格式问题"""
        import re
            
        print(f"\n🔧 修复JSON格式问题...")
        original_str = json_str
            
        # 0. 如果是数组，包装为对象: [{{...}}] → {{"tabs": [{{...}}]}}
        # 但不处理纯坐标数组 [[99,970],...]，让后续逻辑触发二次转换
        json_str_stripped = json_str.strip()
        if json_str_stripped.startswith('[') and json_str_stripped.endswith(']'):
            # 检查是否为纯坐标数组（元素是[[x,y],...]格式）
            try:
                import json
                test_data = json.loads(json_str_stripped)
                if isinstance(test_data, list) and len(test_data) > 0:
                    # 如果第一个元素是list（纯坐标），不包装，让后续逻辑处理
                    if isinstance(test_data[0], list):
                        print(f"  ⚠️  检测到纯坐标数组，不进行包装（留给二次转换处理）")
                    # 如果第一个元素是dict（Tab对象），才包装
                    elif isinstance(test_data[0], dict):
                        json_str = '{{"tabs": ' + json_str + '}}'
                        print(f"  ✓ 将数组包装为对象: {{\"tabs\": [...]}}")
            except:
                # 解析失败，安全起见不包装
                pass
            
        # 0.5. 移除JSON后面的解释性文字（在最后一个}]之后的所有内容）
        # 查找最后一个 }] 或 } 的位置
        last_brace_match = None
        for match in re.finditer(r'\}\s*]\s*\}|\}\s*\}', json_str):
            last_brace_match = match
            
        if last_brace_match:
            end_pos = last_brace_match.end()
            # 检查后面是否有非空白字符
            remaining = json_str[end_pos:].strip()
            if remaining and not remaining.startswith(','):
                json_str = json_str[:end_pos]
                print(f"  ✓ 移除JSON后的解释性文字")
            
        # 1. 移除注释（// ...）
        json_str = re.sub(r'//.*?\n', '\n', json_str)
            
        # 2. 修复等号冒号为冒号："key" =: "value" → "key": "value"
        json_str = re.sub(r'"(\w+)"\s*=:\s*', r'"\1": ', json_str)
            
        # 3. 修复等号为冒号："key" = "value" → "key": "value"
        json_str = re.sub(r'"(\w+)"\s*=\s*', r'"\1": ', json_str)
            
        # 4. 修复属性名中的等号："module_id=" → "module_id"
        json_str = re.sub(r'"(\w+)=\s*"', r'"\1"', json_str)
            
        # 5. 修复属性名后的等号冒号："module_id=":"value" → "module_id":"value"
        json_str = re.sub(r'"(\w+)=\s*"\s*:', r'"\1":', json_str)
            
        # 6. 修复属性名缺失双引号：name: → "name":
        # 匹配: 行首空格 + 单词 + 冒号
        json_str = re.sub(r'(\s+)(\w+)(\s*):', r'\1"\2"\3:', json_str)
            
        # 7. 修复属性值缺失双引号（已有双引号的属性名后）："key": value → "key": "value"
        # 但要排除数字、true、false、null
        json_str = re.sub(
            r'"(\w+)"\s*:\s*([^\s"{},\[\]]+)(?=[,\s}])',
            lambda m: f'"{m.group(1)}": "{m.group(2)}"' 
                      if m.group(2) not in ['true', 'false', 'null'] and not m.group(2).replace('.', '').isdigit()
                      else m.group(0),
            json_str
        )
            
        # 8. 修复缺失的冒号："key" "value" → "key": "value"
        json_str = re.sub(r'"(\w+)"\s+"', r'"\1": "', json_str)
            
        # 9. 修复缺失的逗号（在对象之间）：} { → }, {
        json_str = re.sub(r'\}\s*\n\s*\{', '},\n{', json_str)
            
        # 10. 修复缺失的逗号（在属性之间）："value"\n  "key" → "value",\n  "key"
        json_str = re.sub(r'"\s*\n\s*"', '",\n"', json_str)
            
        # 11. 修复属性值后缺失右引号和逗号："description="xxx") → "description": "xxx",
        json_str = re.sub(r'="([^"]+)"\)', r': "\1",', json_str)
            
        # 12. 修复缺失的逗号（属性值后）："value"\n  } → "value"\n  },
        json_str = re.sub(r'(["\d])\s*\n\s*\}', r'\1\n}', json_str)
            
        # 13. 移除多余的逗号（最后一个属性后）："value", } → "value" }
        json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
            
        if json_str != original_str:
            print(f"  ✓ JSON格式已修复")
            print(f"\n📄 修复后的JSON:")
            print(json_str[:400] if len(json_str) > 400 else json_str)
            if len(json_str) > 400:
                print(f"... (共{len(json_str)}字符)")
        else:
            print(f"  ℹ️  无需修复")
            
        return json_str
