#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coordinate converter utility - converts coordinates between different resolutions
"""

from typing import Tuple, Optional
from .adb_controller import ADBController


class CoordinateConverter:
    """Coordinate converter for handling resolution scaling"""
    
    def __init__(self, device_id: str = None, reference_width: int = None, reference_height: int = None):
        """
        Initialize coordinate converter
        
        Args:
            device_id: Device ID (optional, for getting current screen size)
            reference_width: Reference screen width (for scaling from)
            reference_height: Reference screen height (for scaling from)
        """
        self.device_id = device_id
        self.reference_width = reference_width
        self.reference_height = reference_height
        self._current_screen_size = None
    
    def get_current_screen_size(self) -> Tuple[int, int]:
        """Get current device screen size"""
        if self._current_screen_size is None:
            try:
                adb = ADBController(device_id=self.device_id)
                self._current_screen_size = adb.get_screen_size()
            except Exception as e:
                # Fallback to default if cannot get screen size
                print(f"  ⚠️  Cannot get screen size, using default: {e}")
                self._current_screen_size = (1080, 2400)
        return self._current_screen_size
    
    def convert_coordinate(
        self, 
        x: int, 
        y: int, 
        from_width: int = None, 
        from_height: int = None,
        to_width: int = None,
        to_height: int = None
    ) -> Tuple[int, int]:
        """
        Convert coordinate from one resolution to another
        
        Args:
            x: X coordinate in source resolution
            y: Y coordinate in source resolution
            from_width: Source screen width (if None, uses reference_width or current screen width)
            from_height: Source screen height (if None, uses reference_height or current screen height)
            to_width: Target screen width (if None, uses current device screen width)
            to_height: Target screen height (if None, uses current device screen height)
        
        Returns:
            (converted_x, converted_y) - Coordinates in target resolution
        """
        # Determine source resolution
        if from_width is None:
            from_width = self.reference_width
        if from_height is None:
            from_height = self.reference_height
        
        # If no source resolution specified, assume coordinates are already in target resolution
        if from_width is None or from_height is None:
            return (x, y)
        
        # Determine target resolution
        if to_width is None or to_height is None:
            to_width, to_height = self.get_current_screen_size()
        
        # Calculate scale factors
        scale_x = to_width / from_width
        scale_y = to_height / from_height
        
        # Convert coordinates
        converted_x = int(x * scale_x)
        converted_y = int(y * scale_y)
        
        return (converted_x, converted_y)
    
    def convert_from_reference(self, x: int, y: int) -> Tuple[int, int]:
        """
        Convert coordinate from reference resolution to current device resolution
        
        Args:
            x: X coordinate in reference resolution
            y: Y coordinate in reference resolution
        
        Returns:
            (converted_x, converted_y) - Coordinates in current device resolution
        """
        if self.reference_width is None or self.reference_height is None:
            raise ValueError("Reference resolution not set. Please provide reference_width and reference_height.")
        
        return self.convert_coordinate(x, y, 
                                      from_width=self.reference_width, 
                                      from_height=self.reference_height)
    
    def convert_to_reference(self, x: int, y: int) -> Tuple[int, int]:
        """
        Convert coordinate from current device resolution to reference resolution
        
        Args:
            x: X coordinate in current device resolution
            y: Y coordinate in current device resolution
        
        Returns:
            (converted_x, converted_y) - Coordinates in reference resolution
        """
        if self.reference_width is None or self.reference_height is None:
            raise ValueError("Reference resolution not set. Please provide reference_width and reference_height.")
        
        to_width, to_height = self.get_current_screen_size()
        return self.convert_coordinate(x, y,
                                     from_width=to_width,
                                     from_height=to_height,
                                     to_width=self.reference_width,
                                     to_height=self.reference_height)


def convert_coordinate_simple(
    x: int,
    y: int,
    from_resolution: Tuple[int, int],
    to_resolution: Tuple[int, int]
) -> Tuple[int, int]:
    """
    Simple coordinate conversion utility function
    
    Args:
        x: X coordinate in source resolution
        y: Y coordinate in source resolution
        from_resolution: (width, height) of source resolution
        to_resolution: (width, height) of target resolution
    
    Returns:
        (converted_x, converted_y) - Coordinates in target resolution
    
    Example:
        # Convert from 1080x2400 to 1440x3200
        new_x, new_y = convert_coordinate_simple(540, 1200, (1080, 2400), (1440, 3200))
    """
    from_width, from_height = from_resolution
    to_width, to_height = to_resolution
    
    scale_x = to_width / from_width
    scale_y = to_height / from_height
    
    converted_x = int(x * scale_x)
    converted_y = int(y * scale_y)
    
    return (converted_x, converted_y)

