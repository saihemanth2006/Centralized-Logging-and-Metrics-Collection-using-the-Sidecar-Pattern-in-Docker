import time
import json
import requests
import os
from datetime import datetime

# Configuration
LOG_FILE = '/logs/app.log'
AGGREGATOR_URL = os.environ.get('AGGREGATOR_URL', 'http://log-aggregator:8080/logs')
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'unknown-service')
POLL_INTERVAL = 2  # seconds

def tail_and_forward_logs():
    """Tail the log file and forward new entries to the aggregator"""
    print(f"[Logging Sidecar] Starting for service: {SERVICE_NAME}", flush=True)
    print(f"[Logging Sidecar] Watching file: {LOG_FILE}", flush=True)
    print(f"[Logging Sidecar] Forwarding to: {AGGREGATOR_URL}", flush=True)
    
    # Wait for log file to be created
    while not os.path.exists(LOG_FILE):
        print(f"[Logging Sidecar] Waiting for log file to be created...", flush=True)
        time.sleep(2)
    
    print(f"[Logging Sidecar] Log file found, starting to tail...", flush=True)
    
    with open(LOG_FILE, 'r') as f:
        # Move to the end of file
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            if line:
                try:
                    # Parse the JSON log entry
                    log_entry = json.loads(line.strip())
                    
                    # Enrich with sidecar metadata
                    enriched_log = {
                        **log_entry,
                        'sidecar_timestamp': datetime.utcnow().isoformat() + 'Z',
                        'sidecar_forwarded_by': f'{SERVICE_NAME}-logging-sidecar',
                        'environment': 'docker-compose'
                    }
                    
                    # Forward to aggregator
                    try:
                        response = requests.post(
                            AGGREGATOR_URL,
                            json=enriched_log,
                            timeout=5
                        )
                        if response.status_code == 200:
                            print(f"[Logging Sidecar] Forwarded log: {log_entry.get('message', 'N/A')}", flush=True)
                        else:
                            print(f"[Logging Sidecar] Failed to forward log: HTTP {response.status_code}", flush=True)
                    except requests.exceptions.RequestException as e:
                        print(f"[Logging Sidecar] Error forwarding log: {e}", flush=True)
                
                except json.JSONDecodeError as e:
                    print(f"[Logging Sidecar] Invalid JSON in log file: {e}", flush=True)
                except Exception as e:
                    print(f"[Logging Sidecar] Unexpected error: {e}", flush=True)
            else:
                # No new data, sleep briefly
                time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    tail_and_forward_logs()
