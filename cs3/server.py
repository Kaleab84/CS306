import socket
import threading

# TCP Server Configuration
TCP_HOST = "0.0.0.0"
TCP_PORT = 5050

# UDP Server Configuration
UDP_HOST = "0.0.0.0"
UDP_PORT = 6060

clients = {}
announcer = None  # Track the announcer

def handle_client(conn, addr):
    """Handles a single client connection over TCP"""
    global announcer
    username = None
    try:
        while True:
            message = conn.recv(1024).decode("utf-8")
            if not message:
                break

            print(f"[TCP RECEIVED] {message} from {addr}")

            parts = message.split(" ", 2)
            command = parts[0].upper()

            if command == "LOGIN" and len(parts) > 1:
                username = parts[1]
                requested_role = parts[2] if len(parts) > 2 else "LISTENER"
                
                # Assign announcer if none exists, otherwise force user to be a listener
                if announcer is None and requested_role == "ANNOUNCER":
                    announcer = username
                    conn.send("ROLE:ANNOUNCER\n".encode("utf-8"))
                    print(f"{username} is now the announcer.")
                else:
                    conn.send("ROLE:LISTENER\n".encode("utf-8"))
                    print(f"{username} connected as a listener.")
                
                clients[username] = conn

            elif command == "ANNOUNCEMENT" and username == announcer:
                if len(parts) > 1:
                    text = parts[1]
                    print(f"[SERVER] Received announcement: {text}")
                    for client_name, client_conn in clients.items():
                        if client_name != announcer:  # Send only to listeners
                            try:
                                print(f"[SERVER] Sending announcement to {client_name}")
                                client_conn.send(f"ANNOUNCEMENT: {text}\n".encode("utf-8"))
                            except Exception as e:
                                print(f"[ERROR] Failed to send to {client_name}: {e}")

            elif command == "LOGOUT":
                break

    except Exception as e:
        print(f"[ERROR] Connection lost with {username}: {e}")

    finally:
        if username:
            clients.pop(username, None)
            if username == announcer:
                announcer = None  # Reset announcer if they disconnect
            print(f"{username} disconnected")
        conn.close()

def tcp_server():
    """Handles TCP chat messages"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((TCP_HOST, TCP_PORT))
    server.listen(5)
    print(f"[TCP SERVER] Listening on {TCP_HOST}:{TCP_PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

def udp_server():
    """Handles UDP status updates"""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.bind((UDP_HOST, UDP_PORT))
    print(f"[UDP SERVER] Listening on {UDP_HOST}:{UDP_PORT}")

    while True:
        data, addr = udp_socket.recvfrom(1024)
        message = data.decode("utf-8")
        print(f"[UDP RECEIVED] {message} from {addr}")

if __name__ == "__main__":
    tcp_thread = threading.Thread(target=tcp_server, daemon=True)
    udp_thread = threading.Thread(target=udp_server, daemon=True)

    tcp_thread.start()
    udp_thread.start()

    tcp_thread.join()
    udp_thread.join()
