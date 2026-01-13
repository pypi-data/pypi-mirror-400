"""
AR Data Subscriber module.

Provides ARDataSubscriber class for receiving AR sensor data via ZMQ.
"""

import zmq
import numpy as np
from typing import Optional, Callable, Any, TYPE_CHECKING
from contextlib import contextmanager

if TYPE_CHECKING:
    from .data_types import ARFrame
else:
    from .data_types import ARFrame

from .proto import phone_msg_pb2


# Default configuration
DEFAULT_PORT = 8000
DEFAULT_HWM = 1
DEFAULT_TIMEOUT = 1000  # milliseconds


class ARDataSubscriber:
    """
    A subscriber for AR data streams.
    
    This class provides a simple interface to receive AR data including
    images, depth maps, poses, and other sensor readings.
    
    Example:
        >>> from asmagic import ARDataSubscriber
        >>> 
        >>> # Simple usage with context manager
        >>> with ARDataSubscriber("192.168.1.100") as subscriber:
        ...     frame = subscriber.get_frame()
        ...     if frame:
        ...         print(f"Timestamp: {frame.timestamp}")
        ...         print(f"Has color: {frame.has_color_image}")
        >>> 
        >>> # Or manual management
        >>> subscriber = ARDataSubscriber("192.168.1.100")
        >>> frame = subscriber.get_frame()
        >>> subscriber.close()
    """
    
    def __init__(
        self, 
        ip: str, 
        port: int = DEFAULT_PORT,
        hwm: int = DEFAULT_HWM, 
        conflate: bool = True,
        verbose: bool = False
    ) -> None:
        """
        Initialize the AR data subscriber.
        
        Args:
            ip: IP address of the AR device
            port: Port number (default: 8000)
            hwm: High water mark for ZMQ socket (default: 1)
            conflate: Whether to keep only the latest message (default: True)
            verbose: Print connection info (default: False)
        """
        self._ip = ip
        self._port = port
        self._address = f"tcp://{ip}:{port}"
        self._connected = False
        
        if verbose:
            print(f"[ARDataSubscriber] Connecting to {self._address}")
        
        # Create ZMQ context and socket
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.SUB)
        self._socket.set_hwm(hwm)
        self._socket.setsockopt(zmq.CONFLATE, conflate)
        self._socket.connect(self._address)
        self._socket.setsockopt_string(zmq.SUBSCRIBE, "")
        
        # Set up poller for non-blocking receives
        self._poller = zmq.Poller()
        self._poller.register(self._socket, zmq.POLLIN)
        
        # Reusable protobuf message
        self._proto_msg = phone_msg_pb2.Phone()
        self._connected = True
        
        if verbose:
            print(f"[ARDataSubscriber] Connected successfully")
    
    def __enter__(self) -> "ARDataSubscriber":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
    
    def __iter__(self) -> "ARDataSubscriber":
        """
        Make ARDataSubscriber iterable.
        
        This allows using the subscriber in for loops:
            >>> for data in subscriber:
            ...     print(data.velocity)
        """
        return self
    
    def __next__(self) -> ARFrame:
        """
        Get the next data frame (for iterator protocol).
        
        Returns:
            ARFrame object with the latest sensor data
            
        Raises:
            StopIteration: When subscriber is closed
            
        Example:
            >>> for frame in ARDataSubscriber("192.168.1.100"):
            ...     print(frame.timestamp)
            ...     if some_condition:
            ...         break
        """
        if not self._connected:
            raise StopIteration
        
        # Keep trying until we get a frame or connection is closed
        while self._connected:
            frame = self.get_frame(timeout=DEFAULT_TIMEOUT)
            if frame is not None:
                return frame
        
        raise StopIteration
    
    @property
    def is_connected(self) -> bool:
        """Check if subscriber is connected."""
        return self._connected
    
    @property
    def address(self) -> str:
        """Get the connection address."""
        return self._address
    
    def get_frame(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[ARFrame]:
        """
        Get a single frame of AR data.
        
        Args:
            timeout: Timeout in milliseconds (default: 100)
            
        Returns:
            ARFrame object containing all sensor data, or None if timeout
        """
        if not self._connected:
            return None
            
        socks = dict(self._poller.poll(timeout))
        if self._socket not in socks or socks[self._socket] != zmq.POLLIN:
            return None
        
        try:
            data = self._socket.recv(zmq.DONTWAIT)
            self._proto_msg.ParseFromString(data)
            
            return ARFrame(
                timestamp=self._proto_msg.timestamp,
                color_img=self._proto_msg.color_img,
                depth_img=self._proto_msg.depth_img,
                depth_width=self._proto_msg.depth_width,
                depth_height=self._proto_msg.depth_height,
                local_pose=np.array(self._proto_msg.local_pose, dtype=np.float32),
                global_pose=np.array(self._proto_msg.global_pose, dtype=np.float32),
                velocity=np.array(self._proto_msg.velocity, dtype=np.float32),
                camera_intrinsics=np.array(self._proto_msg.camersIntrinsics, dtype=np.float32)
            )
        except zmq.Again:
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to receive AR data: {e}")
    
    def get(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[ARFrame]:
        """
        Get the latest AR data - Recommended method!
        
        Returns a data object with properties for accessing various sensor data.
        
        Returns:
            Data object with the following properties:
            - timestamp: Unix timestamp
            - velocity: Velocity vector
            - local_pose: Local pose array
            - global_pose: Global pose array
            - camera_intrinsics: Camera intrinsic parameters
            - color_img: Color image bytes
            - depth_img: Depth image bytes
            - depth_width, depth_height: Depth image dimensions
            
            Returns None if no data available
            
        Example:
            >>> data = sub.get()
            >>> if data:
            ...     print(data.timestamp)
            ...     print(data.velocity)
            ...     print(data.local_pose)
            ...     
            ...     # Get depth image as numpy array
            ...     depth_array = data.depth
        """
        return self.get_frame(timeout)
    
    def get_all_data(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[tuple]:
        """
        Get all data at once (returns tuple, requires manual unpacking).
        
        ⚠️ Recommend using get() method instead for cleaner API!
        
        Returns:
            Tuple of (timestamp, color_img, depth_img, depth_width, depth_height,
                     local_pose, global_pose, velocity, camera_intrinsics)
            or None if no data available.
        """
        frame = self.get_frame(timeout)
        if frame is None:
            return None
        
        return (
            frame.timestamp,
            frame.color_img,
            frame.depth_img,
            frame.depth_width,
            frame.depth_height,
            frame.local_pose,
            frame.global_pose,
            frame.velocity,
            frame.camera_intrinsics
        )
    
    def get_timestamp(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[float]:
        """Get only the timestamp from the latest frame."""
        frame = self.get_frame(timeout)
        return frame.timestamp if frame else None
    
    def get_color_image(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[bytes]:
        """Get only the color image bytes from the latest frame."""
        frame = self.get_frame(timeout)
        return frame.color_img if frame and frame.has_color_image else None
    
    def get_depth_image(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[np.ndarray]:
        """
        Get the depth image as a numpy array.
        
        Returns:
            Depth image as uint16 numpy array with shape (height, width),
            or None if no data available.
        """
        frame = self.get_frame(timeout)
        return frame.depth if frame else None
    
    def get_depth_raw(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[tuple]:
        """
        Get raw depth data with dimensions.
        
        Returns:
            Tuple of (depth_bytes, width, height) or None if no data.
        """
        frame = self.get_frame(timeout)
        if frame and frame.has_depth_image:
            return (frame.depth_img, frame.depth_width, frame.depth_height)
        return None
    
    def get_local_pose(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[np.ndarray]:
        """Get the local pose array from the latest frame."""
        frame = self.get_frame(timeout)
        return frame.local_pose if frame and len(frame.local_pose) > 0 else None
    
    def get_global_pose(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[np.ndarray]:
        """Get the global pose array from the latest frame."""
        frame = self.get_frame(timeout)
        return frame.global_pose if frame and len(frame.global_pose) > 0 else None
    
    def get_velocity(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[np.ndarray]:
        """Get the velocity array from the latest frame."""
        frame = self.get_frame(timeout)
        return frame.velocity if frame and len(frame.velocity) > 0 else None
    
    def get_camera_intrinsics(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[np.ndarray]:
        """Get the camera intrinsics array from the latest frame."""
        frame = self.get_frame(timeout)
        return frame.camera_intrinsics if frame and len(frame.camera_intrinsics) > 0 else None
    
    def stream(
        self, 
        timeout: int = DEFAULT_TIMEOUT,
        on_frame: Optional[Callable[[ARFrame], Any]] = None
    ):
        """
        Generator that yields frames continuously.
        
        Args:
            timeout: Timeout for each frame in milliseconds
            on_frame: Optional callback function called for each frame
            
        Yields:
            ARFrame objects as they arrive
            
        Example:
            >>> for frame in subscriber.stream():
            ...     print(frame.timestamp)
        """
        while self._connected:
            frame = self.get_frame(timeout)
            if frame:
                if on_frame:
                    on_frame(frame)
                yield frame
    
    def close(self) -> None:
        """
        Close the subscriber connection.
        
        This method is idempotent and safe to call multiple times.
        """
        if not self._connected:
            return
            
        self._connected = False
        
        if hasattr(self, '_socket') and self._socket:
            try:
                self._socket.close()
            except:
                pass
                
        if hasattr(self, '_context') and self._context:
            try:
                self._context.term()
            except:
                pass
    
    def __del__(self):
        """Destructor to ensure resources are cleaned up."""
        self.close()


# Convenience function for quick access
@contextmanager
def connect(ip: str, port: int = DEFAULT_PORT, **kwargs):
    """
    Context manager for quick AR data access.
    
    Example:
        >>> from asmagic import connect
        >>> with connect("192.168.1.100") as sub:
        ...     frame = sub.get_frame()
    """
    subscriber = ARDataSubscriber(ip, port, **kwargs)
    try:
        yield subscriber
    finally:
        subscriber.close()

