# asmagic

> A Python library for receiving data streams from asMagic iOS App.

Working with asMagic App:

<a href="https://apps.apple.com/cn/app/asmagic/id6661033548">
  <img src="https://tools.applemediaservices.com/api/badges/download-on-the-app-store/black/en-us?size=250x83" alt="Download on the App Store" height="40">
</a>

## Table of Contents

-   [Features](#features)
-   [Install](#install)
-   [Quick Start](#quick-start)
    -   [AR Data](#ar-data)
    -   [IMU Data](#imu-data)
-   [Usage Examples](#usage-examples)
    -   [AR Data Examples](#ar-data-examples)
    -   [IMU Data Examples](#imu-data-examples)
-   [Data Format Reference](#data-format-reference)
    -   [AR Data](#ar-data-1)
    -   [IMU Data](#imu-data-1)
-   [API Reference](#api-reference)
    -   [ARDataSubscriber](#ardatasubscriber)
    -   [IMUDataSubscriber](#imudatasubscriber)

## Features

### AR Data Streaming

-   6DOF camera pose (position + orientation)
-   RGB camera images
-   Depth maps
-   Camera intrinsics
-   Device velocity

### IMU Data Streaming

-   Accelerometer (3-axis)
-   Gyroscope (3-axis)
-   Magnetometer (3-axis)
-   Gravity vector
-   User acceleration
-   Device attitude (quaternion)

## Install

```bash
pip install asmagic
```

## Quick Start

### AR Data

```python
from asmagic import ARDataSubscriber

# Create subscriber with your iPhone's IP address
sub = ARDataSubscriber("192.168.1.100")

try:
    # Continuous data streaming
    for data in sub:
        # All sensor data in one frame
        print(f"Timestamp: {data.timestamp}")
        print(f"Velocity: {data.velocity}")
        print(f"Local Pose: {data.local_pose}")
        print(f"Global Pose: {data.global_pose}")
        print(f"Camera Intrinsics: {data.camera_intrinsics}")

        # Access image data
        if data.has_color_image:
            # Color: bytes(jpeg format) or array
            color_bytes = data.color_bytes
            color_array = data.color_array  # or shortcut: data.color
            print(f"Color: {len(color_bytes)} bytes, array shape: {color_array.shape}")

        if data.has_depth_image:
            # Depth: Numpy array
            depth = data.depth_array  # or shortcut: data.depth
            print(f"Depth: {depth.shape}")

except KeyboardInterrupt:
    print("\nStopped by user")
finally:
    sub.close()
```

### IMU Data

```python
from asmagic import IMUDataSubscriber

# Create IMU subscriber (port 8002 is fixed)
sub = IMUDataSubscriber("192.168.1.100")

try:
    # Continuous IMU data streaming
    for data in sub:
        print(f"Timestamp: {data.timestamp}")
        print(f"Accelerometer (G): {data.accelerometer}")
        print(f"Gyroscope (rad/s): {data.gyroscope}")
        print(f"Magnetometer (μT): {data.magnetometer}")
        print(f"Gravity (G): {data.gravity}")
        print(f"User Acceleration (G): {data.user_acceleration}")
        print(f"Attitude (quat): {data.attitude}")

except KeyboardInterrupt:
    print("\nStopped by user")
finally:
    sub.close()
```

## Usage Examples

### AR Data Examples

> **Note**: Example 1 and Example 2 achieve the same goal of continuous data reading.

#### Example 1: Continuous AR Data Reading

```python
from asmagic import ARDataSubscriber

# Connect to iPhone
sub = ARDataSubscriber("192.168.1.100")

try:
    for data in sub:
        # Print all available data
        print(f"\n--- Frame at {data.timestamp} ---")
        print(f"Velocity: {data.velocity}")
        print(f"Local Pose: {data.local_pose}")
        print(f"Global Pose: {data.global_pose}")
        print(f"Camera Intrinsics: {data.camera_intrinsics}")

        if data.has_depth_image:
            depth = data.depth  # or data.depth_array
            print(f"Depth shape: {depth.shape}, min: {depth.min()}, max: {depth.max()}")

except KeyboardInterrupt:
    print("\nStopped")
finally:
    sub.close()
```

#### Example 2: Continuous Reading with `get()`

```python
from asmagic import ARDataSubscriber

sub = ARDataSubscriber("192.168.1.100")

try:
    while True:
        data = sub.get()
        if data:
            print(f"Timestamp: {data.timestamp}")
            print(f"Velocity: {data.velocity}")
            print(f"Local Pose: {data.local_pose}")
            print(f"Global Pose: {data.global_pose}")
            print(f"Camera Intrinsics: {data.camera_intrinsics}")

            # Access images
            if data.has_color_image:
                print(f"Color bytes: {len(data.color_bytes)} bytes")
                print(f"Color array: {data.color_array.shape}")

            if data.has_depth_image:
                print(f"Depth array: {data.depth_array.shape}")

except KeyboardInterrupt:
    print("\nStopped")
finally:
    sub.close()
```

#### Example 3: Display Color and Depth Images

```python
from asmagic import ARDataSubscriber
import cv2

# Connect to iPhone
sub = ARDataSubscriber("192.168.1.100")

try:
    for data in sub:
        # Display both images side by side
        data.show_images()

        # Or display individually:
        # data.show_color()  # RGB image
        # data.show_depth()  # Depth map with colormap

        # Press ESC to exit
        if cv2.waitKey(1) == 27:
            break

except KeyboardInterrupt:
    print("\nStopped")
finally:
    sub.close()
    cv2.destroyAllWindows()
```

#### Example 4: Process Image Data

```python
from asmagic import ARDataSubscriber
import numpy as np

sub = ARDataSubscriber("192.168.1.100")

try:
    for data in sub:

        # Color image: process as numpy array
        if data.has_color_image:
            color = data.color_array  # RGB numpy array
            print(f"Color shape: {color.shape}")

        # Depth image: always as numpy array
        if data.has_depth_image:
            depth = data.depth_array  # uint16 numpy array
            depth_meters = depth.astype(np.float32) / 10000.0
            print(f"Depth range: {depth_meters.min():.2f}m - {depth_meters.max():.2f}m")

except KeyboardInterrupt:
    pass
finally:
    sub.close()
```

#### Example 5: Using Pose Data

```python
from asmagic import ARDataSubscriber
import numpy as np

sub = ARDataSubscriber("192.168.1.100")

try:
    for data in sub:
        # Extract position from pose (first 3 elements)
        position = data.local_pose[:3] # [tx, ty, tz]

        # Extract quaternion from pose (last 4 elements)
        quaternion = data.local_pose[3:]  # [qx, qy, qz, qw]

        print(f"Position (m): x={position[0]:.3f}, y={position[1]:.3f}, z={position[2]:.3f}")
        print(f"Quaternion: {quaternion}")
        print(f"Velocity (m/s): {data.velocity}")   # [vx, vy, vz]

except KeyboardInterrupt:
    pass
finally:
    sub.close()
```

#### Example 6: Get Individual AR Data Fields

```python
from asmagic import ARDataSubscriber
import numpy as np

sub = ARDataSubscriber("192.168.1.100")

try:
    while True:
        # Get only specific data fields
        timestamp = sub.get_timestamp()
        print(f"Timestamp: {timestamp}")

except KeyboardInterrupt:
    print("\nStopped")
finally:
    sub.close()
```

> **Note**: Use `get_*()` methods when you need specific data fields. This is more efficient than receiving the full frame.

### IMU Data Examples

> **Note**: Example 7 and Example 8 achieve the same goal of continuous data reading.

#### Example 7: Continuous IMU Data Reading

```python
from asmagic import IMUDataSubscriber

sub = IMUDataSubscriber("192.168.1.100")

try:
    for data in sub:
        print(f"\n--- IMU Frame at {data.timestamp} ---")
        print(f"Accelerometer (G): {data.accelerometer}")
        print(f"Gyroscope (rad/s): {data.gyroscope}")
        print(f"Magnetometer (μT): {data.magnetometer}")
        print(f"Gravity (G): {data.gravity}")
        print(f"User Acceleration (G): {data.user_acceleration}")
        print(f"Attitude (quat): {data.attitude}")

except KeyboardInterrupt:
    print("\nStopped")
finally:
    sub.close()
```

#### Example 8: Continuous Reading with `get()`

```python
from asmagic import IMUDataSubscriber

sub = IMUDataSubscriber("192.168.1.100")

try:
    while True:
        data = sub.get()
        if data:
            print(f"\n--- IMU Frame at {data.timestamp} ---")
            print(f"Accelerometer (G): {data.accelerometer}")
            print(f"Gyroscope (rad/s): {data.gyroscope}")
            print(f"Magnetometer (μT): {data.magnetometer}")
            print(f"Gravity (G): {data.gravity}")
            print(f"User Acceleration (G): {data.user_acceleration}")
            print(f"Attitude (quat): {data.attitude}")

except KeyboardInterrupt:
    print("\nStopped")
finally:
    sub.close()
```

#### Example 9: Get Individual IMU Data Fields

```python
from asmagic import IMUDataSubscriber
import numpy as np

sub = IMUDataSubscriber("192.168.1.100")

try:
    while True:
        # Get only specific IMU fields
        accel = sub.get_accelerometer()
        gyro = sub.get_gyroscope()

        if accel is not None and gyro is not None:
            # Calculate magnitudes
            accel_mag = np.linalg.norm(accel)
            gyro_mag = np.linalg.norm(gyro)

            print(f"Accel: {accel}, |a| = {accel_mag:.3f} G")
            print(f"Gyro: {gyro}, |ω| = {gyro_mag:.3f} rad/s")

except KeyboardInterrupt:
    print("\nStopped")
finally:
    sub.close()
```

> **Note**: Use `get_*()` methods when you need specific data fields. This is more efficient than receiving the full frame.

## Data Format Reference

### AR Data

#### Coordinate System

**Pose Format**: $[t_x, t_y, t_z, q_x, q_y, q_z, q_w]$

-   **Translation** (first 3 values): Position in meters
    -   $t_x, t_y, t_z$: X, Y, Z coordinates
-   **Rotation** (last 4 values): Orientation as quaternion
    -   $q_x, q_y, q_z$: Imaginary part
    -   $q_w$: Real part
    -   Normalized: $q_x^2 + q_y^2 + q_z^2 + q_w^2 = 1$

**Coordinate Frame**:

-   **X-axis**: Right
-   **Y-axis**: Up
-   **Z-axis**: Forward

**Difference between local_pose and global_pose**:

-   `local_pose`: Position relative to device starting point
-   `global_pose`: Position in shared world coordinate (when multiple devices collaborate)

> **Note**: When using a single device, `local_pose` and `global_pose` are identical

#### Velocity

**Format**: $[v_x, v_y, v_z]$

-   Calculated as: $\vec{v} = \frac{\Delta \vec{p}}{\Delta t}$
-   Unit: meters per second (m/s)
-   In the same coordinate frame as pose

#### Camera Intrinsics

**Format**: $[f_x, 0, 0, 0, f_y, 0, c_x, c_y, 1]$

Represents 3×3 matrix:

$$
K = \begin{bmatrix}
f_x & 0 & c_x \\
0 & f_y & c_y \\
0 & 0 & 1
\end{bmatrix}
$$

Where:

-   $f_x, f_y$: Focal length in pixels
-   $c_x, c_y$: Principal point (optical center) in pixels

#### Depth Image

-   **Format**: 16-bit unsigned integer (uint16)
-   **Unit**: $10^{-4}$ m (0.1 mm, scaled by 10000 from meters)
-   **Conversion to meters**: $d_{meters} = \frac{d_{raw}}{10000}$
-   **Range**: $0 \leq d_{raw} \leq 65535$ → $0$ to $6.5535$ m
-   **Access**: Use `data.depth` or `data.depth_array` to get numpy array

#### Image Data Format

**Color Image**: Two formats available

-   `color_bytes`: JPEG compressed bytes
-   `color_array`: RGB numpy array (640×480×3)
-   `color`: Shortcut for `color_array`

**Depth Image**: Numpy array **only**

-   `depth_array`: uint16 numpy array (256×192)
-   `depth`: Shortcut for `depth_array`

### IMU Data

For detailed field descriptions, see [IMUFrame Properties](#imuframe) in API Reference.

#### IMU Coordinate System

**Coordinate Frame** (iPhone device frame):

-   **X-axis**: Right (when holding phone in portrait)
-   **Y-axis**: Up (toward top of device)
-   **Z-axis**: Forward (out of screen)

![iPhone Coordinate System](https://docs-assets.developer.apple.com/published/64b92fc751671c47e15435b373ffc1bf/media-4251993@2x.png)

#### IMU Data Explained

The IMU data follows Apple's CoreMotion framework conventions. For comprehensive details, refer to [Apple's CoreMotion Documentation](https://developer.apple.com/documentation/coremotion/getting-processed-device-motion-data).

**1. Accelerometer**

Total acceleration measured by the device's accelerometer hardware.

-   **Unit**: G (gravitational force units, where $1G = 9.81 \text{ m/s}^2$)

**2. Gyroscope**

Angular velocity around each axis.

-   **Unit**: rad/s (radians per second)

**3. Magnetometer**

Magnetic field strength detected by the device.

-   **Unit**: μT (microteslas)

**4. Gravity Vector**

Component of acceleration due to Earth's gravitational pull, isolated from user motion.

-   **Unit**: G (gravitational force units)
-   **Magnitude**: $\|\vec{g}\| \approx 1.0G$ when stationary
-   **Usage**: Determining device orientation relative to Earth
-   **Reference**: [CMDeviceMotion.gravity](https://developer.apple.com/documentation/coremotion/cmdevicemotion/1616164-gravity)

**5. User Acceleration**

Acceleration from user motion, with gravity removed.

-   **Unit**: G (gravitational force units)
-   **Formula**: $\vec{a}_{user} = \vec{a}_{total} - \vec{g}$
-   **Reference**: [CMDeviceMotion.userAcceleration](https://developer.apple.com/documentation/coremotion/cmdevicemotion/1616147-useracceleration)

**6. Attitude (Quaternion)**

Device orientation in 3D space.

-   **Format**: $[q_x, q_y, q_z, q_w]$ (quaternion)
-   **Normalized**: $q_x^2 + q_y^2 + q_z^2 + q_w^2 = 1$
-   **Reference**: [CMAttitude](https://developer.apple.com/documentation/coremotion/cmattitude)

## API Reference

### ARDataSubscriber

**Constructor:**

```python
ARDataSubscriber(ip, port=8000, hwm=1, conflate=True, verbose=False)
```

**Parameters:**

-   `ip` (str): iPhone's IP address
-   `port` (int): Port number (default: 8000)
-   `hwm` (int): High water mark (default: 1, keeps only latest message)
-   `conflate` (bool): Message conflation (default: True)
-   `verbose` (bool): Print connection info (default: False)

**Usage:**

```python
# Create subscriber
sub = ARDataSubscriber("192.168.1.100")

# Continuously receive data
for data in sub:
    print(data.timestamp)
    print(data.velocity)

# Close when done
sub.close()
```

**Main Methods:**

| Method                    | Returns                | Description                |
| ------------------------- | ---------------------- | -------------------------- |
| `get()`                   | `ARFrame` or `None`    | Get latest data frame      |
| `get_timestamp()`         | `float` or `None`      | Get timestamp only         |
| `get_velocity()`          | `np.ndarray` or `None` | Get velocity only          |
| `get_local_pose()`        | `np.ndarray` or `None` | Get local pose only        |
| `get_global_pose()`       | `np.ndarray` or `None` | Get global pose only       |
| `get_camera_intrinsics()` | `np.ndarray` or `None` | Get camera intrinsics only |
| `get_color_image()`       | `bytes` or `None`      | Get color image bytes only |
| `get_depth_image()`       | `np.ndarray` or `None` | Get depth array only       |
| `close()`                 | `None`                 | Close connection           |

**Note**:

-   The subscriber is iterable, so you can use `for data in sub:` to receive frames continuously.
-   All `get_*()` methods accept an optional `timeout` parameter (default: 1000ms).

### ARFrame

Data object returned by `get()` or when iterating. For data format details, see [AR Data Format Reference](#ar-data) above.

**Properties:**

| Property            | Type         | Description                                       |
| ------------------- | ------------ | ------------------------------------------------- |
| `timestamp`         | `float`      | Unix timestamp in seconds                         |
| `velocity`          | `np.ndarray` | Velocity $[v_x, v_y, v_z]$ in m/s                 |
| `local_pose`        | `np.ndarray` | Local pose $[t_x, t_y, t_z, q_x, q_y, q_z, q_w]$  |
| `global_pose`       | `np.ndarray` | Global pose $[t_x, t_y, t_z, q_x, q_y, q_z, q_w]$ |
| `camera_intrinsics` | `np.ndarray` | Camera intrinsics (3×3 flattened)                 |
| **Color Image**     |              |                                                   |
| `color_bytes`       | `bytes`      | JPEG image bytes (for saving/forwarding)          |
| `color_array`       | `np.ndarray` | Decoded RGB image array (H×W×3)                   |
| `color`             | `np.ndarray` | Shortcut for `color_array`                        |
| **Depth Image**     |              |                                                   |
| `depth_array`       | `np.ndarray` | Depth image array (uint16, H×W)                   |
| `depth`             | `np.ndarray` | Shortcut for `depth_array`                        |
| `depth_width`       | `int`        | Depth image width                                 |
| `depth_height`      | `int`        | Depth image height                                |
| **Helpers**         |              |                                                   |
| `has_color_image`   | `bool`       | Check if color image exists                       |
| `has_depth_image`   | `bool`       | Check if depth image exists                       |

**Methods:**

| Method                                | Returns | Description                       |
| ------------------------------------- | ------- | --------------------------------- |
| `show_color(window_name)`             | `bool`  | Display color image with OpenCV   |
| `show_depth(window_name, colormap)`   | `bool`  | Display depth image with colormap |
| `show_images(show_color, show_depth)` | `tuple` | Display both images side by side  |

### IMUDataSubscriber

**Constructor:**

```python
IMUDataSubscriber(ip, port=8002, hwm=1, conflate=True, verbose=False)
```

**Parameters:**

-   `ip` (str): iPhone's IP address
-   `port` (int): Port number (default: 8002, fixed for IMU data)
-   `hwm` (int): High water mark (default: 1, keeps only latest message)
-   `conflate` (bool): Message conflation (default: True)
-   `verbose` (bool): Print connection info (default: False)

**Usage:**

```python
# Create IMU subscriber
sub = IMUDataSubscriber("192.168.1.100")

# Continuously receive IMU data
for data in sub:
    print(data.accelerometer)
    print(data.gyroscope)

# Close when done
sub.close()
```

**Main Methods:**

| Method                    | Returns                | Description                  |
| ------------------------- | ---------------------- | ---------------------------- |
| `get()`                   | `IMUFrame` or `None`   | Get latest IMU data frame    |
| `get_timestamp()`         | `float` or `None`      | Get timestamp only           |
| `get_accelerometer()`     | `np.ndarray` or `None` | Get accelerometer only       |
| `get_gyroscope()`         | `np.ndarray` or `None` | Get gyroscope only           |
| `get_magnetometer()`      | `np.ndarray` or `None` | Get magnetometer only        |
| `get_gravity()`           | `np.ndarray` or `None` | Get gravity vector only      |
| `get_user_acceleration()` | `np.ndarray` or `None` | Get user acceleration only   |
| `get_attitude()`          | `np.ndarray` or `None` | Get attitude quaternion only |
| `close()`                 | `None`                 | Close connection             |

**Note**:

-   The subscriber is iterable, so you can use `for data in sub:` to receive frames continuously.
-   All `get_*()` methods accept an optional `timeout` parameter (default: 1000ms).

### IMUFrame

Data object returned by `get()` or when iterating. For data format details and physical meanings, see [IMU Data Format Reference](#imu-data) above.

**Properties:**

| Property            | Type         | Description                                         |
| ------------------- | ------------ | --------------------------------------------------- |
| `timestamp`         | `float`      | Unix timestamp in seconds                           |
| `accelerometer`     | `np.ndarray` | Accelerometer $[a_x, a_y, a_z]$ in G                |
| `gyroscope`         | `np.ndarray` | Gyroscope $[\omega_x, \omega_y, \omega_z]$ in rad/s |
| `magnetometer`      | `np.ndarray` | Magnetometer $[m_x, m_y, m_z]$ in μT                |
| `gravity`           | `np.ndarray` | Gravity $[g_x, g_y, g_z]$ in G                      |
| `user_acceleration` | `np.ndarray` | User acceleration $[u_x, u_y, u_z]$ in G            |
| `attitude`          | `np.ndarray` | Attitude quaternion $[q_x, q_y, q_z, q_w]$          |

**Helper Properties:**

| Property                | Type   | Description                        |
| ----------------------- | ------ | ---------------------------------- |
| `has_accelerometer`     | `bool` | Check if accelerometer data exists |
| `has_gyroscope`         | `bool` | Check if gyroscope data exists     |
| `has_magnetometer`      | `bool` | Check if magnetometer data exists  |
| `has_gravity`           | `bool` | Check if gravity data exists       |
| `has_user_acceleration` | `bool` | Check if user acceleration exists  |
| `has_attitude`          | `bool` | Check if attitude data exists      |

## Requirements

-   Python >= 3.8
-   numpy >= 1.20.0
-   pyzmq >= 22.0.0
-   protobuf >= 4.0.0
-   opencv-python >= 4.5.0
-   Pillow >= 8.0.0

## License

MIT License
