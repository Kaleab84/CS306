import socket
import threading
import time

TCP_SERVER = "127.0.0.1"
TCP_PORT = 5050
UDP_SERVER = "127.0.0.1"
UDP_PORT = 6060


def receive_messages(client_socket):
    """Receives incoming messages from the server."""
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                break
            print(message)
        except:
            break


def send_status_updates(username):
    """Sends periodic status updates via UDP"""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        udp_socket.sendto(f"STATUS {username} online".encode("utf-8"), (UDP_SERVER, UDP_PORT))
        time.sleep(10)  # Update every 10 seconds


def chat_client():
    """Main chat client function"""
    username = input("Enter your username: ")

    # Connect to TCP Server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((TCP_SERVER, TCP_PORT))
    client_socket.send(f"LOGIN {username}".encode("utf-8"))

    # Start receiving messages in a separate thread
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    # Start sending status updates in a separate thread
    threading.Thread(target=send_status_updates, args=(username,), daemon=True).start()

    # User input loop for sending messages
    while True:
        message = input()
        if message.lower() == "exit":
            client_socket.send(f"LOGOUT {username}".encode("utf-8"))
            break
        else:
            recipient = input("Enter recipient username: ")
            client_socket.send(f"MESSAGE {recipient} {message}".encode("utf-8"))

    client_socket.close()


if __name__ == "__main__":
    chat_client()
