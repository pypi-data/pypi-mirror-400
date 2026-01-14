#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI 分析器 - 负责解析 UI XML 和元素分析
"""

import re
import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class UIAnalyzer:
    """UI 分析器"""
    
    def __init__(self, fingerprint_sample_size: int = 20, fingerprint_text_length: int = 10):
        """
        初始化 UI 分析器
        
        Args:
            fingerprint_sample_size: 指纹采样元素数量
            fingerprint_text_length: 指纹文本长度
        """
        self.fingerprint_sample_size = fingerprint_sample_size
        self.fingerprint_text_length = fingerprint_text_length
        
        print(f"✅ UI 分析器初始化完成")
    
    def parse_xml(self, xml_path: Path) -> List[Dict]:
        """
        解析 UI XML 获取可点击元素
        
        Args:
            xml_path: XML 文件路径
            
        Returns:
            可点击元素列表
        """
        clickable = []
        try:
            # Check if file exists before parsing
            if not xml_path.exists():
                print(f"⚠️  XML file does not exist: {xml_path}")
                return clickable
            
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            def extract_text_from_children(node):
                """从子节点提取文本"""
                for child in node:
                    content_desc = child.get('content-desc', '')
                    text = child.get('text', '')
                    if content_desc and content_desc not in ['', '0', '词']:
                        return content_desc
                    if text and text not in ['', '0', '词']:
                        return text
                    # 递归查找
                    child_text = extract_text_from_children(child)
                    if child_text:
                        return child_text
                return ''
            
            for node in root.iter():
                if node.get('clickable') == 'true':
                    text = node.get('text', '')
                    content_desc = node.get('content-desc', '')
                    resource_id = node.get('resource-id', '')
                    bounds = node.get('bounds', '')
                    
                    # 如果节点本身没有文本，尝试从子节点提取
                    if not text and not content_desc:
                        extracted_text = extract_text_from_children(node)
                        if extracted_text:
                            content_desc = extracted_text
                    
                    # 只保留有文本的元素
                    if text or content_desc:
                        clickable.append({
                            'text': text or content_desc,
                            'content_desc': content_desc,
                            'resource_id': resource_id,
                            'bounds': bounds,
                            'class': node.get('class', '')
                        })
        except Exception as e:
            print(f"⚠️  解析 UI XML 失败: {e}")
        
        return clickable
    
    def find_element_by_text(self, xml_path: Path, text: str, strict_match: bool = True, y_range: tuple = None) -> Optional[Tuple[str, str, ET.Element]]:
        """
        通过文本在 XML 中查找元素及其坐标
        
        Args:
            xml_path: XML 文件路径
            text: 要查找的文本
            strict_match: 是否严格匹配（True: 仅精确匹配，False: 允许包含匹配）
            y_range: Y坐标范围限制 (y_min, y_max)，用于限定查找区域（如底部导航栏）
            
        Returns:
            (bounds, match_type, element) 或 None
            - bounds: 坐标字符串 "[x1,y1][x2,y2]"
            - match_type: 匹配类型 ('exact', 'contains', 'parent_container', etc.)
            - element: XML 元素
        """
        try:
            # Check if file exists before parsing
            if not xml_path.exists():
                print(f"⚠️  XML file does not exist: {xml_path}")
                return None
            
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # 递归查找包含目标文本的元素及其可点击父容器
            def find_element_bounds(element, target_text, strict, y_range_filter):
                """递归查找包含目标文本的元素及其坐标"""
                text_attr = element.get('text', '')
                desc_attr = element.get('content-desc', '')
                bounds = element.get('bounds')
                clickable = element.get('clickable', 'false')
                
                # 检查Y坐标范围
                if y_range_filter and bounds:
                    try:
                        coords = re.findall(r'\d+', bounds)
                        if len(coords) >= 2:
                            y = int(coords[1])  # 获取Y1坐标
                            y_min, y_max = y_range_filter
                            if not (y_min <= y <= y_max):
                                # 不在指定Y范围内，跳过
                                pass
                            else:
                                # 在范围内，继续检查
                                if self._check_text_match(target_text, text_attr, desc_attr, strict):
                                    return self._process_matched_element(element, bounds, clickable)
                    except:
                        pass
                else:
                    # 无Y范围限制
                    if self._check_text_match(target_text, text_attr, desc_attr, strict):
                        return self._process_matched_element(element, bounds, clickable)
                
                # 递归查找子元素
                for child in element:
                    result = find_element_bounds(child, target_text, strict, y_range_filter)
                    if result and result[0]:
                        return result
                    elif result and result[1] == 'invalid_bounds':
                        return result
                
                return None
            
            # 首先尝试严格匹配
            result = find_element_bounds(root, text, strict=True, y_range_filter=y_range)
            
            if result and len(result) == 3:
                bounds, match_type, found_element = result
                
                # 如果坐标无效或元素不可点击，尝试查找可点击的父容器
                if match_type in ['invalid_bounds', 'not_clickable']:
                    parent_bounds = self._find_clickable_parent(found_element, root)
                    if parent_bounds:
                        return parent_bounds, 'parent_container', found_element
                
                if bounds and bounds != '[0,0][0,0]':
                    return bounds, match_type, found_element
            
            # 如果严格匹配失败且允许包含匹配，尝试包含匹配
            if not strict_match:
                result = self._find_element_contains(root, text, y_range)
                if result:
                    return result
            
            return None
            
        except Exception as e:
            print(f"  ❌ 查找元素失败: {e}")
            return None
    
    def find_clickable_element_by_text(self, xml_path: Path, text: str, y_range: tuple = None) -> Optional[Tuple[str, str, ET.Element]]:
        """
        查找可点击元素（优先精确匹配）
        
        Args:
            xml_path: XML文件路径
            text: 要查找的文本
            y_range: Y坐标范围 (y_min, y_max)
        
        Returns:
            (bounds, match_type, element) 或 None
        """
        try:
            # Check if file exists before parsing
            if not xml_path.exists():
                print(f"⚠️  XML file does not exist: {xml_path}")
                return None
            
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            def find_clickable(element, target_text, y_range_filter):
                text_attr = element.get('text', '')
                desc_attr = element.get('content-desc', '')
                bounds = element.get('bounds', '')
                clickable = element.get('clickable', 'false')
                
                # 检查Y坐标范围
                in_y_range = True
                if y_range_filter and bounds:
                    try:
                        coords = re.findall(r'\d+', bounds)
                        if len(coords) >= 2:
                            y = int(coords[1])
                            y_min, y_max = y_range_filter
                            in_y_range = (y_min <= y <= y_max)
                    except:
                        pass
                
                # 只查找可点击且匹配文本的元素
                if in_y_range and clickable == 'true' and (target_text == text_attr or target_text == desc_attr):
                    if bounds and bounds != '[0,0][0,0]':
                        return bounds, 'exact_clickable', element
                
                # 递归查找
                for child in element:
                    result = find_clickable(child, target_text, y_range_filter)
                    if result:
                        return result
                
                return None
            
            return find_clickable(root, text, y_range)
            
        except Exception as e:
            print(f"  ❌ 查找可点击元素失败: {e}")
            return None
    
    def find_clickable_parent_by_text(self, xml_path: Path, text: str, y_range: tuple = None) -> Optional[Tuple[str, str, ET.Element]]:
        """
        查找包含指定文本的可点击父容器（用于Tab栏等复合布局）
        
        Args:
            xml_path: XML文件路径
            text: 要查找的文本
            y_range: Y坐标范围 (y_min, y_max)
        
        Returns:
            (bounds, match_type, element) 或 None
        """
        try:
            # Check if file exists before parsing
            if not xml_path.exists():
                print(f"⚠️  XML file does not exist: {xml_path}")
                return None
            
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # 构建XPath查询：查找可点击且子元素包含目标文本的元素
            xpath_text = f"//*[@clickable='true' and .//*[contains(@text, '{text}')]]"
            xpath_desc = f"//*[@clickable='true' and .//*[contains(@content-desc, '{text}')]]"
            
            candidates = []
            
            # 尝试text查询
            try:
                elements = root.findall(xpath_text)
                candidates.extend(elements)
            except:
                pass
            
            # 尝试content-desc查询
            try:
                elements = root.findall(xpath_desc)
                candidates.extend(elements)
            except:
                pass
            
            # 过滤Y范围并选择最佳候选
            for element in candidates:
                bounds = element.get('bounds', '')
                if not bounds or bounds == '[0,0][0,0]':
                    continue
                
                # 检查Y范围
                if y_range:
                    try:
                        coords = re.findall(r'\d+', bounds)
                        if len(coords) >= 2:
                            y = int(coords[1])
                            y_min, y_max = y_range
                            if not (y_min <= y <= y_max):
                                continue
                    except:
                        continue
                
                return bounds, 'clickable_parent', element
            
            return None
            
        except Exception as e:
            print(f"  ❌ 查找可点击父容器失败: {e}")
            return None
    
    def _check_text_match(self, target_text: str, text_attr: str, desc_attr: str, strict: bool) -> bool:
        """检查文本是否匹配"""
        if strict:
            return target_text == text_attr or target_text == desc_attr
        else:
            return target_text in text_attr or target_text in desc_attr
    
    def _process_matched_element(self, element: ET.Element, bounds: str, clickable: str) -> Tuple:
        """处理匹配的元素"""
        is_valid_bounds = bounds and bounds != '[0,0][0,0]'
        
        if is_valid_bounds and clickable == 'true':
            return bounds, 'exact', element
        elif is_valid_bounds:
            return bounds, 'not_clickable', element
        else:
            return None, 'invalid_bounds', element
    
    def _find_element_contains(self, root: ET.Element, text: str, y_range: tuple = None) -> Optional[Tuple[str, str, ET.Element]]:
        """查找包含目标文本的元素（包含匹配）"""
        def find_element_bounds_contains(element, target_text, y_range_filter):
            text_attr = element.get('text', '')
            desc_attr = element.get('content-desc', '')
            bounds = element.get('bounds')
            clickable = element.get('clickable', 'false')
            
            # 检查Y坐标范围
            in_y_range = True
            if y_range_filter and bounds:
                try:
                    coords = re.findall(r'\d+', bounds)
                    if len(coords) >= 2:
                        y = int(coords[1])
                        y_min, y_max = y_range_filter
                        in_y_range = (y_min <= y <= y_max)
                except:
                    pass
            
            if in_y_range and (target_text in text_attr or target_text in desc_attr):
                is_valid_bounds = bounds and bounds != '[0,0][0,0]'
                
                if is_valid_bounds and clickable == 'true':
                    return bounds, 'contains', element
                elif is_valid_bounds:
                    return bounds, 'contains_not_clickable', element
            
            for child in element:
                result = find_element_bounds_contains(child, target_text, y_range_filter)
                if result:
                    return result
            
            return None
        
        result = find_element_bounds_contains(root, text, y_range)
        
        if result and len(result) == 3:
            bounds, match_type, found_element = result
            
            if match_type == 'contains_not_clickable':
                parent_bounds = self._find_clickable_parent(found_element, root)
                if parent_bounds:
                    return parent_bounds, 'parent_container', found_element
            
            if bounds and bounds != '[0,0][0,0]':
                return bounds, match_type, found_element
        
        return None
    
    def _find_clickable_parent(self, target_elem: ET.Element, root: ET.Element, parent: ET.Element = None) -> Optional[str]:
        """递归查找目标元素的可点击父容器"""
        if root == target_elem:
            if parent is not None:
                parent_bounds = parent.get('bounds')
                parent_clickable = parent.get('clickable', 'false')
                
                if parent_clickable == 'true' and parent_bounds and parent_bounds != '[0,0][0,0]':
                    return parent_bounds
                else:
                    return self._find_clickable_parent(parent, root)
            return None
        
        for child in root:
            result = self._find_clickable_parent(target_elem, child, root)
            if result:
                return result
        
        return None
    
    def parse_bounds(self, bounds: str) -> Optional[Tuple[int, int]]:
        """
        解析 bounds 字符串并计算中心点坐标
        
        Note: UI Automator dump returns bounds in physical pixels (not dp).
        These coordinates can be used directly with ADB tap command.
        
        Args:
            bounds: bounds 字符串，如 "[x1,y1][x2,y2]" (像素坐标)
            
        Returns:
            (center_x, center_y) 像素坐标或 None
        """
        coords = re.findall(r'\[(\d+),(\d+)\]', bounds)
        
        if len(coords) == 2:
            x1, y1 = int(coords[0][0]), int(coords[0][1])
            x2, y2 = int(coords[1][0]), int(coords[1][1])
            # 计算中心点
            x = (x1 + x2) // 2
            y = (y1 + y2) // 2
            return x, y
        
        return None
    
    def generate_page_fingerprint(self, ui_elements: List[Dict]) -> str:
        """
        从 UI 元素生成页面指纹（用于去重）
        
        使用更稳定的特征：
        1. 优先使用 resource_id（最稳定）
        2. 其次使用 class + text（文本截断）
        3. 增加采样数量提高准确性
        
        Args:
            ui_elements: UI元素列表
            
        Returns:
            页面指纹字符串
        """
        elements_sig = []
        
        # 采样前 N 个元素
        for elem in ui_elements[:self.fingerprint_sample_size]:
            resource_id = elem.get('resource_id', '')
            class_name = elem.get('class', '')
            text = elem.get('text', '')
            
            # 优先使用 resource_id（更稳定）
            if resource_id:
                elements_sig.append(f"id:{resource_id}")
            elif class_name:
                # 只取文本前 N 个字符（避免动态内容影响）
                text_part = text[:self.fingerprint_text_length] if text else ''
                elements_sig.append(f"class:{class_name}:{text_part}")
        
        # 去重并排序确保稳定性
        signature = "|".join(sorted(set(elements_sig)))
        
        # 计算哈希值
        return hashlib.md5(signature.encode()).hexdigest()
    
    def extract_text_pattern(self, text: str) -> str:
        """
        提取文本模式（移除数字、日期等变化部分）
        
        Args:
            text: 元素文本
            
        Returns:
            文本模式
        """
        # 移除数字
        pattern = re.sub(r'\d+', '#', text)
        
        # 移除日期格式 (2024-01-01, 01/01, 等)
        pattern = re.sub(r'\d{4}-\d{2}-\d{2}', 'DATE', pattern)
        pattern = re.sub(r'\d{2}/\d{2}', 'DATE', pattern)
        
        # 移除百分比 (95%, 100%)
        pattern = re.sub(r'\d+%', 'PERCENT', pattern)
        
        # 移除常见单位 (10个, 5分钟, 3次)
        pattern = re.sub(r'\d+(个|分钟|次|天|小时)', '#UNIT', pattern)
        
        return pattern
