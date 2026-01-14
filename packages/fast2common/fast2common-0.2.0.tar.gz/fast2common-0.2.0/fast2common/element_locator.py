#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Element locator - Find clickable element center coordinates by text
"""

import time
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Tuple

from .adb_controller import ADBController
from .ui_analyzer import UIAnalyzer


class ElementLocator:
    """Element locator for finding clickable element center coordinates by text"""
    
    def __init__(self):
        """Initialize element locator"""
        self.ui_analyzer = UIAnalyzer()
    
    def _calculate_y_range(self, y_position: str, screen_height: int) -> Tuple[int, int]:
        """
        Calculate Y coordinate range based on position string
        
        Args:
            y_position: Position string - "top", "middle", or "bottom"
            screen_height: Screen height in pixels
        
        Returns:
            (y_min, y_max) tuple
        """
        if y_position == "top":
            return (0, screen_height // 3)
        elif y_position == "middle":
            return (screen_height // 3, 2 * screen_height // 3)
        elif y_position == "bottom":
            return (2 * screen_height // 3, screen_height)
        else:
            raise ValueError(f"Invalid y_position: {y_position}. Must be 'top', 'middle', or 'bottom'")
    
    def find_clickable_element_center(
        self,
        text: str,
        device_id: Optional[str] = None,
        y_position: Optional[str] = None,
        strict_match: bool = True
    ) -> Optional[Tuple[int, int]]:
        """
        Find clickable element center coordinates by text
        
        Args:
            text: Text to search for
            device_id: Device ID (optional, uses current device if not provided)
            y_position: Y coordinate range limit - "top" (upper third), "middle" (middle third), "bottom" (lower third)
            strict_match: Whether to use strict text matching (default: True)
        
        Returns:
            (x, y) center coordinates or None if not found
        
        Example:
            # Find element in upper third
            coords = locator.find_clickable_element_center("登录", device_id="device123", y_position="top")
            
            # Find element in middle third
            coords = locator.find_clickable_element_center("搜索", y_position="middle")
            
            # Find element in lower third (bottom navigation)
            coords = locator.find_clickable_element_center("我的", y_position="bottom")
            
            # No Y range limit
            coords = locator.find_clickable_element_center("设置")
        """
        try:
            # Create ADB controller
            adb = ADBController(device_id=device_id)
            
            # Get screen size for Y range calculation
            screen_width, screen_height = adb.get_screen_size()
            
            # Calculate Y coordinate range if y_position is provided
            y_range = None
            if y_position:
                if y_position not in ["top", "middle", "bottom"]:
                    print(f"  ⚠️  Invalid y_position: {y_position}. Must be 'top', 'middle', or 'bottom'")
                    return None
                y_range = self._calculate_y_range(y_position, screen_height)
                print(f"  📍 Y range limit: {y_position} ({y_range[0]}-{y_range[1]})")
            
            # Get UI dump
            temp_xml = Path(tempfile.gettempdir()) / f"ui_locator_{int(time.time())}.xml"
            if not adb.get_ui_xml(temp_xml):
                print(f"  ❌ Failed to get UI dump")
                return None
            
            # Parse XML to get root element (needed for parent search)
            try:
                tree = ET.parse(temp_xml)
                root = tree.getroot()
            except Exception as e:
                print(f"  ❌ Failed to parse UI XML: {e}")
                try:
                    temp_xml.unlink(missing_ok=True)
                except Exception:
                    pass
                return None
            
            # Find element by text
            result = self.ui_analyzer.find_element_by_text(
                temp_xml,
                text,
                strict_match=strict_match,
                y_range=y_range
            )
            
            # Clean up temp file
            try:
                temp_xml.unlink(missing_ok=True)
            except Exception:
                pass
            
            if not result:
                print(f"  ⚠️  Element not found: {text}")
                return None
            
            bounds, match_type, element = result
            
            # If element is not clickable, try to find clickable parent
            if match_type in ['not_clickable', 'contains_not_clickable']:
                print(f"  🔍 Element found but not clickable, searching for clickable parent...")
                try:
                    parent_bounds = self.ui_analyzer._find_clickable_parent(element, root)
                    if parent_bounds:
                        bounds = parent_bounds
                        match_type = 'parent_container'
                        print(f"  ✅ Found clickable parent container")
                    else:
                        print(f"  ❌ No clickable parent found")
                        return None
                except Exception as e:
                    print(f"  ⚠️  Failed to find clickable parent: {e}")
                    return None
            
            # Parse bounds to get center coordinates
            # Note: UI Automator dump returns bounds in physical pixels, not dp
            # These coordinates can be used directly with adb tap command (which expects pixels)
            center_coords = self.ui_analyzer.parse_bounds(bounds)
            
            if center_coords:
                x, y = center_coords
                print(f"  ✅ Found element '{text}' at center: ({x}, {y}) [match_type: {match_type}, pixel coordinates]")
                return (x, y)
            else:
                print(f"  ❌ Failed to parse bounds: {bounds}")
                return None
                
        except Exception as e:
            print(f"  ❌ Error finding element: {e}")
            import traceback
            traceback.print_exc()
            return None

