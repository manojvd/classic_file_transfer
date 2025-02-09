import socket
import hashlib

CHUNK_SIZE = 1024  # Define chunk size

def compute_checksum(data):
    """Compute SHA256 checksum of received data."""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()

def receive_file(server_ip, port, file_name):
    """Request file from server and save it after verifying checksum."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, port))

    # Send file name to server
    client.sendall(file_name.encode())

    # Receive checksum from server
    expected_checksum = client.recv(64).decode()
    
    # Receive file chunks
    received_data = {}
    while True:
        chunk_data = client.recv(CHUNK_SIZE + 8)  # 8 bytes for sequence number
        if not chunk_data:
            break

        seq_num = int(chunk_data[:8].decode())  # Extract sequence number
        received_data[seq_num] = chunk_data[8:]  # Store chunk in dictionary

    # Reassemble the file in order
    ordered_data = b''.join(received_data[i] for i in sorted(received_data.keys()))

    # Verify checksum
    received_checksum = compute_checksum(ordered_data)
    if received_checksum == expected_checksum:
        with open(f"received_{file_name}", 'wb') as f:
            f.write(ordered_data)
        print("Transfer Successful: File received and verified.")
    else:
        print("Transfer Failed: Checksum mismatch.")

    client.close()

if __name__ == "__main__":
    server_ip = "127.0.0.1"
    port = 5000
    file_name = "data.txt"
    receive_file(server_ip, port, file_name)
