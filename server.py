import socket
import threading
import hashlib
import os

CHUNK_SIZE = 1024  # Define chunk size

# def compute_checksum(file_path):
#     """Compute SHA256 checksum of a file."""
#     hasher = hashlib.sha256()
#     with open(file_path, 'rb') as f:
#         while chunk := f.read(CHUNK_SIZE):
#             hasher.update(chunk)
#     return hasher.hexdigest()

def compute_checksum(file_path):
    """Compute SHA256 checksum of a file."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        chunk = f.read(CHUNK_SIZE)
        while chunk:  # Equivalent to "while chunk := f.read(CHUNK_SIZE)"
            hasher.update(chunk)
            chunk = f.read(CHUNK_SIZE)  # Read the next chunk
    return hasher.hexdigest()

def handle_client(conn, addr):
    """Handle incoming client connection."""
    print(f"Connected to {addr}")

    # Receive file name
    file_name = conn.recv(1024).decode()
    if not file_name:
        print("No file name received.")
        conn.close()
        return

    # Check if file exists
    if not os.path.exists(file_name):
        conn.sendall(b"ERROR: File not found")
        conn.close()
        return

    # Compute checksum
    checksum = compute_checksum(file_name)

    # Send checksum to client
    conn.sendall(checksum.encode())

    # Send file in chunks
    with open(file_name, 'rb') as f:
        chunk_index = 0
        chunk = f.read(CHUNK_SIZE)  # Read the first chunk
        while chunk:  # Equivalent to "while chunk := f.read(CHUNK_SIZE)" (Python 3.8+)
            conn.sendall(f"{chunk_index:08d}".encode() + chunk)  # Prefix chunk with sequence number
            chunk_index += 1
            chunk = f.read(CHUNK_SIZE)  # Read the next chunk

    print(f"File {file_name} sent successfully.")
    conn.close()

def start_server(host='0.0.0.0', port=5000):
    """Start the server to accept connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()
