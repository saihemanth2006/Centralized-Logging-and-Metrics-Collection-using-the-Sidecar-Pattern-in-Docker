from flask import Flask, jsonify
import json
import time
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
LOG_FILE = '/logs/app.log'
SERVICE_NAME = 'user-service'

# Metrics storage
request_count = 0
user_operations = 0

def write_log(level, message, extra_data=None):
    """Write structured JSON logs to file"""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'service': SERVICE_NAME,
        'level': level,
        'message': message,
    }
    if extra_data:
        log_entry.update(extra_data)
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
        f.flush()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    global request_count
    request_count += 1
    write_log('INFO', 'Health check endpoint called')
    return jsonify({'status': 'healthy', 'service': SERVICE_NAME}), 200

@app.route('/users', methods=['GET'])
def get_users():
    """Mock endpoint to get users"""
    global request_count, user_operations
    request_count += 1
    user_operations += 1
    
    write_log('INFO', 'Fetching users list', {'operation': 'get_users', 'count': 3})
    
    return jsonify({
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'},
            {'id': 3, 'name': 'Charlie'}
        ]
    }), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Mock endpoint to get a specific user"""
    global request_count, user_operations
    request_count += 1
    user_operations += 1
    
    write_log('INFO', f'Fetching user {user_id}', {'operation': 'get_user', 'user_id': user_id})
    
    return jsonify({'id': user_id, 'name': f'User{user_id}'}), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus-compatible metrics endpoint"""
    metrics_text = f"""# HELP app_requests_total Total number of requests received
# TYPE app_requests_total counter
app_requests_total{{service="{SERVICE_NAME}"}} {request_count}

# HELP user_operations_total Total number of user operations
# TYPE user_operations_total counter
user_operations_total{{service="{SERVICE_NAME}"}} {user_operations}

# HELP app_info Application information
# TYPE app_info gauge
app_info{{service="{SERVICE_NAME}",version="1.0.0"}} 1
"""
    return metrics_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == '__main__':
    write_log('INFO', f'{SERVICE_NAME} starting up')
    app.run(host='0.0.0.0', port=8080, debug=False)
