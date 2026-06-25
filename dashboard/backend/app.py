from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os
import time

app = Flask(__name__)
CORS(app)

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
            return
        except Exception as e:
            print(f"Database not ready, retrying... ({e})")
            retries -= 1
            time.sleep(3)

init_db()

@app.route('/api/logs')
def get_logs():
    limit = request.args.get('limit', 100)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, service_name, log_level, message, timestamp FROM logs ORDER BY id DESC LIMIT %s",
        (limit,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([{
        'id': r[0],
        'service': r[1],
        'level': r[2],
        'message': r[3],
        'timestamp': str(r[4])
    } for r in rows])

@app.route('/api/stats')
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
    cursor.execute("SELECT service_name, COUNT(*) FROM logs GROUP BY service_name")
    by_service = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({
        'total': total,
        'errors': errors,
        'warnings': warnings,
        'info': info,
        'by_service': [{'service': r[0], 'count': r[1]} for r in by_service]
    })

@app.route('/api/search')
def search_logs():
    query = request.args.get('q', '')
    level = request.args.get('level', None)
    service = request.args.get('service', None)
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
    return jsonify([{
        'id': r[0],
        'service': r[1],
        'level': r[2],
        'message': r[3],
        'timestamp': str(r[4])
    } for r in rows])

@app.route('/api/export')
def export_logs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, service_name, log_level, message, timestamp FROM logs ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    csv = "id,service,level,message,timestamp\n"
    for r in rows:
        csv += f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]}\n"
    return csv, 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=sentinellog.csv'}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)