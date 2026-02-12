from flask import Flask, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)

# In-memory storage for logs
logs_storage = []

@app.route('/logs', methods=['POST'])
def receive_logs():
    """Receive logs from logging sidecars"""
    try:
        log_entry = request.get_json()
        
        if not log_entry:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Add reception timestamp
        log_entry['aggregator_received_at'] = datetime.utcnow().isoformat() + 'Z'
        
        # Store in memory
        logs_storage.append(log_entry)
        
        # Print to stdout for visibility
        print(f"[Log Aggregator] Received log from {log_entry.get('service', 'unknown')}: {log_entry.get('message', 'N/A')}", flush=True)
        print(f"[Log Aggregator] Full log entry: {json.dumps(log_entry, indent=2)}", flush=True)
        
        return jsonify({'status': 'success', 'message': 'Log received'}), 200
    
    except Exception as e:
        print(f"[Log Aggregator] Error receiving log: {e}", flush=True)
        return jsonify({'error': str(e)}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    """Retrieve all stored logs"""
    # Support filtering by service
    service_filter = request.args.get('service')
    
    filtered_logs = logs_storage
    if service_filter:
        filtered_logs = [log for log in logs_storage if log.get('service') == service_filter]
    
    return jsonify({
        'total': len(filtered_logs),
        'logs': filtered_logs
    }), 200

@app.route('/logs/count', methods=['GET'])
def log_count():
    """Get count of logs by service"""
    counts = {}
    for log in logs_storage:
        service = log.get('service', 'unknown')
        counts[service] = counts.get(service, 0) + 1
    
    return jsonify({
        'total_logs': len(logs_storage),
        'by_service': counts
    }), 200

@app.route('/logs/clear', methods=['POST'])
def clear_logs():
    """Clear all stored logs"""
    global logs_storage
    count = len(logs_storage)
    logs_storage = []
    print(f"[Log Aggregator] Cleared {count} logs", flush=True)
    return jsonify({'status': 'success', 'cleared': count}), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'log-aggregator',
        'logs_stored': len(logs_storage)
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Simple index page with instructions"""
    return jsonify({
        'service': 'Log Aggregator',
        'endpoints': {
            'POST /logs': 'Receive logs from sidecars',
            'GET /logs': 'Retrieve all logs (optional ?service=<name> filter)',
            'GET /logs/count': 'Get log counts by service',
            'POST /logs/clear': 'Clear all stored logs',
            'GET /health': 'Health check'
        },
        'current_log_count': len(logs_storage)
    }), 200

if __name__ == '__main__':
    print("[Log Aggregator] Starting up...", flush=True)
    print("[Log Aggregator] Ready to receive logs at POST /logs", flush=True)
    app.run(host='0.0.0.0', port=8080, debug=False)
