import socket
import threading
import json
import os
from database import init_db, insert_log, get_stats

HOST = '0.0.0.0'
PORT = int(os.environ.get('COLLECTOR_PORT', 9999))

def handle_client(conn, addr):
    print(f"[CONNECTED] {addr} connected")
    try:
        buffer = ""
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            buffer += data
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                if line.strip():
                    process_log(line.strip(), addr)
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()
        print(f"[DISCONNECTED] {addr} disconnected")

def process_log(data, addr):
    try:
        log = json.loads(data)
        service_name = log.get('service', 'Unknown')
        log_level = log.get('level', 'INFO')
        message = log.get('message', '')

        insert_log(service_name, log_level, message)
        print(f"[{log_level}] {service_name}: {message}")

        if log_level == 'ERROR':
            stats = get_stats()
            if stats['errors'] % 10 == 0 and stats['errors'] != 0:
                print(f"[ALERT] {stats['errors']} total errors detected!")

    except json.JSONDecodeError:
        print(f"[ERROR] Invalid JSON from {addr}: {data}")
    except Exception as e:
        print(f"[ERROR] Failed to process log: {e}")

def start_server():
    init_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    print(f"[SENTINELLOG] Collector listening on port {PORT}...")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.daemon = True
        thread.start()
        print(f"[ACTIVE] {threading.active_count() - 1} services connected")

if __name__ == "__main__":
    start_server()