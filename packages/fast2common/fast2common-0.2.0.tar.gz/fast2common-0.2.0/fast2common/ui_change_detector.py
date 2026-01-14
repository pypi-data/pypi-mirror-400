#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI change detector - Detect if UI changed after an action
"""

import time
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from .adb_controller import ADBController
from .ui_analyzer import UIAnalyzer


class UIChangeDetector:
    """UI change detector - detects if UI changed after an action"""
    
    def __init__(self):
        """Initialize UI change detector"""
        self.ui_analyzer = UIAnalyzer()
    
    def check_ui_changed(
        self,
        device_id: str,
        before_fingerprint: Optional[str] = None,
        wait_time: float = 1.5,
        timeout: float = 5.0
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if UI changed after an action
        
        Args:
            device_id: Device ID
            before_fingerprint: UI fingerprint before action (if None, will capture it)
            wait_time: Time to wait after action before checking (seconds)
            timeout: Maximum time to wait for UI dump (seconds)
        
        Returns:
            (ui_changed, info_dict)
            - ui_changed: True if UI changed, False otherwise
            - info_dict: Contains method, before_fingerprint, after_fingerprint, etc.
        """
        try:
            adb = ADBController(device_id=device_id)
            
            # Capture before fingerprint if not provided
            if before_fingerprint is None:
                before_fingerprint = self._capture_fingerprint(adb, timeout)
                if before_fingerprint is None:
                    return True, {
                        "method": "fingerprint",
                        "error": "Failed to capture before fingerprint",
                        "assumed_changed": True
                    }
            
            # Wait for UI to respond
            if wait_time > 0:
                time.sleep(wait_time)
            
            # Capture after fingerprint
            after_fingerprint = self._capture_fingerprint(adb, timeout)
            if after_fingerprint is None:
                # If we can't get after fingerprint, assume UI changed (action likely worked)
                return True, {
                    "method": "fingerprint",
                    "before_fingerprint": before_fingerprint,
                    "error": "Failed to capture after fingerprint",
                    "assumed_changed": True
                }
            
            # Compare fingerprints
            ui_changed = (before_fingerprint != after_fingerprint)
            
            return ui_changed, {
                "method": "fingerprint",
                "before_fingerprint": before_fingerprint,
                "after_fingerprint": after_fingerprint,
                "changed": ui_changed
            }
            
        except Exception as e:
            # If detection fails, assume UI changed (action likely worked)
            return True, {
                "method": "fingerprint",
                "error": str(e),
                "assumed_changed": True
            }
    
    def _capture_fingerprint(self, adb: ADBController, timeout: float = 5.0) -> Optional[str]:
        """
        Capture UI fingerprint from device
        
        Args:
            adb: ADBController instance
            timeout: Maximum time to wait (seconds)
        
        Returns:
            UI fingerprint string or None if failed
        """
        try:
            temp_xml = Path(tempfile.gettempdir()) / f"ui_fingerprint_{int(time.time() * 1000)}.xml"
            
            if adb.get_ui_xml(temp_xml):
                # Verify file exists before parsing
                if not temp_xml.exists():
                    print(f"⚠️  UI XML file not found after get_ui_xml: {temp_xml}")
                    return None
                
                elements = self.ui_analyzer.parse_xml(temp_xml)
                fingerprint = self.ui_analyzer.generate_page_fingerprint(elements)
                
                # Clean up temp file
                try:
                    temp_xml.unlink(missing_ok=True)
                except Exception:
                    pass
                
                return fingerprint
            else:
                # Clean up temp file even if failed
                try:
                    temp_xml.unlink(missing_ok=True)
                except Exception:
                    pass
                return None
                
        except Exception as e:
            print(f"⚠️  Failed to capture UI fingerprint: {e}")
            return None
    
    def capture_before_fingerprint(
        self,
        device_id: str,
        timeout: float = 5.0
    ) -> Optional[str]:
        """
        Capture UI fingerprint before an action
        
        Args:
            device_id: Device ID
            timeout: Maximum time to wait (seconds)
        
        Returns:
            UI fingerprint string or None if failed
        """
        try:
            adb = ADBController(device_id=device_id)
            return self._capture_fingerprint(adb, timeout)
        except Exception as e:
            return None

