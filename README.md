# Sail_sim_live_data
The Sail Simulation Live Race Display project focuses on developing a system to simulate real-time telemetry data from a sailing simulator and display this data live to remote clients.
WebSocket Real-Time Data Streaming Project
This project enables real-time data streaming from a local simulator to multiple clients via a WebSocket server hosted on an AWS EC2 instance. It includes a simple front-end interface for monitoring simulation data in real-time. The project was designed with a flexible architecture that supports both manual and automated WebSocket server management.
Table of Contents
• Introduction
• Features
• Setup
  - Requirements
  - Installation
• Usage
  - Local Machine Setup
  - AWS EC2 WebSocket Server Management
  - Client-Side Connection
• Configuration
• Future Developments

Introduction
This project captures telemetry data from a local simulator using UDP and TCP listeners, formats the data into JSON, and transmits it to connected clients via a WebSocket server. The WebSocket server is hosted on AWS, providing a scalable and efficient setup that allows clients to monitor simulation data live. A simple HTML file (Race.html) is provided to display data in real-time.

Features
• Real-Time Data Streaming: Sends real-time telemetry data to multiple clients.
• Automated Server Management: Automated start/stop of the WebSocket server based on data activity.
• Cross-Platform Deployment: Supports deployment across different local machines and simulators.
• Extensible Data Handling: Built to easily integrate additional telemetry metrics.

Setup
Requirements
• Python 3.7+ on the local machine
• AWS EC2 Instance (Ubuntu 20.04 recommended) for hosting the WebSocket server
• Python Packages:
  - websockets for WebSocket server management
  - paramiko for SSH automation
• Web Browser for viewing the Race.html file

Installation
• Clone the Repository:
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
• Install Required Python Packages: On both the local machine and the AWS instance, run:
   pip install websockets paramiko
• AWS EC2 Configuration:
   - Set up an AWS EC2 instance with the necessary security groups:
   - Allow inbound traffic on port 8765 for WebSocket.
   - Allow inbound traffic on port 80/443 for HTTP/HTTPS if hosting Race.html.
   - Restrict SSH access to trusted IPs on port 22.
   - Upload project files (server4.py, Race.html, and any automation scripts) to the AWS instance.
Usage
Local Machine Setup
• Run the Listener Script:
• Run Local.py for manual WebSocket control, or Autostart_local.py for automated WebSocket start/stop. Ensure IP settings match your local environment.
• To start:
   python Local.py
or
   python Autostart_local.py
• Dynamic IP Detection: The scripts Local.py and Autostart_local.py automatically detect the local IP address, allowing them to adapt to different network configurations.

AWS EC2 WebSocket Server Management
Automated Start/Stop: The Autostart_local.py script uses SSH to start/stop the WebSocket server on AWS based on data activity. Inactivity triggers an automatic server shutdown after 60 seconds.
Manual Control (optional): To manually start or stop the WebSocket server on AWS, connect via SSH and run server4.py directly:
	ssh -i "path-to-key.pem" ubuntu@<your-ec2-ip>
	python server4.py
	
Client-Side Connection
Connect to WebSocket: Open Race.html in a web browser. This file connects to the WebSocket server and displays real-time telemetry data. Ensure the WebSocket URL in Race.html matches your EC2 instance:
	const websocketURL = "ws://<your-ec2-ip>:8765";
	
Configuration
• IP Addresses: Modify LOCAL_UDP_IP and SIMULATOR_TCP_IP in Local.py and Autostart_local.py as needed. The scripts will attempt dynamic IP detection if left as-is.
•Automation Settings: Adjust the inactivity timeout in Autostart_local.py to control when the WebSocket server should automatically shut down.

Future Developments
Consider the following potential enhancements:

•IAM Role Configuration: Transition from root access to IAM roles with restricted permissions for improved security.
•Front-End Interface: Develop a more advanced front-end with interactive charts and customizable views.
•Additional Telemetry Metrics: Incorporate more simulation metrics (e.g., hike value) once the simulation software supports these values.
•Automated IP Detection: Integrated dynamic IP detection simplifies deployment across simulators.
