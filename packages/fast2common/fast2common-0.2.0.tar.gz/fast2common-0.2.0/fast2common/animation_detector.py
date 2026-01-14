#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Animation completion detector - detects when Android app animations/transitions are complete

Supports three detection methods:
1. Activity lifecycle detection (most accurate for page transitions)
2. FPS stability detection (simplest, works for all animations)
3. GPU idle detection (comprehensive, works for complex animations)
"""

import time
import subprocess
import re
from typing import Optional, Tuple, Dict, Any
from pathlib import Path


def find_adb_path() -> str:
    """Find ADB executable path"""
    common_paths = [
        "/Users/fansc/Library/Android/sdk/platform-tools/adb",
        "/usr/local/bin/adb",
        "/opt/homebrew/bin/adb",
    ]
    
    for path in common_paths:
        if Path(path).exists():
            return path
    
    try:
        result = subprocess.run(["which", "adb"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    raise FileNotFoundError("ADB not found. Please install Android SDK Platform Tools.")


def check_activity_resumed(device_id: str, package_name: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if Activity is in RESUMED state (most accurate for page transitions)
    
    Args:
        device_id: Device ID
        package_name: Optional package name to filter
    
    Returns:
        (is_complete, info_dict)
    """
    try:
        adb_path = find_adb_path()
        result = subprocess.run(
            [adb_path, "-s", device_id, "shell", "dumpsys", "activity", "top"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return False, {"error": f"Command failed: {result.stderr}", "method": "activity"}
        
        output = result.stdout
        
        # Check for RESUMED state
        if "mState=RESUMED" in output:
            # If package_name is provided, verify it matches
            if package_name:
                if package_name in output:
                    return True, {"method": "activity", "state": "RESUMED", "package": package_name}
                else:
                    return False, {"method": "activity", "state": "STARTED", "package_mismatch": True}
            else:
                return True, {"method": "activity", "state": "RESUMED"}
        
        # Check for STARTED state (animation in progress)
        if "mState=STARTED" in output:
            return False, {"method": "activity", "state": "STARTED"}
        
        return False, {"method": "activity", "state": "UNKNOWN", "output": output[:200]}
        
    except subprocess.TimeoutExpired:
        return False, {"error": "Command timeout", "method": "activity"}
    except Exception as e:
        return False, {"error": str(e), "method": "activity"}


def check_fps_stable(device_id: str, package_name: str, stable_frames: int = 3, target_fps: int = 60) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if FPS is stable (indicates animation completion)
    
    Uses dumpsys gfxinfo to check frame rendering stability.
    When animation is complete, FPS should stabilize at device refresh rate.
    
    Args:
        device_id: Device ID
        package_name: App package name
        stable_frames: Number of consecutive stable frames required
        target_fps: Target FPS value (device refresh rate, default 60)
    
    Returns:
        (is_complete, info_dict)
    """
    try:
        adb_path = find_adb_path()
        
        # Get frame timing info using --profile flag for better data
        result = subprocess.run(
            [adb_path, "-s", device_id, "shell", "dumpsys", "gfxinfo", "--profile", package_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            # Fallback to regular gfxinfo if --profile fails
            result = subprocess.run(
                [adb_path, "-s", device_id, "shell", "dumpsys", "gfxinfo", package_name],
                capture_output=True,
                text=True,
                timeout=5
            )
        
        if result.returncode != 0:
            return False, {"error": f"Command failed: {result.stderr}", "method": "fps"}
        
        output = result.stdout
        
        # Parse frame times from gfxinfo output
        # Look for frame timing data (usually in "Profile data in ms" section)
        frame_times = []
        
        # Method 1: Parse from "Profile data" section
        in_profile_section = False
        for line in output.split('\n'):
            if "Profile data" in line or "Janky frames" in line:
                in_profile_section = True
                continue
            
            if in_profile_section:
                # Skip empty lines and headers
                if not line.strip() or line.strip().startswith('Draw') or line.strip().startswith('Process'):
                    if not line.strip():
                        continue
                    else:
                        in_profile_section = False
                        continue
                
                # Parse frame time values (format: numbers separated by spaces or tabs)
                # Each number represents frame render time in ms
                numbers = re.findall(r'\d+\.?\d*', line)
                for num_str in numbers:
                    try:
                        frame_time = float(num_str)
                        # Reasonable frame time: 8-33ms for 60fps (16.67ms ideal)
                        if 5 < frame_time < 50:
                            frame_times.append(frame_time)
                    except ValueError:
                        continue
        
        # Method 2: If no profile data, try to parse from summary stats
        if len(frame_times) < stable_frames:
            # Look for "Total frames rendered" or similar stats
            match = re.search(r'Total frames rendered:\s*(\d+)', output)
            if match:
                total_frames = int(match.group(1))
                # If we have total frames but no timing data, assume stable if no jank
                jank_match = re.search(r'Janky frames:\s*(\d+)', output)
                if jank_match:
                    janky_frames = int(jank_match.group(1))
                    jank_ratio = janky_frames / total_frames if total_frames > 0 else 1.0
                    # Low jank ratio (< 5%) indicates stable rendering
                    is_stable = jank_ratio < 0.05
                    return is_stable, {
                        "method": "fps",
                        "total_frames": total_frames,
                        "janky_frames": janky_frames,
                        "jank_ratio": round(jank_ratio, 3),
                        "stable": is_stable
                    }
        
        if len(frame_times) < stable_frames:
            return False, {"method": "fps", "reason": "insufficient_data", "frames": len(frame_times)}
        
        # Check if recent frames are stable
        recent_frames = frame_times[-stable_frames:] if len(frame_times) >= stable_frames else frame_times
        avg_frame_time = sum(recent_frames) / len(recent_frames)
        fps = 1000 / avg_frame_time if avg_frame_time > 0 else 0
        
        # Check if FPS is close to target and frame times are stable
        fps_diff = abs(fps - target_fps)
        frame_time_variance = max(recent_frames) - min(recent_frames) if len(recent_frames) > 1 else 0
        
        # Animation complete if:
        # 1. FPS is close to target (within 15% for tolerance)
        # 2. Frame time variance is small (< 8ms for 60fps devices)
        # 3. Average frame time is reasonable (close to 16.67ms for 60fps)
        target_frame_time = 1000 / target_fps
        frame_time_diff = abs(avg_frame_time - target_frame_time)
        
        is_stable = (
            fps_diff < (target_fps * 0.15) and 
            frame_time_variance < 8.0 and
            frame_time_diff < (target_frame_time * 0.2)
        )
        
        return is_stable, {
            "method": "fps",
            "fps": round(fps, 1),
            "target_fps": target_fps,
            "avg_frame_time": round(avg_frame_time, 2),
            "target_frame_time": round(target_frame_time, 2),
            "variance": round(frame_time_variance, 2),
            "stable": is_stable,
            "frames_analyzed": len(recent_frames)
        }
        
    except subprocess.TimeoutExpired:
        return False, {"error": "Command timeout", "method": "fps"}
    except Exception as e:
        return False, {"error": str(e), "method": "fps"}


def check_gpu_idle(device_id: str, package_name: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if GPU is idle (indicates all animations complete)
    
    Args:
        device_id: Device ID
        package_name: App package name
    
    Returns:
        (is_complete, info_dict)
    """
    try:
        adb_path = find_adb_path()
        
        # Check GPU idle status
        result = subprocess.run(
            [adb_path, "-s", device_id, "shell", "dumpsys", "gfxinfo", package_name, "idle"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return False, {"error": f"Command failed: {result.stderr}", "method": "gpu"}
        
        output = result.stdout.strip().upper()
        
        # Check for idle state
        is_idle = "IDLE" in output or "true" in output.lower()
        
        return is_idle, {
            "method": "gpu",
            "idle": is_idle,
            "output": output[:100]
        }
        
    except subprocess.TimeoutExpired:
        return False, {"error": "Command timeout", "method": "gpu"}
    except Exception as e:
        return False, {"error": str(e), "method": "gpu"}


def get_current_package(device_id: str) -> Optional[str]:
    """
    Get current foreground app package name
    
    Args:
        device_id: Device ID
    
    Returns:
        Package name or None
    """
    try:
        adb_path = find_adb_path()
        result = subprocess.run(
            [adb_path, "-s", device_id, "shell", "dumpsys", "window", "windows"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return None
        
        # Parse mCurrentFocus line
        for line in result.stdout.split('\n'):
            if "mCurrentFocus" in line:
                match = re.search(r'(\S+)/(\S+)\}', line)
                if match:
                    return match.group(1)
        
        return None
    except Exception as e:
        return None


def wait_for_animation_complete(
    device_id: str,
    package_name: Optional[str] = None,
    timeout: int = 10,
    method: str = "auto",
    check_interval: float = 0.3
) -> Tuple[bool, Dict[str, Any]]:
    """
    Wait for animation/transition to complete using ADB detection methods
    
    Args:
        device_id: Device ID
        package_name: Optional app package name (if None, will try to detect)
        timeout: Maximum wait time in seconds
        method: Detection method ("auto" | "activity" | "fps" | "gpu")
        check_interval: Interval between checks in seconds
    
    Returns:
        (success, info_dict) where info_dict contains:
            - method: Detection method used
            - duration: Time taken in seconds
            - details: Method-specific details
            - error: Error message if failed
    """
    start_time = time.time()
    info = {
        "method": method,
        "duration": 0.0,
        "details": {},
        "attempts": 0
    }
    
    # Get package name if not provided
    if not package_name:
        package_name = get_current_package(device_id)
        if package_name:
            info["detected_package"] = package_name
        else:
            info["warning"] = "Could not detect package name, some methods may not work"
    
    # Determine detection methods to try
    methods_to_try = []
    if method == "auto":
        # Priority: Activity > FPS > GPU
        if package_name:
            methods_to_try = ["activity", "fps", "gpu"]
        else:
            methods_to_try = ["fps", "gpu"]  # Activity requires package name
    else:
        methods_to_try = [method]
    
    last_check_time = start_time
    
    while (time.time() - start_time) < timeout:
        info["attempts"] += 1
        
        # Try each method in order
        for detection_method in methods_to_try:
            is_complete = False
            method_info = {}
            
            if detection_method == "activity":
                is_complete, method_info = check_activity_resumed(device_id, package_name)
            elif detection_method == "fps":
                if package_name:
                    is_complete, method_info = check_fps_stable(device_id, package_name)
                else:
                    continue  # Skip if no package name
            elif detection_method == "gpu":
                if package_name:
                    is_complete, method_info = check_gpu_idle(device_id, package_name)
                else:
                    continue  # Skip if no package name
            else:
                continue
            
            # If detection succeeded, return success
            if is_complete:
                info["method"] = detection_method
                info["details"] = method_info
                info["duration"] = time.time() - start_time
                return True, info
            
            # If this is the last method and we have time, continue checking
            if detection_method == methods_to_try[-1]:
                # Wait before next check
                elapsed = time.time() - last_check_time
                if elapsed < check_interval:
                    time.sleep(check_interval - elapsed)
                last_check_time = time.time()
        
        # If all methods failed and we're still in timeout, continue loop
        elapsed = time.time() - last_check_time
        if elapsed < check_interval:
            time.sleep(check_interval - elapsed)
        last_check_time = time.time()
    
    # Timeout
    info["duration"] = time.time() - start_time
    info["error"] = f"Timeout after {timeout}s"
    info["details"] = {"timeout": True}
    return False, info

