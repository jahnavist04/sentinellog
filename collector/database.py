import psycopg2
import os
import time

def get_connection():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        database=os.environ.get('DB_NAME', 'sentinellog'),
        user=os.environ.get('DB_USER', 'sentinel'),
        password=os.environ.get('DB_PASSWORD', 'sentinel123')
    )

def init_db():
    retries = 5
    while retries > 0:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    service_name VARCHAR(100) NOT NULL,
                    log_level VARCHAR(20) NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            cursor.close()
            conn.close()
            print("Database initialized successfully")
            return
        except Exception as e:
            print(f"Database not ready yet, retrying... ({e})")
            retries -= 1
            time.sleep(3)
    raise Exception("Could not connect to database after 5 retries")

def insert_log(service_name, log_level, message):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (service_name, log_level, message) VALUES (%s, %s, %s)",
        (service_name, log_level, message)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_all_logs(limit=100):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, service_name, log_level, message, timestamp FROM logs ORDER BY id DESC LIMIT %s",
        (limit,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM logs")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM logs WHERE log_level='ERROR'")
    errors = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM logs WHERE log_level='WARNING'")
    warnings = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM logs WHERE log_level='INFO'")
    info = cursor.fetchone()[0]
    cursor.execute(
        "SELECT service_name, COUNT(*) FROM logs GROUP BY service_name"
    )
    by_service = cursor.fetchall()
    cursor.close()
    conn.close()
    return {
        'total': total,
        'errors': errors,
        'warnings': warnings,
        'info': info,
        'by_service': by_service
    }

def search_logs(query, level=None, service=None):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "SELECT id, service_name, log_level, message, timestamp FROM logs WHERE message ILIKE %s"
    params = [f'%{query}%']
    if level:
        sql += " AND log_level = %s"
        params.append(level)
    if service:
        sql += " AND service_name = %s"
        params.append(service)
    sql += " ORDER BY id DESC LIMIT 100"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows