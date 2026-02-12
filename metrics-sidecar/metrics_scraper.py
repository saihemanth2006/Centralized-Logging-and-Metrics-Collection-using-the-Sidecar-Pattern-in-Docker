from flask import Flask, Response
import requests
import os
import time
from threading import Thread, Lock

app = Flask(__name__)

# Configuration
APP_SERVICE_URL = os.environ.get('APP_SERVICE_URL', 'http://localhost:8080')
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'unknown-service')
SCRAPE_INTERVAL = 10  # seconds

# Cached metrics
cached_metrics = ""
metrics_lock = Lock()

def scrape_metrics():
    """Periodically scrape metrics from the application service"""
    global cached_metrics
    
    print(f"[Metrics Sidecar] Starting for service: {SERVICE_NAME}", flush=True)
    print(f"[Metrics Sidecar] Scraping from: {APP_SERVICE_URL}/metrics", flush=True)
    
    while True:
        try:
            response = requests.get(f"{APP_SERVICE_URL}/metrics", timeout=5)
            if response.status_code == 200:
                # Parse and enrich metrics
                original_metrics = response.text
                enriched_metrics = enrich_metrics(original_metrics)
                
                with metrics_lock:
                    cached_metrics = enriched_metrics
                
                print(f"[Metrics Sidecar] Successfully scraped and enriched metrics", flush=True)
            else:
                print(f"[Metrics Sidecar] Failed to scrape metrics: HTTP {response.status_code}", flush=True)
        except requests.exceptions.RequestException as e:
            print(f"[Metrics Sidecar] Error scraping metrics: {e}", flush=True)
        except Exception as e:
            print(f"[Metrics Sidecar] Unexpected error: {e}", flush=True)
        
        time.sleep(SCRAPE_INTERVAL)

def enrich_metrics(original_metrics):
    """Add identifying labels and metadata to metrics"""
    enriched_lines = []
    
    # Add sidecar metadata
    enriched_lines.append(f"# Metrics enriched by {SERVICE_NAME}-metrics-sidecar")
    enriched_lines.append(f"# Scraped from: {APP_SERVICE_URL}/metrics")
    enriched_lines.append("")
    
    # Process each line and add labels
    for line in original_metrics.split('\n'):
        if line.strip() and not line.startswith('#'):
            # Add environment label to metric lines
            if '{' in line:
                # Metric already has labels, add to them
                metric_name, rest = line.split('{', 1)
                labels, value = rest.split('}', 1)
                enriched_line = f'{metric_name}{{sidecar="true",environment="docker",{labels}}}{value}'
            else:
                # Metric has no labels, add them
                parts = line.split(' ')
                if len(parts) >= 2:
                    metric_name = parts[0]
                    value = ' '.join(parts[1:])
                    enriched_line = f'{metric_name}{{sidecar="true",environment="docker"}} {value}'
                else:
                    enriched_line = line
            enriched_lines.append(enriched_line)
        else:
            enriched_lines.append(line)
    
    return '\n'.join(enriched_lines)

@app.route('/metrics', methods=['GET'])
def metrics():
    """Expose enriched Prometheus-compatible metrics"""
    with metrics_lock:
        return Response(cached_metrics, mimetype='text/plain; charset=utf-8')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'service': f'{SERVICE_NAME}-metrics-sidecar'}, 200

if __name__ == '__main__':
    # Start the scraper thread
    scraper_thread = Thread(target=scrape_metrics, daemon=True)
    scraper_thread.start()
    
    # Give the scraper a moment to fetch initial metrics
    time.sleep(2)
    
    # Start the Flask app
    print(f"[Metrics Sidecar] Starting metrics endpoint on port 9090", flush=True)
    app.run(host='0.0.0.0', port=9090, debug=False)
