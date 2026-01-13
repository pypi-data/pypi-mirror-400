"""
IMU Data Subscriber for receiving iPhone IMU sensor data.

This module provides the IMUDataSubscriber class for subscribing to IMU data streams
from iPhone devices via ZeroMQ.
"""

import zmq
import numpy as np
from typing import Optional
from .proto import imu_msg_pb2
from .data_types import IMUFrame

# Default configuration
DEFAULT_PORT = 8002
DEFAULT_HWM = 1
DEFAULT_CONFLATE = True
DEFAULT_TIMEOUT = 1000  # milliseconds


class IMUDataSubscriber:
    """
    Subscribe to IMU sensor data stream from iPhone.
    
    Simple and Pythonic API for receiving IMU data including accelerometer,
    gyroscope, magnetometer, gravity, user acceleration, and attitude.
    
    Example - Basic usage:
        >>> sub = IMUDataSubscriber("192.168.1.100")
        >>> data = sub.get()
        >>> if data:
        ...     print(data.accelerometer)
        ...     print(data.gyroscope)
        >>> sub.close()
    
    Example - Continuous streaming:
        >>> sub = IMUDataSubscriber("192.168.1.100")
        >>> for data in sub:
        ...     print(f"Accel: {data.accelerometer}")
        ...     print(f"Gyro: {data.gyroscope}")
    
    Example - Context manager:
        >>> with IMUDataSubscriber("192.168.1.100") as sub:
        ...     for data in sub:
        ...         print(data.attitude)
    """
    
    def __init__(
        self,
        ip: str,
        port: int = DEFAULT_PORT,
        hwm: int = DEFAULT_HWM,
        conflate: bool = DEFAULT_CONFLATE,
        verbose: bool = False,
    ) -> None:
        """
        Initialize IMU data subscriber.
        
        Args:
            ip: iPhone's IP address
            port: Port number (default: 8002)
            hwm: High water mark - number of messages to buffer (default: 1)
            conflate: Keep only latest message when buffer full (default: True)
            verbose: Print connection info (default: False)
        """
        self._ip = ip
        self._port = port
        self._hwm = hwm
        self._conflate = conflate
        self._verbose = verbose
        self._connected = False
        
        # Initialize ZMQ
        self._context = zmq.Context()
        self._subscriber = self._context.socket(zmq.SUB)
        self._subscriber.set_hwm(hwm)
        self._subscriber.setsockopt(zmq.CONFLATE, conflate)
        
        # Connect
        address = f"tcp://{ip}:{port}"
        self._subscriber.connect(address)
        self._subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        
        # Setup poller
        self._poller = zmq.Poller()
        self._poller.register(self._subscriber, zmq.POLLIN)
        
        self._connected = True
        
        if verbose:
            print(f"IMU Subscriber connected to {address}")
    
    @property
    def ip(self) -> str:
        """Get the IP address"""
        return self._ip
    
    @property
    def port(self) -> int:
        """Get the port number"""
        return self._port
    
    @property
    def is_connected(self) -> bool:
        """Check if subscriber is connected"""
        return self._connected
    
    def get_frame(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[IMUFrame]:
        """
        Get a single IMU data frame.
        
        Args:
            timeout: Maximum time to wait in milliseconds (default: 1000)
        
        Returns:
            IMUFrame object containing all sensor data, or None if timeout
        """
        if not self._connected:
            return None
        
        # Poll for messages
        socks = dict(self._poller.poll(timeout))
        
        if self._subscriber not in socks or socks[self._subscriber] != zmq.POLLIN:
            return None
        
        try:
            # Receive protobuf message
            msg_bytes = self._subscriber.recv(zmq.DONTWAIT)
            
            # Parse protobuf
            imu_msg = imu_msg_pb2.Imu()
            imu_msg.ParseFromString(msg_bytes)
            
            # Extract data into numpy arrays
            accelerometer = np.array([
                imu_msg.accelerometer.x,
                imu_msg.accelerometer.y,
                imu_msg.accelerometer.z
            ], dtype=np.float32)
            
            gyroscope = np.array([
                imu_msg.gyroscope.x,
                imu_msg.gyroscope.y,
                imu_msg.gyroscope.z
            ], dtype=np.float32)
            
            magnetometer = np.array([
                imu_msg.magnetometer.x,
                imu_msg.magnetometer.y,
                imu_msg.magnetometer.z
            ], dtype=np.float32)
            
            gravity = np.array([
                imu_msg.gravity.x,
                imu_msg.gravity.y,
                imu_msg.gravity.z
            ], dtype=np.float32)
            
            user_acceleration = np.array([
                imu_msg.user_acceleration.x,
                imu_msg.user_acceleration.y,
                imu_msg.user_acceleration.z
            ], dtype=np.float32)
            
            attitude = np.array([
                imu_msg.attitude.x,
                imu_msg.attitude.y,
                imu_msg.attitude.z,
                imu_msg.attitude.w
            ], dtype=np.float32)
            
            # Create IMUFrame
            return IMUFrame(
                timestamp=imu_msg.timestamp,
                accelerometer=accelerometer,
                gyroscope=gyroscope,
                magnetometer=magnetometer,
                gravity=gravity,
                user_acceleration=user_acceleration,
                attitude=attitude,
            )
            
        except zmq.Again:
            return None
        except Exception as e:
            if self._verbose:
                print(f"Error receiving IMU data: {e}")
            return None
    
    def get(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[IMUFrame]:
        """
        Get the latest IMU data frame.
        This is the recommended method for single-frame access.
        
        Args:
            timeout: Maximum time to wait in milliseconds (default: 1000)
        
        Returns:
            IMUFrame object or None if timeout
        """
        return self.get_frame(timeout)
    
    def get_timestamp(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[float]:
        """Get only the timestamp"""
        frame = self.get_frame(timeout)
        return frame.timestamp if frame else None
    
    def get_accelerometer(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[np.ndarray]:
        """Get only the accelerometer data"""
        frame = self.get_frame(timeout)
        return frame.accelerometer if frame else None
    
    def get_gyroscope(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[np.ndarray]:
        """Get only the gyroscope data"""
        frame = self.get_frame(timeout)
        return frame.gyroscope if frame else None
    
    def get_magnetometer(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[np.ndarray]:
        """Get only the magnetometer data"""
        frame = self.get_frame(timeout)
        return frame.magnetometer if frame else None
    
    def get_gravity(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[np.ndarray]:
        """Get only the gravity vector"""
        frame = self.get_frame(timeout)
        return frame.gravity if frame else None
    
    def get_user_acceleration(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[np.ndarray]:
        """Get only the user acceleration"""
        frame = self.get_frame(timeout)
        return frame.user_acceleration if frame else None
    
    def get_attitude(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[np.ndarray]:
        """Get only the attitude quaternion"""
        frame = self.get_frame(timeout)
        return frame.attitude if frame else None
    
    def __iter__(self) -> "IMUDataSubscriber":
        """Make the subscriber iterable for continuous data streaming"""
        return self
    
    def __next__(self) -> IMUFrame:
        """
        Get the next available IMUFrame.
        Blocks until a frame is available or connection is closed.
        """
        if not self._connected:
            raise StopIteration
        
        # Keep trying until we get a frame or connection is closed
        while self._connected:
            frame = self.get_frame(timeout=DEFAULT_TIMEOUT)
            if frame is not None:
                return frame
        
        raise StopIteration
    
    def __enter__(self) -> "IMUDataSubscriber":
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - auto cleanup"""
        self.close()
    
    def close(self) -> None:
        """Close the subscriber connection and cleanup resources"""
        if self._connected:
            self._connected = False
            
            if hasattr(self, "_subscriber") and self._subscriber:
                self._subscriber.close()
            
            if hasattr(self, "_context") and self._context:
                self._context.term()
            
            if self._verbose:
                print("IMU Subscriber closed")
    
    def __del__(self):
        """Destructor - ensure cleanup"""
        self.close()

