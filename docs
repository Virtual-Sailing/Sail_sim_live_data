# Future Developments

This document outlines potential future enhancements for the WebSocket Real-Time Data Streaming Project to further improve functionality, security, and scalability.

## 1. IAM Role Configuration for Enhanced Security
Transitioning from root user access to AWS IAM roles is recommended for secure and role-based access control.

- **Access Control**: Define roles with specific permissions required for server operations.
- **User Management**: Create IAM users for different organizational roles.
- **Auditability**: Enable logging with Amazon CloudWatch for detailed insights into user actions.

## 2. Development of a Purpose-Built Front-End Interface
To improve user experience, consider developing a front-end interface for advanced data visualization.

- **Real-Time Visualization**: Charts and interactive displays for metrics like position, speed, and angle.
- **Customizable Views**: Allow users to tailor views to specific data points.
- **Authentication and Privacy**: Implement user authentication for controlled access to sensitive data.

## 3. Inclusion of Additional Simulation Metrics
Further enrich data by adding new metrics, such as hike value, if supported by the simulator software.

- **New Metrics**: Include hike value or other advanced telemetry data.
- **Extended Data Parsing**: Modify `Local.py` and `Autostart_local.py` to recognize and parse additional fields.

## 4. Automated IP Address Detection
Implement automated IP detection in the listener scripts to streamline deployment across various simulators.

```python
import socket

# Automatically detect the local IP address
def get_local_ip():
    """Determine the local IP address by creating a dummy socket connection."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Dummy connection
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error determining IP: {e}")
        return "127.0.0.1"

LOCAL_UDP_IP = get_local_ip()
SIMULATOR_TCP_IP = get_local_ip()
