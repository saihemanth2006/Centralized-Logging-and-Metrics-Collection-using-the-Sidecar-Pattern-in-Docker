.PHONY: help build up down logs test clean restart ps health

# Default target
help:
	@echo "Centralized Logging and Metrics Collection - Sidecar Pattern"
	@echo ""
	@echo "Available commands:"
	@echo "  make build     - Build all Docker images"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - Tail logs from all services"
	@echo "  make ps        - Show running containers"
	@echo "  make test      - Run system tests"
	@echo "  make health    - Check health of all services"
	@echo "  make clean     - Stop services and remove volumes"
	@echo ""

# Build all images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d
	@echo ""
	@echo "All services started!"
	@echo "Access points:"
	@echo "  - Log Aggregator:  http://localhost:8000"
	@echo "  - User Service:    http://localhost:8081"
	@echo "  - Product Service: http://localhost:8082"
	@echo "  - Order Service:   http://localhost:8083"
	@echo ""
	@echo "Run 'make logs' to view logs or 'make test' to test the system"

# Stop all services
down:
	docker-compose down

# Restart all services
restart: down up

# View logs
logs:
	docker-compose logs -f

# Show running containers
ps:
	docker-compose ps

# Run tests
test:
	@echo "Running system tests..."
	@if [ -f test-system.sh ]; then \
		chmod +x test-system.sh; \
		./test-system.sh; \
	else \
		echo "Test script not found. Run manually with: ./test-system.sh or .\\test-system.ps1"; \
	fi

# Check health of services
health:
	@echo "Checking service health..."
	@echo ""
	@echo "User Service:"
	@curl -s http://localhost:8081/health | grep -q "healthy" && echo "  ✓ Healthy" || echo "  ✗ Unhealthy"
	@echo ""
	@echo "Product Service:"
	@curl -s http://localhost:8082/health | grep -q "healthy" && echo "  ✓ Healthy" || echo "  ✗ Unhealthy"
	@echo ""
	@echo "Order Service:"
	@curl -s http://localhost:8083/health | grep -q "healthy" && echo "  ✓ Healthy" || echo "  ✗ Unhealthy"
	@echo ""
	@echo "Log Aggregator:"
	@curl -s http://localhost:8000/health | grep -q "healthy" && echo "  ✓ Healthy" || echo "  ✗ Unhealthy"
	@echo ""

# Clean up everything including volumes
clean:
	docker-compose down -v
	@echo "Cleaned up all containers and volumes"
