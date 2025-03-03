import socket
import threading

# TCP Server Configuration
TCP_HOST = "0.0.0.0"
TCP_PORT = 5050

# UDP Server Configuration
UDP_HOST = "0.0.0.0"
UDP_PORT = 6060

clients = {}

def handle_client(conn, addr):
    """Handles a single client connection over TCP"""
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
                clients[username] = conn
                print(f"{username} logged in from {addr}")
                conn.send("LOGIN_SUCCESS\n".encode("utf-8"))

            elif command == "MESSAGE" and len(parts) > 2:
                recipient, text = parts[1], parts[2]
                if recipient in clients:
                    clients[recipient].send(f"[{username}]: {text}\n".encode("utf-8"))
                else:
                    conn.send(f"ERROR: User {recipient} not found.\n".encode("utf-8"))

            elif command == "LOGOUT":
                break

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        if username:
            del clients[username]
            print(f"{username} disconnected")
        conn.close()

def tcp_server():
    """Handles TCP chat messages"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
    udp_socket.bind((UDP_HOST, UDP_PORT))
    print(f"[UDP SERVER] Listening on {UDP_HOST}:{UDP_PORT}")

    while True:
        data, addr = udp_socket.recvfrom(1024)
        message = data.decode("utf-8")
        print(f"[UDP RECEIVED] {message} from {addr}")

if __name__ == "__main__":
    tcp_thread = threading.Thread(target=tcp_server)
    udp_thread = threading.Thread(target=udp_server)

    tcp_thread.start()
    udp_thread.start()

    tcp_thread.join()
    udp_thread.join()
