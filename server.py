import socket
import threading
import hashlib
import random
import os

# Server Configuration
HOST = "127.0.0.1"
PORT = 5000
CHUNK_SIZE = 1024
PACKET_DROP_RATE = 0
  # 10% chance to drop a packet (simulating network issues)


def compute_checksum(filename):
    """Compute SHA-256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()


def handle_client(client_socket, client_address):
    """Handles file transfer for a single client."""
    try:
        print(f"[NEW CONNECTION] {client_address} connected.")

        # Receive file name and size
        file_info = client_socket.recv(1024).decode()
        filename, filesize = file_info.split("|")
        filename = f"received_{filename}"
        filesize = int(filesize)

        # Receive file data
        with open(filename, "wb") as f:
            received_size = 0
            while received_size < filesize:
                chunk = client_socket.recv(CHUNK_SIZE)
                if not chunk:
                    break
                f.write(chunk)
                received_size += len(chunk)

        print(f"[RECEIVED] File {filename} ({filesize} bytes) from {client_address}")

        # Compute checksum
        checksum = compute_checksum(filename)
        client_socket.send(checksum.encode())

        # Resend file in chunks with packet drop simulation
        with open(filename, "rb") as f:
            seq_num = 0
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                if random.random() > PACKET_DROP_RATE:  # Simulate packet loss
                    client_socket.send(f"{seq_num}|".encode() + chunk)
                seq_num += 1

        print(f"[SENT] File {filename} sent back to {client_address}")

    except Exception as e:
        print(f"[ERROR] Client {client_address} - {e}")
    finally:
        client_socket.close()
        print(f"[DISCONNECTED] {client_address} disconnected.")


def start_server():
    """Starts the multi-client server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"[LISTENING] Server is running on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()


if __name__ == "__main__":
    start_server()
