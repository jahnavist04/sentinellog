import socket
import json
import time
import random
import os

SERVICE_NAME = os.environ.get('SERVICE_NAME', 'ServiceA')
COLLECTOR_HOST = os.environ.get('COLLECTOR_HOST', 'localhost')
COLLECTOR_PORT = int(os.environ.get('COLLECTOR_PORT', 9999))

LOG_LEVELS = ['INFO', 'INFO', 'INFO', 'WARNING', 'ERROR']

MESSAGES = {
    'INFO': [
        "Server started successfully",
        "Request processed in 120ms",
        "Connection established",
        "Data synced successfully",
        "Heartbeat sent",
        "Cache refreshed",
        "User authenticated successfully",
        "Backup completed successfully"
    ],
    'WARNING': [
        "CPU usage at 80%",
        "Memory usage high",
        "Response time degraded",
        "Retry attempt 1/3",
        "Disk space below 20%",
        "Network latency spike detected",
        "Connection pool nearly exhausted",
        "Rate limit threshold approaching"
    ],
    'ERROR': [
        "Database connection failed",
        "Request timeout after 30s",
        "Service unreachable",
        "Authentication failed",
        "Critical memory overflow",
        "Packet loss detected on interface eth0",
        "5G node handover failed",
        "Network slice allocation error"
    ]
}

def send_log(sock, level, message):
    log = {
        'service': SERVICE_NAME,
        'level': level,
        'message': message
    }
    sock.send((json.dumps(log) + '\n').encode('utf-8'))

def connect_with_retry():
    retries = 10
    while retries > 0:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((COLLECTOR_HOST, COLLECTOR_PORT))
            print(f"[{SERVICE_NAME}] Connected to collector at {COLLECTOR_HOST}:{COLLECTOR_PORT}")
            return sock
        except Exception as e:
            print(f"[{SERVICE_NAME}] Collector not ready, retrying... ({e})")
            retries -= 1
            time.sleep(3)
    raise Exception("Could not connect to collector after 10 retries")

def start_service():
    print(f"[{SERVICE_NAME}] Starting...")
    sock = connect_with_retry()

    try:
        while True:
            level = random.choice(LOG_LEVELS)
            message = random.choice(MESSAGES[level])
            send_log(sock, level, message)
            print(f"[{SERVICE_NAME}] Sent {level}: {message}")
            time.sleep(random.uniform(1, 4))
    except KeyboardInterrupt:
        print(f"[{SERVICE_NAME}] Shutting down")
    except Exception as e:
        print(f"[{SERVICE_NAME}] Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    start_service()