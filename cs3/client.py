import socket
import threading
import time

TCP_SERVER = "127.0.0.1"
TCP_PORT = 5050
UDP_SERVER = "127.0.0.1"
UDP_PORT = 6060

role = None  # Stores "ANNOUNCER" or "LISTENER"

def receive_messages(client_socket):
    """Receives incoming messages from the server."""
    try:
        while True:
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                print("[DISCONNECTED] Server closed the connection.")
                break
            print(message)
    except Exception as e:
        print(f"[ERROR] Lost connection to server: {e}")
    finally:
        client_socket.close()

def send_status_updates(username):
    """Sends periodic status updates via UDP"""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            udp_socket.sendto(f"STATUS {username} online".encode("utf-8"), (UDP_SERVER, UDP_PORT))
            time.sleep(10)  # Update every 10 seconds
        except:
            break  # Stop if an error occurs

def chat_client():
    """Main chat client function"""
    global role
    username = input("Enter your username: ")
    
    # Ask if they want to be the announcer
    choice = input("Do you want to be the announcer? (yes/no): ").strip().lower()
    requested_role = "ANNOUNCER" if choice == "yes" else "LISTENER"

    # Connect to TCP Server
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((TCP_SERVER, TCP_PORT))
        client_socket.send(f"LOGIN {username} {requested_role}".encode("utf-8"))

        # Get assigned role from server
        role_response = client_socket.recv(1024).decode("utf-8").strip()
        if "ROLE:ANNOUNCER" in role_response:
            role = "ANNOUNCER"
            print("You are the ANNOUNCER. You can send messages.")
        else:
            role = "LISTENER"
            print("You are a LISTENER. You will only receive announcements.")

        # Start receiving messages in a separate thread
        threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

        # Start sending status updates in a separate thread
        threading.Thread(target=send_status_updates, args=(username,), daemon=True).start()

        # If announcer, allow sending messages
        if role == "ANNOUNCER":
            while True:
                message = input("Enter announcement (or type 'exit' to quit): ")
                if message.lower() == "exit":
                    client_socket.send(f"LOGOUT {username}".encode("utf-8"))
                    break
                else:
                    client_socket.send(f"ANNOUNCEMENT {message}".encode("utf-8"))

        while True:  # Keep the listener alive
            time.sleep(1)  

    except Exception as e:
        print(f"[ERROR] Could not connect to server: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    chat_client()
