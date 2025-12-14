import socket
import threading

# KONFIGURASI PORT
# Sesuaikan dengan forwarding rule di Proxy (Laptop B)
# Misal: Proxy port 8080 -> forward ke Laptop A port 8000
TCP_PORT = 8000 
# Misal: Proxy port 9090 -> forward ke Laptop A port 9090
UDP_PORT = 9090 

# ==========================================
# 1. TCP SERVER (HTTP Handling)
# ==========================================
def run_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow reuse address agar tidak error "Address already in use" saat restart
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('0.0.0.0', TCP_PORT))
        server_socket.listen(5)
        print(f"[TCP] Web Server berjalan di port {TCP_PORT}...")
        
        while True:
            client_sock, addr = server_socket.accept()
            # Terima request (tidak perlu diparsing detail untuk tugas ini)
            request = client_sock.recv(1024).decode()
            
            # Respon HTTP Sederhana
            http_response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n\r\n"
                "<html><body><h1>Halo dari Laptop A (Web Server)!</h1></body></html>"
            )
            
            client_sock.sendall(http_response.encode())
            client_sock.close()
            
    except Exception as e:
        print(f"[TCP Error] {e}")

# ==========================================
# 2. UDP SERVER (QoS Echo Reply)
# ==========================================
def run_udp_server():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        udp_socket.bind(('0.0.0.0', UDP_PORT))
        print(f"[UDP] Echo Server berjalan di port {UDP_PORT}...")
        
        while True:
            # Terima paket dari Proxy/Client
            data, addr = udp_socket.recvfrom(2048)
            
            # Langsung kirim balik (Echo) agar Client bisa hitung Latency/Jitter
            udp_socket.sendto(data, addr)
            
    except Exception as e:
        print(f"[UDP Error] {e}")

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # Jalankan TCP dan UDP secara paralel (Threading)
    t1 = threading.Thread(target=run_tcp_server)
    t2 = threading.Thread(target=run_udp_server)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
