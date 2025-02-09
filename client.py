import socket
import hashlib
import os

# Client Configuration
HOST = "127.0.0.1"
PORT = 5000
CHUNK_SIZE = 1024


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


def send_file(client_socket, filepath):
    """Send a file to the server."""
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)

    # Send file metadata
    client_socket.send(f"{filename}|{filesize}".encode())

    # Send file in chunks
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            client_socket.send(chunk)

    print(f"[UPLOADED] {filename} ({filesize} bytes) to server.")


def receive_file(client_socket, original_filename):
    """Receive a file back from the server and verify integrity."""
    checksum = client_socket.recv(64).decode()

    received_filename = f"received_{original_filename}"
    chunks = {}

    with open(received_filename, "wb") as f:
        while True:
            data = client_socket.recv(CHUNK_SIZE + 10)  # Extra for sequence number
            if not data:
                break
            parts = data.split(b"|", 1)
            if len(parts) != 2:
                continue
            seq_num = int(parts[0])
            chunks[seq_num] = parts[1]

        for i in sorted(chunks.keys()):
            f.write(chunks[i])

    print(f"[DOWNLOADED] {received_filename} received from server.")

    # Verify checksum
    received_checksum = compute_checksum(received_filename)
    if received_checksum == checksum:
        print("[SUCCESS] File integrity verified.")
    else:
        print("[ERROR] File is corrupted. Retransmission needed.")


def start_client(filepath):
    """Starts the client and handles file transfer."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    send_file(client_socket, filepath)
    receive_file(client_socket, os.path.basename(filepath))

    client_socket.close()


if __name__ == "__main__":
    file_to_send = input("Enter the path of the file to upload: ")
    start_client(file_to_send)
