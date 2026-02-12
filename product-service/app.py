from flask import Flask, jsonify
import json
import time
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
LOG_FILE = '/logs/app.log'
SERVICE_NAME = 'product-service'

# Metrics storage
request_count = 0
product_operations = 0

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

@app.route('/products', methods=['GET'])
def get_products():
    """Mock endpoint to get products"""
    global request_count, product_operations
    request_count += 1
    product_operations += 1
    
    write_log('INFO', 'Fetching products list', {'operation': 'get_products', 'count': 4})
    
    return jsonify({
        'products': [
            {'id': 1, 'name': 'Laptop', 'price': 999.99},
            {'id': 2, 'name': 'Mouse', 'price': 29.99},
            {'id': 3, 'name': 'Keyboard', 'price': 79.99},
            {'id': 4, 'name': 'Monitor', 'price': 299.99}
        ]
    }), 200

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Mock endpoint to get a specific product"""
    global request_count, product_operations
    request_count += 1
    product_operations += 1
    
    write_log('INFO', f'Fetching product {product_id}', {'operation': 'get_product', 'product_id': product_id})
    
    return jsonify({'id': product_id, 'name': f'Product{product_id}', 'price': 99.99}), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus-compatible metrics endpoint"""
    metrics_text = f"""# HELP app_requests_total Total number of requests received
# TYPE app_requests_total counter
app_requests_total{{service="{SERVICE_NAME}"}} {request_count}

# HELP product_operations_total Total number of product operations
# TYPE product_operations_total counter
product_operations_total{{service="{SERVICE_NAME}"}} {product_operations}

# HELP app_info Application information
# TYPE app_info gauge
app_info{{service="{SERVICE_NAME}",version="1.0.0"}} 1
"""
    return metrics_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == '__main__':
    write_log('INFO', f'{SERVICE_NAME} starting up')
    app.run(host='0.0.0.0', port=8080, debug=False)
