import socket
import threading
import time


# ==========================
# KONFIGURASI SERVER
# ==========================
SERVER_IP = "10.18.45.185"      # GANTI dengan IP Laptop A (Web Server)
TCP_SERVER_PORT = 8000        # Port Web Server (TCP)
UDP_SERVER_PORT = 9000        # Port UDP Echo Server


PROXY_TCP_PORT = 8080         # Port Proxy TCP
PROXY_UDP_PORT = 9090         # Port Proxy UDP


PROXY_BIND_IP = "10.18.45.185"




TIMEOUT = 7                   # Timeout (detik)


# Cache sederhana (key: request, value: response)
cache = {}


# ======================================================
# HANDLE TCP CONNECTION (WORKER THREAD)
# ======================================================
def handle_tcp(client_conn, client_addr):
    start_time = time.time()
    client_conn.settimeout(TIMEOUT)


    try:
        print(f"[B][TCP] Connection from {client_addr}")


        # Koneksi ke Web Server
        server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_conn.settimeout(TIMEOUT)
        server_conn.connect((SERVER_IP, TCP_SERVER_PORT))


        # Terima request dari client
        request = client_conn.recv(4096)
        req_size = len(request)


        # ==========================
        # CACHE CHECK
        # ==========================
        if request in cache:
            response = cache[request]
            cache_status = "HIT"
        else:
            server_conn.sendall(request)
            response = server_conn.recv(4096)
            cache[request] = response
            cache_status = "MISS"


        resp_size = len(response)


        # Kirim response ke client
        client_conn.sendall(response)


    except socket.timeout:
        response = (
            "HTTP/1.1 504 Gateway Timeout\r\n"
            "Content-Type: text/plain\r\n\r\n"
            "504 Gateway Timeout"
        ).encode()
        client_conn.sendall(response)
        resp_size = len(response)
        cache_status = "ERROR-504"


    except Exception:
        response = (
            "HTTP/1.1 502 Bad Gateway\r\n"
            "Content-Type: text/plain\r\n\r\n"
            "502 Bad Gateway"
        ).encode()
        client_conn.sendall(response)
        resp_size = len(response)
        cache_status = "ERROR-502"


    end_time = time.time()
    process_time = end_time - start_time


    # ==========================
    # LOGGING TCP
    # ==========================
    print("===== TCP PROXY LOG =====")
    print(f"Source IP      : {client_addr[0]}")
    print(f"Destination IP : {SERVER_IP}")
    print("Protocol       : TCP")
    print(f"Cache Status   : {cache_status}")
    print(f"Request Size   : {req_size if 'req_size' in locals() else 0} bytes")
    print(f"Response Size  : {resp_size} bytes")
    print(f"Process Time   : {process_time:.5f} seconds")
    print("==========================")


    client_conn.close()
    try:
        server_conn.close()
    except:
        pass




# ======================================================
# TCP PROXY SERVER (LISTENER)
# ======================================================
def tcp_proxy():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", PROXY_TCP_PORT))
    s.listen(20)


    print(f"[B] TCP Proxy running on port {PROXY_TCP_PORT}")


    while True:
        client_conn, client_addr = s.accept()
        threading.Thread(
            target=handle_tcp,
            args=(client_conn, client_addr)
        ).start()




# ======================================================
# UDP PROXY SERVER
# ======================================================
def udp_proxy():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((PROXY_BIND_IP, PROXY_UDP_PORT))






    print(f"[B] UDP Proxy running on port {PROXY_UDP_PORT}")


    while True:
        try:
            # Terima paket dari client
            data, client_addr = s.recvfrom(2048)
            start_time = time.time()
            data_size = len(data)


            # Forward ke UDP server
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_sock.settimeout(TIMEOUT)
            server_sock.sendto(data, (SERVER_IP, UDP_SERVER_PORT))


            # Terima response dari server
            response, _ = server_sock.recvfrom(2048)
            s.sendto(response, client_addr)


            status = "FORWARDED"


        except socket.timeout:
            # Tidak ada retransmission (sesuai PDF)
            status = "TIMEOUT"


        except Exception:
            status = "ERROR"


        end_time = time.time()
        process_time = end_time - start_time if 'start_time' in locals() else 0


        # ==========================
        # LOGGING UDP
        # ==========================
        print("===== UDP PROXY LOG =====")
        print(f"Source IP      : {client_addr[0]}")
        print(f"Destination IP : {SERVER_IP}")
        print("Protocol       : UDP")
        print(f"Status         : {status}")
        print(f"Data Size      : {data_size if 'data_size' in locals() else 0} bytes")
        print(f"Process Time   : {process_time:.5f} seconds")
        print("==========================")


        try:
            server_sock.close()
        except:
            pass




# ======================================================
# RUN BOTH TCP & UDP PROXY
# ======================================================
def main():
    tcp_thread = threading.Thread(target=tcp_proxy)
    udp_thread = threading.Thread(target=udp_proxy)


    tcp_thread.start()
    udp_thread.start()


    tcp_thread.join()
    udp_thread.join()




if __name__ == "__main__":
    main()
