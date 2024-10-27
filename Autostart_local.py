import socket
import struct
import threading
import json
import time
import paramiko
from datetime import datetime, timedelta

# Local IP address and ports for receiving simulation software data
LOCAL_UDP_IP = "192.168.50.164"
LOCAL_UDP_PORT = 1206  # Port your simulation software is using for UDP
SIMULATOR_TCP_IP = "192.168.50.164"  # This should be your local IP or the IP of the simulator
SIMULATOR_TCP_PORT = 1207  # Port your simulation software is using for TCP

# AWS UDP server IP and port (Code 2 is listening here)
AWS_UDP_IP = "3.92.183.187"
AWS_UDP_PORT = 9876  # Port for UDP data on the AWS instance

# WebSocket server details
SSH_HOST = "3.92.183.187"  # AWS instance IP
SSH_USERNAME = "ubuntu"    # Username for the AWS instance
SSH_KEY_PATH = "d:/desktop/AC4pem.pem"  # Path to your .pem key file

# Create a UDP socket for sending data to AWS
udp_socket_to_aws = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Timeout for inactivity (in seconds)
INACTIVITY_TIMEOUT = 6  # 6 seconds
last_activity_time = datetime.now()

# Function to start the WebSocket server on the AWS instance via SSH
def start_websocket_server_via_ssh():
    try:
        print("Connecting to AWS WebSocket server.....")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SSH_HOST, username=SSH_USERNAME, key_filename=SSH_KEY_PATH)
        
        # Commands to start the WebSocket server on the AWS instance (updated to server4.py)
        commands = """
        cd ~/SailSim/websocket_server
        source ~/SailSim/venv/bin/activate
        nohup python3 server4.py > output.log 2>&1 &
        """
        
        stdin, stdout, stderr = ssh.exec_command(commands)
        print("Successfully connected to WebSocket server")
        print("WebSocket ready to receive UDP packets from Simulator")
        ssh.close()
    except Exception as e:
        print(f"Failed to start WebSocket server via SSH: {e}")

# Function to stop the WebSocket server on the AWS instance via SSH
def stop_websocket_server_via_ssh():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SSH_HOST, username=SSH_USERNAME, key_filename=SSH_KEY_PATH)
        
        # Command to stop the WebSocket server (server4.py)
        commands = "pkill -f server4.py"
        ssh.exec_command(commands)
        print("Stopped WebSocket server on AWS instance.")
        ssh.close()
    except Exception as e:
        print(f"Failed to stop WebSocket server via SSH: {e}")

# Function to send JSON data to the AWS UDP server
def send_data_to_aws_udp(json_data):
    try:
        udp_packet = json_data.encode('utf-8')
        print(f"Sending UDP packet: {udp_packet}")
        udp_socket_to_aws.sendto(udp_packet, (AWS_UDP_IP, AWS_UDP_PORT))
        print(f"Successfully sent data to AWS UDP server: {json_data}")
    except Exception as e:
        print(f"Failed to send data to AWS UDP server: {e}")

def decode_binary_data(binary_data):
    format_string = '<I I i i f f f f f f f i f ? f'
    try:
        size, message_type, simclock, sendtime, posx, posy, posz, anglex, angley, anglez, boomangle, tack, sailangletowind, luffing, finishtime = struct.unpack(format_string, binary_data[:struct.calcsize(format_string)])
        data = {
            "Size": size,
            "Message Type": message_type,
            "Simclock": simclock,
            "Send Time": sendtime,
            "Position": {"X": posx, "Y": posy, "Z": posz},
            "Angle": {"X": anglex, "Y": angley, "Z": anglez},
            "Boom Angle": boomangle,
            "Tack": tack,
            "Sail Angle to Wind": sailangletowind,
            "Luffing": luffing,
            "Finish Time": finishtime
        }
        json_data = json.dumps(data, indent=4)
        print(f"Decoded JSON data:\n{json_data}")
        send_data_to_aws_udp(json_data)
    except struct.error as e:
        print(f"Error decoding data: {e}")

def listen_for_tcp_data():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((SIMULATOR_TCP_IP, SIMULATOR_TCP_PORT))
    print(f"Connected to TCP data on {SIMULATOR_TCP_IP}:{SIMULATOR_TCP_PORT}...")

    try:
        while True:
            data = tcp_socket.recv(4096)
            if not data:
                print("Connection closed by the simulator.")
                break
            print(f"Received {len(data)} bytes from simulator (TCP)")
            decode_binary_data(data)
            update_last_activity_time()
    except socket.error as e:
        print(f"Error receiving TCP data: {e}")
    finally:
        tcp_socket.close()

def listen_for_udp_data():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((LOCAL_UDP_IP, LOCAL_UDP_PORT))
    print(f"Listening for UDP data on {LOCAL_UDP_IP}:{LOCAL_UDP_PORT}...")

    try:
        while True:
            data, addr = udp_socket.recvfrom(4096)
            print(f"Received {len(data)} bytes from {addr} (UDP)")
            decode_binary_data(data)
            update_last_activity_time()
    except socket.error as e:
        print(f"Error receiving UDP data: {e}")
    finally:
        udp_socket.close()

# Function to update the timestamp of the last received data
def update_last_activity_time():
    global last_activity_time
    last_activity_time = datetime.now()

# Function to monitor inactivity and stop the WebSocket server after 10 minutes
def monitor_inactivity():
    global last_activity_time
    while True:
        time_since_last_activity = datetime.now() - last_activity_time
        if time_since_last_activity.total_seconds() > INACTIVITY_TIMEOUT:
            print("Inactivity detected. Stopping WebSocket server...")
            stop_websocket_server_via_ssh()
            break
        time.sleep(60)  # Check every 60 seconds

if __name__ == "__main__":
    # Auto-start the WebSocket server on the AWS instance
    start_websocket_server_via_ssh()

    # Start the TCP and UDP listening threads
    tcp_thread = threading.Thread(target=listen_for_tcp_data)
    udp_thread = threading.Thread(target=listen_for_udp_data)
    monitor_thread = threading.Thread(target=monitor_inactivity)

    # Start all threads
    tcp_thread.start()
    udp_thread.start()
    monitor_thread.start()

    # Keep the main program running until the threads finish
    tcp_thread.join()
    udp_thread.join()
    monitor_thread.join()
