# Centralized Logging and Metrics Collection using the Sidecar Pattern in Docker

## Overview

This project demonstrates the **sidecar pattern** for centralized logging and metrics collection in a microservices architecture using Docker. It implements a production-like observability infrastructure that separates cross-cutting concerns (logging, monitoring) from application business logic.

### What is the Sidecar Pattern?

The sidecar pattern is a fundamental concept in cloud-native and microservices architectures. It involves co-locating a helper container (the "sidecar") alongside the main application container. Both containers share resources like network space and storage volumes, allowing the sidecar to augment or enhance the application without being part of its codebase.

### Why Use the Sidecar Pattern?

- **Separation of Concerns**: Decouple observability from application logic
- **Language Agnostic**: Works with any application regardless of programming language
- **Independent Management**: Infrastructure teams can update monitoring components independently
- **Reduced Code Duplication**: Reusable sidecars across multiple services
- **Production-Ready**: Same pattern used by service meshes (Istio/Envoy) and logging agents (Fluentd/Vector)

## Architecture

The system consists of:

- **3 Application Services**: `user-service`, `product-service`, `order-service`
- **Logging Sidecars**: One per service, tails log files and forwards to aggregator
- **Metrics Sidecars**: One per service, scrapes `/metrics` endpoint and enriches data
- **Log Aggregator**: Central service that receives and stores logs from all sidecars

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Log Aggregator                         │
│                   (Receives all logs)                       │
└─────────────────────────────────────────────────────────────┘
                    ▲           ▲           ▲
                    │           │           │
         Logs       │           │           │        Logs
                    │           │           │
    ┌───────────────┴───┐   ┌───┴───────────┴───┐   ┌───────────────┐
    │  Logging Sidecar  │   │  Logging Sidecar  │   │ Logging Sidecar│
    │  (user-service)   │   │ (product-service) │   │ (order-service)│
    └─────────┬─────────┘   └─────────┬─────────┘   └───────┬────────┘
              │                       │                     │
       Shared │                Shared │              Shared │
       Volume │                Volume │              Volume │
              ▼                       ▼                     ▼
    ┌─────────────────┐     ┌─────────────────┐   ┌─────────────────┐
    │  User Service   │     │ Product Service │   │  Order Service  │
    │   (Port 8081)   │     │   (Port 8082)   │   │   (Port 8083)   │
    └─────────┬───────┘     └─────────┬───────┘   └─────────┬───────┘
              │                       │                     │
       HTTP   │                HTTP   │              HTTP   │
    /metrics  │             /metrics  │           /metrics  │
              ▼                       ▼                     ▼
    ┌─────────────────┐     ┌─────────────────┐   ┌─────────────────┐
    │ Metrics Sidecar │     │ Metrics Sidecar │   │ Metrics Sidecar │
    │   (Port 9091)   │     │   (Port 9092)   │   │   (Port 9093)   │
    └─────────────────┘     └─────────────────┘   └─────────────────┘
```

## Project Structure

```
.
├── user-service/
│   ├── app.py                    # User service application
│   ├── Dockerfile
│   └── requirements.txt
├── product-service/
│   ├── app.py                    # Product service application
│   ├── Dockerfile
│   └── requirements.txt
├── order-service/
│   ├── app.py                    # Order service application
│   ├── Dockerfile
│   └── requirements.txt
├── logging-sidecar/
│   ├── log_forwarder.py          # Log tailing and forwarding script
│   ├── Dockerfile
│   └── requirements.txt
├── metrics-sidecar/
│   ├── metrics_scraper.py        # Metrics scraping and enrichment
│   ├── Dockerfile
│   └── requirements.txt
├── log-aggregator/
│   ├── app.py                    # Central log collection service
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml            # Orchestration configuration
├── .env.example                  # Environment variables documentation
├── .gitignore                    # Git ignore rules
├── Makefile                      # Convenience commands
├── QUICKSTART.md                 # Quick start guide
├── test-system.ps1               # Windows test script
├── test-system.sh                # Linux/Mac test script
└── README.md                     # This file
```
```

## Getting Started

### Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

### Running the System

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd Centralized-Logging-and-Metrics-Collection-using-the-Sidecar-Pattern-in-Docker
   ```

2. **Build and start all services**:
   ```bash
   docker-compose up --build
   ```

3. **Access the services**:
   - **User Service**: http://localhost:8081
   - **Product Service**: http://localhost:8082
   - **Order Service**: http://localhost:8083
   - **Log Aggregator**: http://localhost:8000

4. **Access enriched metrics**:
   - **User Service Metrics**: http://localhost:9091/metrics
   - **Product Service Metrics**: http://localhost:9092/metrics
   - **Order Service Metrics**: http://localhost:9093/metrics

### Stopping the System

```bash
docker-compose down
```

To remove volumes as well:
```bash
docker-compose down -v
```

## Testing the System

### 1. Test Application Endpoints

Generate some application activity to create logs and metrics:

```bash
# Test user service
curl http://localhost:8081/health
curl http://localhost:8081/users
curl http://localhost:8081/users/1

# Test product service
curl http://localhost:8082/health
curl http://localhost:8082/products
curl http://localhost:8082/products/1

# Test order service
curl http://localhost:8083/health
curl http://localhost:8083/orders
curl http://localhost:8083/orders/1
```

### 2. View Aggregated Logs

Check that logs are being collected centrally:

```bash
# Get all logs
curl http://localhost:8000/logs

# Get logs for a specific service
curl http://localhost:8000/logs?service=user-service

# Get log count by service
curl http://localhost:8000/logs/count
```

### 3. View Enriched Metrics

Check that metrics are being scraped and enriched with labels:

```bash
# View user service metrics (enriched by sidecar)
curl http://localhost:9091/metrics

# View product service metrics (enriched by sidecar)
curl http://localhost:9092/metrics

# View order service metrics (enriched by sidecar)
curl http://localhost:9093/metrics
```

### 4. Monitor Container Logs

Watch the logs to see the sidecar pattern in action:

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f user-service
docker-compose logs -f user-service-logging-sidecar
docker-compose logs -f log-aggregator
```

## Key Features

### Application Services

Each service (`user-service`, `product-service`, `order-service`) provides:

- **Health Check**: `GET /health` - Returns service health status
- **Business Endpoints**: Service-specific REST APIs
- **Metrics Endpoint**: `GET /metrics` - Prometheus-compatible metrics
- **Structured Logging**: JSON-formatted logs written to `/logs/app.log`

### Logging Sidecar

The logging sidecar container:

1. **Tails** the application's log file from a shared volume (`/logs`)
2. **Enriches** each log entry with metadata:
   - `sidecar_timestamp`: When the log was forwarded
   - `sidecar_forwarded_by`: Identity of the logging sidecar
   - `environment`: Deployment environment
3. **Forwards** enriched logs to the central aggregator via HTTP POST

### Metrics Sidecar

The metrics sidecar container:

1. **Scrapes** the application's `/metrics` endpoint every 10 seconds
2. **Enriches** metrics with additional labels:
   - `sidecar="true"`: Indicates enrichment by sidecar
   - `environment="docker"`: Deployment environment
3. **Exposes** enriched metrics on port 9090 for centralized collection

### Log Aggregator

The central log aggregator provides:

- **POST /logs**: Receive logs from sidecars
- **GET /logs**: Retrieve all stored logs (supports `?service=<name>` filter)
- **GET /logs/count**: Get log counts by service
- **POST /logs/clear**: Clear all stored logs
- **GET /health**: Health check endpoint

## Learning Outcomes

This project demonstrates:

1. **Container Composition**: How to compose multiple containers that work together
2. **Shared Volumes**: Using Docker volumes for inter-container communication
3. **Shared Networks**: Container networking for service discovery
4. **Infrastructure Abstraction**: Separating cross-cutting concerns from application code
5. **Observability Patterns**: Real-world logging and metrics collection strategies
6. **Microservices Architecture**: Building scalable, maintainable distributed systems
7. **Production Patterns**: Techniques used in production Kubernetes environments

## Configuration

### Environment Variables

The system can be configured using environment variables. A comprehensive `.env.example` file is provided that documents all available variables.

**To use custom configuration:**

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your desired values

3. Start the system:
   ```bash
   docker-compose up
   ```

**Key Environment Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment name (development, staging, production) | `development` |
| `USER_SERVICE_PORT` | Port for user service | `8081` |
| `PRODUCT_SERVICE_PORT` | Port for product service | `8082` |
| `ORDER_SERVICE_PORT` | Port for order service | `8083` |
| `USER_METRICS_PORT` | Port for user metrics sidecar | `9091` |
| `PRODUCT_METRICS_PORT` | Port for product metrics sidecar | `9092` |
| `ORDER_METRICS_PORT` | Port for order metrics sidecar | `9093` |
| `LOG_AGGREGATOR_PORT` | Port for log aggregator | `8000` |
| `LOG_AGGREGATOR_URL` | URL for log aggregator (internal) | `http://log-aggregator:8080/logs` |

**Sidecar-Specific Variables:**

**Logging Sidecar**:
- `SERVICE_NAME`: Name of the application service (e.g., `user-service`)
- `AGGREGATOR_URL`: URL of the log aggregator (injected from `LOG_AGGREGATOR_URL`)
- `ENVIRONMENT`: Environment identifier added to all logs

**Metrics Sidecar**:
- `SERVICE_NAME`: Name of the application service
- `APP_SERVICE_URL`: URL of the application service (e.g., `http://user-service:8080`)
- `ENVIRONMENT`: Environment identifier added to all metrics

**Note:** All variables have sensible defaults. You can run the system without creating a `.env` file.

### Ports

| Service | Port | Description |
|---------|------|-------------|
| Log Aggregator | 8000 | Central log collection |
| User Service | 8081 | User service API |
| Product Service | 8082 | Product service API |
| Order Service | 8083 | Order service API |
| User Metrics Sidecar | 9091 | Enriched user service metrics |
| Product Metrics Sidecar | 9092 | Enriched product service metrics |
| Order Metrics Sidecar | 9093 | Enriched order service metrics |

### Docker Compose Features

The `docker-compose.yml` implements several best practices:

- **Health Check Dependencies**: Sidecars wait for their application services to be healthy before starting
- **Read-Only Volumes**: Logging sidecars mount log volumes as read-only (`:ro`) for security
- **Start Period**: Services have a grace period during startup before health checks count as failures
- **Shared Networks**: All containers communicate over a dedicated `app-network`
- **Named Volumes**: Persistent volumes for log storage shared between services and sidecars

## Troubleshooting

### Logs Not Appearing in Aggregator

1. Check if the logging sidecar is running:
   ```bash
   docker-compose ps
   ```

2. Check logging sidecar logs:
   ```bash
   docker-compose logs user-service-logging-sidecar
   ```

3. Verify the log file is being created:
   ```bash
   docker exec user-service ls -la /logs/
   ```

### Metrics Not Updating

1. Check if the metrics sidecar is running:
   ```bash
   docker-compose ps
   ```

2. Verify the application service is responding:
   ```bash
   curl http://localhost:8081/metrics
   ```

3. Check metrics sidecar logs:
   ```bash
   docker-compose logs user-service-metrics-sidecar
   ```

## Production Considerations

While this is a learning project, here are considerations for production:

1. **Use Established Tools**: Replace custom sidecars with production-grade tools:
   - Logging: Fluentd, Fluent Bit, Vector, Filebeat
   - Metrics: Prometheus, OpenTelemetry Collector

2. **Add Security**: Implement authentication, TLS, and secure communication

3. **Resource Limits**: Set memory and CPU limits for containers

4. **Persistent Storage**: Use persistent volumes for the log aggregator

5. **Monitoring**: Add health checks and alerting

6. **Service Mesh**: Consider using Istio or Linkerd for production-grade sidecars

## Further Reading

- [Kubernetes Sidecar Pattern](https://kubernetes.io/docs/concepts/workloads/pods/#workload-resources-for-managing-pods)
- [Service Mesh Architecture](https://istio.io/latest/docs/concepts/)
- [The Twelve-Factor App](https://12factor.net/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Structured Logging](https://www.structlog.org/en/stable/why.html)

## License

This project is for educational purposes.

## Contributing

Feel free to submit issues or pull requests to improve this educational project!