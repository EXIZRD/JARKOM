import socket
import threading
import os

# ================= K O N F I G U R A S I =================
TCP_PORT = 8000     # Port Web Server
UDP_PORT = 9090     # Port Echo/QoS Server
HTML_FILE = "index.html"  # Nama file HTML lokal
# =========================================================

# --- 1. TCP SERVER (Serving HTML File) ---
def run_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('0.0.0.0', TCP_PORT))
        server_socket.listen(5)
        print(f"[TCP] Web Server jalan di port {TCP_PORT}. Melayani file: {HTML_FILE}")
        
        while True:
            client_sock, addr = server_socket.accept()
            request = client_sock.recv(1024).decode()
            
            # Coba baca file HTML lokal
            try:
                with open(HTML_FILE, 'r', encoding='utf-8') as file:
                    file_content = file.read()
                
                # Header HTTP 200 OK
                response_header = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
                response_data = response_header + file_content
                
            except FileNotFoundError:
                # Jika file tidak ada, kirim 404
                response_data = (
                    "HTTP/1.1 404 Not Found\r\n"
                    "Content-Type: text/html\r\n\r\n"
                    "<h1>404 Error</h1><p>File html tidak ditemukan.</p>"
                )
            
            # Kirim data ke client/proxy
            client_sock.sendall(response_data.encode())
            client_sock.close()
            
    except Exception as e:
        print(f"[TCP Error] {e}")

# --- 2. UDP SERVER (Echo Reply for QoS) ---
def run_udp_server():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        udp_socket.bind(('0.0.0.0', UDP_PORT))
        print(f"[UDP] Echo Server jalan di port {UDP_PORT}...")
        
        while True:
            data, addr = udp_socket.recvfrom(2048)
            # Echo balik untuk tes latency/jitter
            udp_socket.sendto(data, addr)
            
    except Exception as e:
        print(f"[UDP Error] {e}")

# --- MAIN ---
if __name__ == "__main__":
    t1 = threading.Thread(target=run_tcp_server)
    t2 = threading.Thread(target=run_udp_server)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
