import socket
import threading

# ==========================================
# KONFIGURASI SERVER
# ==========================================
# 0.0.0.0 artinya server akan mendengarkan dari segala IP interface (Wi-Fi/LAN)
BIND_IP = '0.0.0.0' 

# Port yang dibuka di Laptop A. 
# PENTING: Beritahu tim Proxy (Laptop B) untuk meneruskan trafik ke port ini.
SERVER_TCP_PORT = 8000  # Proxy (8080) -> Forward ke sini (8000)
SERVER_UDP_PORT = 9000  # Proxy (9090) -> Forward ke sini (9090)

# ==========================================
# TCP HANDLER (Simulasi Web Server HTTP)
# ==========================================
def run_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Menghindari error "Address already in use" saat restart cepat
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((BIND_IP, SERVER_TCP_PORT))
        server.listen(5)
        print(f"[*] TCP Web Server berjalan di port {SERVER_TCP_PORT}")
        
        while True:
            client_sock, addr = server.accept()
            # print(f"[TCP] Koneksi masuk dari {addr[0]}:{addr[1]}")
            
            # Handle request dalam thread terpisah agar tidak blocking
            client_handler = threading.Thread(target=handle_tcp_client, args=(client_sock,))
            client_handler.start()
    except Exception as e:
        print(f"[!] Error TCP Server: {e}")

def handle_tcp_client(client_socket):
    try:
        request = client_socket.recv(1024).decode()
        # print(f"[TCP Request Received]:\n{request}")

        # Membuat respon HTTP sederhana
        http_body = "<html><body><h1>Halo! Ini Laptop A (Web Server).</h1><p>Koneksi TCP Sukses.</p></body></html>"
        
        http_response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(http_body)}\r\n"
            "\r\n"
            f"{http_body}"
        )
        
        client_socket.send(http_response.encode())
    except Exception as e:
        print(f"[!] Error handling client: {e}")
    finally:
        client_socket.close()

# ==========================================
# UDP HANDLER (Simulasi Echo Server untuk QoS)
# ==========================================
def run_udp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        sock.bind((BIND_IP, SERVER_UDP_PORT))
        print(f"[*] UDP Echo Server berjalan di port {SERVER_UDP_PORT}")
        
        while True:
            # Terima data dari Proxy
            data, addr = sock.recvfrom(2048)
            
            # Log opsional (bisa dimatikan agar terminal tidak penuh saat ping 100x)
            # print(f"[UDP] Ping dari {addr}: {data.decode()}")
            
            # Echo: Kirim balik data persis seperti yang diterima ke pengirim (Proxy)
            sock.sendto(data, addr)
            
    except Exception as e:
        print(f"[!] Error UDP Server: {e}")

# ==========================================
# MAIN PROGRAM
# ==========================================
if __name__ == "__main__":
    print("--- MEMULAI SERVER LAPTOP A ---")
    
    # Jalankan TCP dan UDP secara paralel menggunakan Threading
    t_tcp = threading.Thread(target=run_tcp_server)
    t_udp = threading.Thread(target=run_udp_server)
    
    t_tcp.start()
    t_udp.start()
    
    # Join threads agar program utama tidak langsung keluar
    t_tcp.join()
    t_udp.join()
