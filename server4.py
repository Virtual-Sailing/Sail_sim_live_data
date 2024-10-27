import asyncio
import websockets
import socket
import json

# WebSocket server configuration
WEBSOCKET_PORT = 8765

# UDP server configuration
UDP_IP = "0.0.0.0"
UDP_PORT = 9876

# Create a UDP socket
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind((UDP_IP, UDP_PORT))

connected_clients = set()

async def udp_to_websocket():
    while True:
        data, addr = await asyncio.get_event_loop().run_in_executor(None, udp_sock.recvfrom, 1024)
        json_packet = data.decode('utf-8')
        print(f"Received JSON packet: {json_packet} from {addr}")

        # Forward the JSON object to all connected WebSocket clients
        if connected_clients:
            await asyncio.gather(
                *(client.send(json_packet) for client in connected_clients)
            )

async def handler(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received message from WebSocket client: {message}")
    finally:
        connected_clients.remove(websocket)

async def main():
    websocket_server = await websockets.serve(handler, "0.0.0.0", WEBSOCKET_PORT)
    print(f"WebSocket server is running on port {WEBSOCKET_PORT}")

    await udp_to_websocket()

    await websocket_server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
