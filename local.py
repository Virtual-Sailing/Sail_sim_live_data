import socket
import struct
import threading
import json

# Local IP address and ports for receiving simulation software data
LOCAL_UDP_IP = "192.168.50.164"
LOCAL_UDP_PORT = 1206  # Port your simulation software is using for UDP
SIMULATOR_TCP_IP = "192.168.50.164"  # This should be your local IP or the IP of the simulator
SIMULATOR_TCP_PORT = 1207  # Port your simulation software is using for TCP

# AWS UDP server IP and port (Code 2 is listening here)
AWS_UDP_IP = "3.92.183.187"
AWS_UDP_PORT = 9876  # Port for UDP data on the AWS instance

# Create a UDP socket for sending data to AWS
udp_socket_to_aws = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_data_to_aws_udp(json_data):
    """Send JSON formatted data to the AWS UDP server and print the packet to the console."""
    try:
        # Convert the JSON data to bytes for UDP transmission
        udp_packet = json_data.encode('utf-8')
        
        # Print the raw packet being sent
        print(f"Sending UDP packet: {udp_packet}")
        
        # Send the packet to the AWS UDP server
        udp_socket_to_aws.sendto(udp_packet, (AWS_UDP_IP, AWS_UDP_PORT))
        print(f"Successfully sent data to AWS UDP server: {json_data}")
    except Exception as e:
        print(f"Failed to send data to AWS UDP server: {e}")

def decode_binary_data(binary_data):
    """Decode the binary data using the defined structure and return it in JSON format."""
    format_string = '<I I i i f f f f f f f i f ? f'
    
    try:
        # Unpack the binary data according to the format string
        size, message_type, simclock, sendtime, posx, posy, posz, anglex, angley, anglez, boomangle, tack, sailangletowind, luffing, finishtime = struct.unpack(format_string, binary_data[:struct.calcsize(format_string)])
        
        # Create a dictionary to hold the decoded values
        data = {
            "Size": size,
            "Message Type": message_type,
            "Simclock": simclock,
            "Send Time": sendtime,
            "Position": {
                "X": posx,
                "Y": posy,
                "Z": posz
            },
            "Angle": {
                "X": anglex,
                "Y": angley,
                "Z": anglez
            },
            "Boom Angle": boomangle,
            "Tack": tack,
            "Sail Angle to Wind": sailangletowind,
            "Luffing": luffing,
            "Finish Time": finishtime
        }

        # Convert to JSON
        json_data = json.dumps(data, indent=4)
        
        # Print the JSON data
        print(f"Decoded JSON data:\n{json_data}")

        # Send the JSON data to the AWS UDP server
        send_data_to_aws_udp(json_data)

    except struct.error as e:
        print(f"Error decoding data: {e}")

def listen_for_tcp_data():
    """Function to listen for TCP data on the specified port and decode it in real-time."""
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((SIMULATOR_TCP_IP, SIMULATOR_TCP_PORT))  # Connect to the simulator's IP and TCP port

    print(f"Connected to TCP data on {SIMULATOR_TCP_IP}:{SIMULATOR_TCP_PORT}...")

    try:
        while True:
            data = tcp_socket.recv(4096)  # Adjust buffer size as needed
            if not data:
                print("Connection closed by the simulator.")
                break

            print(f"Received {len(data)} bytes from simulator (TCP)")

            # Decode the binary data from TCP packets and send as JSON
            decode_binary_data(data)

    except socket.error as e:
        print(f"Error receiving TCP data: {e}")
    finally:
        tcp_socket.close()

def listen_for_udp_data():
    """Function to listen for UDP data on the specified port and decode it in real-time."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((LOCAL_UDP_IP, LOCAL_UDP_PORT))  # Bind to the local UDP IP and port

    print(f"Listening for UDP data on {LOCAL_UDP_IP}:{LOCAL_UDP_PORT}...")

    try:
        while True:
            data, addr = udp_socket.recvfrom(4096)  # Adjust buffer size as needed
            print(f"Received {len(data)} bytes from {addr} (UDP)")

            # Decode the binary data from UDP packets and send as JSON
            decode_binary_data(data)

    except socket.error as e:
        print(f"Error receiving UDP data: {e}")
    finally:
        udp_socket.close()

if __name__ == "__main__":
    # Start the TCP listening thread
    tcp_thread = threading.Thread(target=listen_for_tcp_data)
    
    # Start the UDP listening thread
    udp_thread = threading.Thread(target=listen_for_udp_data)

    # Start both threads
    tcp_thread.start()
    udp_thread.start()

    # Keep the main program running until the threads finish
    tcp_thread.join()
    udp_thread.join()
