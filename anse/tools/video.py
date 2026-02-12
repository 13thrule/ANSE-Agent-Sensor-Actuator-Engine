"""
Video capture tool - camera access for agents.
"""
import asyncio
import os
import uuid
from typing import Dict, Any


def _blocking_capture_frame(camera_id: int, out_dir: str) -> Dict[str, Any]:
    """Blocking implementation of frame capture using OpenCV."""
    try:
        import cv2
    except ImportError:
        return {"error": "opencv-python not installed"}
    
    try:
        os.makedirs(out_dir, exist_ok=True)
        cap = cv2.VideoCapture(int(camera_id))
        
        if not cap.isOpened():
            return {"error": "camera_unavailable", "camera_id": camera_id}
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret or frame is None:
            return {"error": "capture_failed", "camera_id": camera_id}
        
        # Generate unique filename
        frame_id = uuid.uuid4().hex
        fname = f"{frame_id}.jpg"
        path = os.path.join(out_dir, fname)
        
        # Save frame
        success = cv2.imwrite(path, frame)
        
        if not success:
            return {"error": "save_failed", "path": path}
        
        # Get frame info
        height, width, channels = frame.shape
        
        return {
            "frame_id": frame_id,
            "path": path,
            "width": width,
            "height": height,
            "channels": channels,
            "camera_id": camera_id,
        }
    except Exception as e:
        return {"error": str(e), "camera_id": camera_id}


async def capture_frame(camera_id: int = 0, out_dir: str = "/tmp/anse") -> Dict[str, Any]:
    """
    Capture a single RGB frame from the specified camera.
    
    Non-blocking wrapper that runs the blocking OpenCV call in a thread pool.
    
    Args:
        camera_id: Camera device ID (default: 0)
        out_dir: Output directory for saved frames
        
    Returns:
        Dict containing frame_id and path, or error information
    """
    return await asyncio.to_thread(_blocking_capture_frame, camera_id, out_dir)


async def list_cameras() -> Dict[str, Any]:
    """
    List available camera devices.
    
    Returns:
        Dict containing list of available camera IDs
    """
    try:
        import cv2
    except ImportError:
        return {"error": "opencv-python not installed"}
    
    available_cameras = []
    
    # Test up to 10 possible camera indices
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
    
    return {"cameras": available_cameras, "count": len(available_cameras)}
