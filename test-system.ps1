# Test Script for Centralized Logging and Metrics Collection System

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing Sidecar Pattern Implementation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to test HTTP endpoint
function Test-Endpoint {
    param(
        [string]$Url,
        [string]$Description
    )
    
    Write-Host "Testing: $Description" -ForegroundColor Yellow
    Write-Host "URL: $Url" -ForegroundColor Gray
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method Get -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ SUCCESS" -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ FAILED (Status: $($response.StatusCode))" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "✗ FAILED (Error: $($_.Exception.Message))" -ForegroundColor Red
        return $false
    }
    Write-Host ""
}

# Function to generate load
function Generate-Load {
    param([string]$ServiceName, [int]$Port)
    
    Write-Host "Generating load on $ServiceName..." -ForegroundColor Yellow
    
    # Health check
    Invoke-WebRequest -Uri "http://localhost:$Port/health" -Method Get -UseBasicParsing | Out-Null
    
    # Service-specific endpoints
    switch ($ServiceName) {
        "user-service" {
            Invoke-WebRequest -Uri "http://localhost:$Port/users" -Method Get -UseBasicParsing | Out-Null
            Invoke-WebRequest -Uri "http://localhost:$Port/users/1" -Method Get -UseBasicParsing | Out-Null
            Invoke-WebRequest -Uri "http://localhost:$Port/users/2" -Method Get -UseBasicParsing | Out-Null
        }
        "product-service" {
            Invoke-WebRequest -Uri "http://localhost:$Port/products" -Method Get -UseBasicParsing | Out-Null
            Invoke-WebRequest -Uri "http://localhost:$Port/products/1" -Method Get -UseBasicParsing | Out-Null
            Invoke-WebRequest -Uri "http://localhost:$Port/products/2" -Method Get -UseBasicParsing | Out-Null
        }
        "order-service" {
            Invoke-WebRequest -Uri "http://localhost:$Port/orders" -Method Get -UseBasicParsing | Out-Null
            Invoke-WebRequest -Uri "http://localhost:$Port/orders/1" -Method Get -UseBasicParsing | Out-Null
            Invoke-WebRequest -Uri "http://localhost:$Port/orders/2" -Method Get -UseBasicParsing | Out-Null
        }
    }
    
    Write-Host "✓ Load generated for $ServiceName" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Step 1: Testing Application Services" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Test-Endpoint "http://localhost:8081/health" "User Service Health"
Test-Endpoint "http://localhost:8082/health" "Product Service Health"
Test-Endpoint "http://localhost:8083/health" "Order Service Health"
Write-Host ""

Write-Host "Step 2: Testing Metrics Endpoints" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

Test-Endpoint "http://localhost:9091/metrics" "User Service Metrics (Sidecar)"
Test-Endpoint "http://localhost:9092/metrics" "Product Service Metrics (Sidecar)"
Test-Endpoint "http://localhost:9093/metrics" "Order Service Metrics (Sidecar)"
Write-Host ""

Write-Host "Step 3: Testing Log Aggregator" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

Test-Endpoint "http://localhost:8000/health" "Log Aggregator Health"
Write-Host ""

Write-Host "Step 4: Generating Application Load" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

Generate-Load "user-service" 8081
Generate-Load "product-service" 8082
Generate-Load "order-service" 8083

Write-Host "Waiting 5 seconds for logs to be forwarded..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Write-Host ""

Write-Host "Step 5: Checking Aggregated Logs" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

try {
    $logCountResponse = Invoke-RestMethod -Uri "http://localhost:8000/logs/count" -Method Get
    Write-Host "Total logs collected: $($logCountResponse.total_logs)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Logs by service:" -ForegroundColor Yellow
    foreach ($service in $logCountResponse.by_service.PSObject.Properties) {
        Write-Host "  - $($service.Name): $($service.Value)" -ForegroundColor White
    }
    Write-Host ""
} catch {
    Write-Host "✗ Failed to get log count: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Write-Host "Step 6: Sample Enriched Metrics" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

try {
    $metricsResponse = Invoke-WebRequest -Uri "http://localhost:9091/metrics" -Method Get -UseBasicParsing
    $metricsLines = $metricsResponse.Content -split "`n"
    Write-Host "Sample metrics from user-service (enriched by sidecar):" -ForegroundColor Yellow
    $metricsLines | Select-Object -First 15 | ForEach-Object {
        Write-Host "  $_" -ForegroundColor White
    }
    Write-Host ""
} catch {
    Write-Host "✗ Failed to get metrics: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Commands to explore further:" -ForegroundColor Yellow
Write-Host "  View all logs:           curl http://localhost:8000/logs" -ForegroundColor White
Write-Host "  View user service logs:  curl http://localhost:8000/logs?service=user-service" -ForegroundColor White
Write-Host "  View container logs:     docker-compose logs -f" -ForegroundColor White
Write-Host "  Stop system:             docker-compose down" -ForegroundColor White
Write-Host ""
