#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探索策略 - 负责元素过滤、去重和探索决策
"""

from typing import List, Dict, Set
from .ui_analyzer import UIAnalyzer


class ExplorationStrategy:
    """探索策略"""
    
    def __init__(self, 
                 min_text_length: int = 1,
                 max_text_length: int = 30,
                 min_list_items: int = 3,
                 max_elements_per_depth: Dict[int, int] = None):
        """
        初始化探索策略
        
        Args:
            min_text_length: 最小文本长度
            max_text_length: 最大文本长度
            min_list_items: 列表项最小数量
            max_elements_per_depth: 每层最大探索元素数
        """
        self.min_text_length = min_text_length
        self.max_text_length = max_text_length
        self.min_list_items = min_list_items
        self.max_elements_per_depth = max_elements_per_depth or {
            0: 5, 1: 4, 2: 3, 3: 2
        }
        self.default_max_elements = 2
        
        # 去重数据结构
        self.visited_pages: Set[str] = set()
        self.visited_paths: Set[str] = set()
        self.skipped_count = 0
        
        # UI 分析器
        self.ui_analyzer = UIAnalyzer()
        
        print(f"✅ 探索策略初始化完成")
    
    def reset(self):
        """重置探索状态"""
        self.visited_pages.clear()
        self.visited_paths.clear()
        self.skipped_count = 0
        print(f"🔄 探索状态已重置")
    
    def is_page_visited(self, ui_elements: List[Dict], path: List[str] = None) -> bool:
        """
        检查页面是否已访问
        
        Args:
            ui_elements: UI元素列表
            path: 当前路径
            
        Returns:
            True 如果已访问，False 否则
        """
        # 方法1：基于UI指纹检查
        fingerprint = self.ui_analyzer.generate_page_fingerprint(ui_elements)
        if fingerprint in self.visited_pages:
            return True
        
        # 方法2：基于路径检查（可选）
        if path:
            path_key = " > ".join(path)
            if path_key in self.visited_paths:
                return True
        
        return False
    
    def mark_page_visited(self, ui_elements: List[Dict], path: List[str] = None):
        """
        标记页面为已访问
        
        Args:
            ui_elements: UI元素列表
            path: 当前路径
        """
        # 记录UI指纹
        fingerprint = self.ui_analyzer.generate_page_fingerprint(ui_elements)
        self.visited_pages.add(fingerprint)
        
        # 记录路径
        if path:
            path_key = " > ".join(path)
            self.visited_paths.add(path_key)
    
    def filter_valid_elements(self, ui_elements: List[Dict]) -> List[Dict]:
        """
        过滤有效元素（文本长度合适）
        
        Args:
            ui_elements: UI元素列表
            
        Returns:
            过滤后的元素列表
        """
        valid_elements = []
        for elem in ui_elements:
            text = elem.get('text') or elem.get('content_desc', '')
            # 使用配置的文本长度范围
            if text and self.min_text_length < len(text) < self.max_text_length:
                valid_elements.append(elem)
        
        return valid_elements
    
    def filter_list_items(self, elements: List[Dict]) -> List[Dict]:
        """
        智能过滤列表项，相同类型的数据只保留一个代表
        
        Args:
            elements: UI元素列表
            
        Returns:
            过滤后的元素列表
        """
        if not elements:
            return elements
        
        # 检测列表模式：相同resource_id且文本相似
        grouped = {}  # key: (resource_id, 模式), value: [elements]
        filtered = []
        
        for elem in elements:
            text = elem.get('text', '')
            resource_id = elem.get('resource_id', '')
            
            # 如果没有resource_id，直接保留
            if not resource_id:
                filtered.append(elem)
                continue
            
            # 检测文本模式（移除数字、日期等变化部分）
            pattern = self.ui_analyzer.extract_text_pattern(text)
            
            # 分组key
            group_key = (resource_id, pattern)
            
            if group_key not in grouped:
                grouped[group_key] = []
            
            grouped[group_key].append(elem)
        
        # 处理分组
        for group_key, group_elements in grouped.items():
            # 如果该组只有一个元素，直接保留
            if len(group_elements) == 1:
                filtered.append(group_elements[0])
            # 如果有多个相同模式的元素，认为是列表，只保留第一个
            elif len(group_elements) >= self.min_list_items:
                # 保留第一个作为代表
                filtered.append(group_elements[0])
                # 记录被过滤的元素
                for elem in group_elements[1:]:
                    elem['_list_item_filtered'] = True
            else:
                # 2个元素，都保留
                filtered.extend(group_elements)
        
        return filtered
    
    def get_max_elements_for_depth(self, depth: int) -> int:
        """
        获取指定深度的最大探索元素数
        
        Args:
            depth: 当前深度
            
        Returns:
            最大元素数
        """
        return self.max_elements_per_depth.get(depth, self.default_max_elements)
    
    def should_explore_element(self, element: Dict) -> bool:
        """
        判断是否应该探索某个元素
        
        Args:
            element: UI元素
            
        Returns:
            True 如果应该探索，False 否则
        """
        # 检查是否被列表过滤标记
        if element.get('_list_item_filtered'):
            return False
        
        # 检查文本长度
        text = element.get('text') or element.get('content_desc', '')
        if not text:
            return False
        
        if not (self.min_text_length < len(text) < self.max_text_length):
            return False
        
        return True
    
    def get_exploration_statistics(self) -> Dict:
        """
        获取探索统计信息
        
        Returns:
            统计信息字典
        """
        total_visited = len(self.visited_pages)
        total_attempts = total_visited + self.skipped_count
        dedup_rate = (self.skipped_count / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            'visited_pages': total_visited,
            'skipped_pages': self.skipped_count,
            'total_attempts': total_attempts,
            'dedup_rate': dedup_rate
        }
