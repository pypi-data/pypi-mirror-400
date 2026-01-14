#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common 公共模块
可在多个自动化测试项目中复用

模块列表：
- adb_controller: ADB 命令控制器
- ui_analyzer: UI 分析器
- ui_interaction: UI 交互工具（点击、查找等）
  - click_element_by_bounds: 查找bounds坐标 + 计算中心点 + 直接点击（封装三步流程）
- tab_manager: AI驱动的底部Tab管理器
- exploration_strategy: 探索策略
- ai_client: AI 客户端
"""

from .adb_controller import ADBController
from .ui_analyzer import UIAnalyzer
from .ui_interaction import UIInteraction
from .tab_manager import TabManager
from .exploration_strategy import ExplorationStrategy
from .ai_client import AIClient

__all__ = [
    'ADBController',
    'UIAnalyzer',
    'UIInteraction',
    'TabManager',
    'ExplorationStrategy',
    'AIClient',
]

__version__ = '0.1.2'
