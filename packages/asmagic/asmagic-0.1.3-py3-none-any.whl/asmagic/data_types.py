"""
Data types for AR and IMU data subscription.

This module defines the data structures returned by ARDataSubscriber and IMUDataSubscriber.
Easy to extend and maintain when new data types are added.
"""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np


_cv2 = None
_Image = None
_io = None

def _ensure_image_libs():
    """Ensure image processing libraries are imported"""
    global _cv2, _Image, _io
    if _cv2 is None:
        try:
            import cv2
            _cv2 = cv2
        except ImportError:
            raise ImportError("opencv-python is required for image display: pip install opencv-python")
    
    if _Image is None:
        try:
            from PIL import Image
            import io
            _Image = Image
            _io = io
        except ImportError:
            raise ImportError("Pillow is required for image processing: pip install Pillow")


@dataclass
class ARFrame:
    """
    A single frame of AR data containing all sensor readings.
    
    Attributes:
        timestamp: Unix timestamp of the frame
        color_img: Raw bytes of the color image (JPEG/PNG encoded)
        depth_img: Raw bytes of the depth image (uint16 format)
        depth_width: Width of the depth image in pixels
        depth_height: Height of the depth image in pixels
        local_pose: 4x4 local transformation matrix as numpy array
        global_pose: 4x4 global transformation matrix as numpy array
        velocity: Velocity vector as numpy array
        camera_intrinsics: Camera intrinsic parameters as numpy array
    """
    timestamp: float = 0.0
    color_img: bytes = b""
    depth_img: bytes = b""
    depth_width: int = 0
    depth_height: int = 0
    local_pose: np.ndarray = field(default_factory=lambda: np.array([]))
    global_pose: np.ndarray = field(default_factory=lambda: np.array([]))
    velocity: np.ndarray = field(default_factory=lambda: np.array([]))
    camera_intrinsics: np.ndarray = field(default_factory=lambda: np.array([]))
    
    @property
    def has_color_image(self) -> bool:
        """Check if color image data is available."""
        return len(self.color_img) > 0
    
    @property
    def has_depth_image(self) -> bool:
        """Check if depth image data is available."""
        return len(self.depth_img) > 0 and self.depth_width > 0 and self.depth_height > 0
    
    @property
    def has_pose(self) -> bool:
        """Check if pose data is available."""
        return len(self.local_pose) > 0 or len(self.global_pose) > 0
    
    # ========================================
    # Depth Image Access (array only)
    # ========================================
    
    @property
    def depth_array(self) -> Optional[np.ndarray]:
        """
        Get depth image as numpy array.
        
        Returns:
            Depth image as uint16 numpy array with shape (height, width),
            or None if no depth data available.
            
        Example:
            >>> depth = data.depth_array
            >>> if depth is not None:
            ...     print(depth.shape, depth.dtype)
        """
        if not self.has_depth_image:
            return None
        depth_array = np.frombuffer(self.depth_img, dtype=np.uint16)
        return depth_array.reshape(self.depth_height, self.depth_width)
    
    @property
    def depth(self) -> Optional[np.ndarray]:
        """Shortcut for depth_array. Returns depth image as numpy array."""
        return self.depth_array
    
    # ========================================
    # Color Image Access (bytes and array)
    # ========================================
    
    @property
    def color_bytes(self) -> bytes:
        """
        Get raw color image bytes (JPEG encoded).
        
        Returns:
            Raw JPEG image bytes as received from device.
            
        Example:
            >>> color_bytes = data.color_bytes
            >>> # Save directly to file
            >>> with open("image.jpg", "wb") as f:
            ...     f.write(color_bytes)
        """
        return self.color_img
    
    @property
    def color_array(self) -> Optional[np.ndarray]:
        """
        Get color image as numpy array (RGB format).
        
        Returns:
            Color image as numpy array with shape (height, width, 3),
            or None if no color data available.
            
        Example:
            >>> color = data.color_array
            >>> if color is not None:
            ...     print(color.shape, color.dtype)
            ...     # Use with OpenCV
            ...     import cv2
            ...     cv2.imshow("Color", cv2.cvtColor(color, cv2.COLOR_RGB2BGR))
        """
        if not self.has_color_image:
            return None
        
        # Import PIL if not already
        global _Image, _io
        if _Image is None:
            try:
                from PIL import Image
                import io
                _Image = Image
                _io = io
            except ImportError:
                print("Warning: Pillow is required for color image processing")
                return None
        
        try:
            pil_image = _Image.open(_io.BytesIO(self.color_img))
            return np.array(pil_image)
        except Exception as e:
            print(f"Error converting color image: {e}")
            return None
    
    # ========================================
    # Convenient shortcuts (aliases)
    # ========================================
    
    @property
    def color(self) -> Optional[np.ndarray]:
        """Shortcut for color_array. Returns color image as numpy array."""
        return self.color_array
    
    def get_local_pose_matrix(self) -> Optional[np.ndarray]:
        """
        Get local pose as 4x4 transformation matrix.
        
        Returns:
            4x4 numpy array or None if pose data is insufficient.
        """
        if len(self.local_pose) == 16:
            return self.local_pose.reshape(4, 4)
        return None
    
    def get_global_pose_matrix(self) -> Optional[np.ndarray]:
        """
        Get global pose as 4x4 transformation matrix.
        
        Returns:
            4x4 numpy array or None if pose data is insufficient.
        """
        if len(self.global_pose) == 16:
            return self.global_pose.reshape(4, 4)
        return None
    
    def show_color(self, window_name: str = "Color Image") -> bool:
        """
        Display color image if available.
        
        Args:
            window_name: OpenCV window name, default "Color Image"
            
        Returns:
            True if displayed successfully, False if no image data
            
        Example:
            >>> data = sub.get()
            >>> if data:
            ...     data.show_color()
            ...     cv2.waitKey(1)
        """
        if not self.has_color_image:
            return False
        
        _ensure_image_libs()
        
        try:
            # Convert bytes to PIL image
            pil_image = _Image.open(_io.BytesIO(self.color_img))
            color_array = np.array(pil_image)
            
            # Convert color format from RGB to BGR (OpenCV format)
            if len(color_array.shape) == 3 and color_array.shape[2] == 3:
                color_bgr = _cv2.cvtColor(color_array, _cv2.COLOR_RGB2BGR)
            else:
                color_bgr = color_array
            
            # Display image
            _cv2.imshow(window_name, color_bgr)
            return True
        except Exception as e:
            print(f"Error displaying color image: {e}")
            return False
    
    def show_depth(self, window_name: str = "Depth Image", colormap: int = None) -> bool:
        """
        Display depth image if available, with automatic normalization and colormap.
        
        Args:
            window_name: OpenCV window name, default "Depth Image"
            colormap: OpenCV colormap, default cv2.COLORMAP_JET
                     Options: COLORMAP_JET, COLORMAP_HOT, COLORMAP_VIRIDIS, etc.
            
        Returns:
            True if displayed successfully, False if no depth data
            
        Example:
            >>> data = sub.get()
            >>> if data:
            ...     data.show_depth()
            ...     cv2.waitKey(1)
        """
        if not self.has_depth_image:
            return False
        
        _ensure_image_libs()
        
        try:
            # Get depth array
            depth_array = self.depth
            if depth_array is None:
                return False
            
            # Normalize to 0-255
            if depth_array.max() > depth_array.min():
                depth_normalized = ((depth_array - depth_array.min()) / 
                                   (depth_array.max() - depth_array.min()) * 255).astype(np.uint8)
            else:
                depth_normalized = np.zeros(depth_array.shape, dtype=np.uint8)
            
            # Apply colormap
            if colormap is None:
                colormap = _cv2.COLORMAP_JET
            depth_colored = _cv2.applyColorMap(depth_normalized, colormap)
            
            # Display image
            _cv2.imshow(window_name, depth_colored)
            return True
        except Exception as e:
            print(f"Error displaying depth image: {e}")
            return False
    
    def show_images(self, 
                    show_color: bool = True, 
                    show_depth: bool = True,
                    color_window: str = "Color Image",
                    depth_window: str = "Depth Image") -> tuple:
        """
        Display both color and depth images.
        
        Args:
            show_color: Whether to show color image, default True
            show_depth: Whether to show depth image, default True
            color_window: Color image window name
            depth_window: Depth image window name
            
        Returns:
            (color_shown, depth_shown) - Two booleans indicating display success
            
        Example:
            >>> data = sub.get()
            >>> if data:
            ...     data.show_images()
            ...     cv2.waitKey(1)
            
            >>> # Show only depth
            >>> data.show_images(show_color=False, show_depth=True)
        """
        color_shown = False
        depth_shown = False
        
        if show_color:
            color_shown = self.show_color(color_window)
        
        if show_depth:
            depth_shown = self.show_depth(depth_window)
        
        return (color_shown, depth_shown)


@dataclass
class IMUFrame:
    """
    A single frame of IMU data containing all sensor readings.
    
    Attributes:
        timestamp: Unix timestamp of the frame
        accelerometer: 3-axis accelerometer data [x, y, z] in G
        gyroscope: 3-axis gyroscope data [x, y, z] in rad/s
        magnetometer: 3-axis magnetometer data [x, y, z] in μT
        gravity: 3-axis gravity vector [x, y, z] in G
        user_acceleration: 3-axis user acceleration [x, y, z] in G
        attitude: Device attitude as quaternion [x, y, z, w]
    """
    timestamp: float = 0.0
    accelerometer: np.ndarray = field(default_factory=lambda: np.array([]))
    gyroscope: np.ndarray = field(default_factory=lambda: np.array([]))
    magnetometer: np.ndarray = field(default_factory=lambda: np.array([]))
    gravity: np.ndarray = field(default_factory=lambda: np.array([]))
    user_acceleration: np.ndarray = field(default_factory=lambda: np.array([]))
    attitude: np.ndarray = field(default_factory=lambda: np.array([]))
    
    @property
    def has_accelerometer(self) -> bool:
        """Check if accelerometer data is available"""
        return len(self.accelerometer) > 0
    
    @property
    def has_gyroscope(self) -> bool:
        """Check if gyroscope data is available"""
        return len(self.gyroscope) > 0
    
    @property
    def has_magnetometer(self) -> bool:
        """Check if magnetometer data is available"""
        return len(self.magnetometer) > 0
    
    @property
    def has_gravity(self) -> bool:
        """Check if gravity data is available"""
        return len(self.gravity) > 0
    
    @property
    def has_user_acceleration(self) -> bool:
        """Check if user acceleration data is available"""
        return len(self.user_acceleration) > 0
    
    @property
    def has_attitude(self) -> bool:
        """Check if attitude data is available"""
        return len(self.attitude) > 0

