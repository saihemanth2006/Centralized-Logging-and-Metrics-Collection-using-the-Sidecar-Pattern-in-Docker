from flask import Flask, jsonify
import json
import time
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
LOG_FILE = '/logs/app.log'
SERVICE_NAME = 'order-service'

# Metrics storage
request_count = 0
order_operations = 0

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

@app.route('/orders', methods=['GET'])
def get_orders():
    """Mock endpoint to get orders"""
    global request_count, order_operations
    request_count += 1
    order_operations += 1
    
    write_log('INFO', 'Fetching orders list', {'operation': 'get_orders', 'count': 2})
    
    return jsonify({
        'orders': [
            {'id': 1, 'user_id': 1, 'product_id': 1, 'status': 'completed'},
            {'id': 2, 'user_id': 2, 'product_id': 3, 'status': 'pending'}
        ]
    }), 200

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Mock endpoint to get a specific order"""
    global request_count, order_operations
    request_count += 1
    order_operations += 1
    
    write_log('INFO', f'Fetching order {order_id}', {'operation': 'get_order', 'order_id': order_id})
    
    return jsonify({'id': order_id, 'user_id': 1, 'product_id': 1, 'status': 'completed'}), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus-compatible metrics endpoint"""
    metrics_text = f"""# HELP app_requests_total Total number of requests received
# TYPE app_requests_total counter
app_requests_total{{service="{SERVICE_NAME}"}} {request_count}

# HELP order_operations_total Total number of order operations
# TYPE order_operations_total counter
order_operations_total{{service="{SERVICE_NAME}"}} {order_operations}

# HELP app_info Application information
# TYPE app_info gauge
app_info{{service="{SERVICE_NAME}",version="1.0.0"}} 1
"""
    return metrics_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == '__main__':
    write_log('INFO', f'{SERVICE_NAME} starting up')
    app.run(host='0.0.0.0', port=8080, debug=False)
