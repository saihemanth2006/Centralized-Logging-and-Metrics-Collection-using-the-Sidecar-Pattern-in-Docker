#!/bin/bash

# Test Script for Centralized Logging and Metrics Collection System

echo "========================================"
echo "Testing Sidecar Pattern Implementation"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to test HTTP endpoint
test_endpoint() {
    local url=$1
    local description=$2
    
    echo -e "${YELLOW}Testing: ${description}${NC}"
    echo -e "URL: ${url}"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$response" -eq 200 ]; then
        echo -e "${GREEN}✓ SUCCESS${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED (Status: ${response})${NC}"
        return 1
    fi
    echo ""
}

# Function to generate load
generate_load() {
    local service_name=$1
    local port=$2
    
    echo -e "${YELLOW}Generating load on ${service_name}...${NC}"
    
    # Health check
    curl -s "http://localhost:${port}/health" > /dev/null
    
    # Service-specific endpoints
    case $service_name in
        "user-service")
            curl -s "http://localhost:${port}/users" > /dev/null
            curl -s "http://localhost:${port}/users/1" > /dev/null
            curl -s "http://localhost:${port}/users/2" > /dev/null
            ;;
        "product-service")
            curl -s "http://localhost:${port}/products" > /dev/null
            curl -s "http://localhost:${port}/products/1" > /dev/null
            curl -s "http://localhost:${port}/products/2" > /dev/null
            ;;
        "order-service")
            curl -s "http://localhost:${port}/orders" > /dev/null
            curl -s "http://localhost:${port}/orders/1" > /dev/null
            curl -s "http://localhost:${port}/orders/2" > /dev/null
            ;;
    esac
    
    echo -e "${GREEN}✓ Load generated for ${service_name}${NC}"
    echo ""
}

echo -e "${CYAN}Step 1: Testing Application Services${NC}"
echo "====================================="
echo ""

test_endpoint "http://localhost:8081/health" "User Service Health"
test_endpoint "http://localhost:8082/health" "Product Service Health"
test_endpoint "http://localhost:8083/health" "Order Service Health"
echo ""

echo -e "${CYAN}Step 2: Testing Metrics Endpoints${NC}"
echo "=================================="
echo ""

test_endpoint "http://localhost:9091/metrics" "User Service Metrics (Sidecar)"
test_endpoint "http://localhost:9092/metrics" "Product Service Metrics (Sidecar)"
test_endpoint "http://localhost:9093/metrics" "Order Service Metrics (Sidecar)"
echo ""

echo -e "${CYAN}Step 3: Testing Log Aggregator${NC}"
echo "=============================="
echo ""

test_endpoint "http://localhost:8000/health" "Log Aggregator Health"
echo ""

echo -e "${CYAN}Step 4: Generating Application Load${NC}"
echo "===================================="
echo ""

generate_load "user-service" 8081
generate_load "product-service" 8082
generate_load "order-service" 8083

echo -e "${YELLOW}Waiting 5 seconds for logs to be forwarded...${NC}"
sleep 5
echo ""

echo -e "${CYAN}Step 5: Checking Aggregated Logs${NC}"
echo "================================="
echo ""

log_count=$(curl -s "http://localhost:8000/logs/count")
echo -e "${GREEN}Log count response:${NC}"
echo "$log_count" | jq '.'
echo ""

echo -e "${CYAN}Step 6: Sample Enriched Metrics${NC}"
echo "================================"
echo ""

echo -e "${YELLOW}Sample metrics from user-service (enriched by sidecar):${NC}"
curl -s "http://localhost:9091/metrics" | head -n 15
echo ""

echo "========================================"
echo "Test Complete!"
echo "========================================"
echo ""
echo -e "${YELLOW}Commands to explore further:${NC}"
echo "  View all logs:           curl http://localhost:8000/logs | jq '.'"
echo "  View user service logs:  curl http://localhost:8000/logs?service=user-service | jq '.'"
echo "  View container logs:     docker-compose logs -f"
echo "  Stop system:             docker-compose down"
echo ""
