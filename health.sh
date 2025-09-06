#!/bin/bash

# Health check script for Nano Banana Hackathon
# This script checks the status of both frontend and backend services

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_URL="http://localhost:3000"
BACKEND_URL="http://localhost:8000"
BACKEND_STATUS_URL="http://localhost:8000/status"
BACKEND_HEALTH_URL="http://localhost:8000/health"

echo -e "${BLUE}🍌 Nano Banana Hackathon - Health Check${NC}"
echo "================================================"
echo ""

# Function to check if a URL is accessible
check_url() {
    local url=$1
    local service_name=$2
    local timeout=5
    
    if curl -s --max-time $timeout "$url" > /dev/null 2>&1; then
        echo -e "✅ ${GREEN}$service_name${NC}: ${GREEN}ONLINE${NC} ($url)"
        return 0
    else
        echo -e "❌ ${RED}$service_name${NC}: ${RED}OFFLINE${NC} ($url)"
        return 1
    fi
}

# Function to get detailed backend status
get_backend_status() {
    local response=$(curl -s --max-time 5 "$BACKEND_STATUS_URL" 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        echo -e "📊 ${BLUE}Backend Details:${NC}"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    else
        echo -e "${YELLOW}⚠️  Could not retrieve detailed backend status${NC}"
    fi
}

# Check Frontend
echo -e "${BLUE}🔍 Checking Frontend...${NC}"
frontend_status=0
check_url "$FRONTEND_URL" "Frontend (Next.js)" || frontend_status=1

echo ""

# Check Backend
echo -e "${BLUE}🔍 Checking Backend...${NC}"
backend_status=0
check_url "$BACKEND_URL" "Backend (FastAPI)" || backend_status=1

# Check Backend Health Endpoint
if [ $backend_status -eq 0 ]; then
    echo ""
    echo -e "${BLUE}🔍 Checking Backend Health Endpoint...${NC}"
    health_response=$(curl -s --max-time 5 "$BACKEND_HEALTH_URL" 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$health_response" ]; then
        echo -e "✅ ${GREEN}Health Endpoint${NC}: ${GREEN}RESPONDING${NC}"
        echo "   Response: $health_response"
    else
        echo -e "❌ ${RED}Health Endpoint${NC}: ${RED}NOT RESPONDING${NC}"
    fi
    
    # Get detailed status
    echo ""
    get_backend_status
fi

echo ""
echo "================================================"

# Summary
if [ $frontend_status -eq 0 ] && [ $backend_status -eq 0 ]; then
    echo -e "🎉 ${GREEN}All services are running!${NC}"
    echo -e "   Frontend: ${GREEN}http://localhost:3000${NC}"
    echo -e "   Backend:  ${GREEN}http://localhost:8000${NC}"
    echo -e "   API Docs: ${GREEN}http://localhost:8000/docs${NC}"
    exit 0
else
    echo -e "⚠️  ${YELLOW}Some services are not running:${NC}"
    [ $frontend_status -ne 0 ] && echo -e "   ❌ Frontend is offline"
    [ $backend_status -ne 0 ] && echo -e "   ❌ Backend is offline"
    echo ""
    echo -e "${BLUE}💡 To start the services, run:${NC}"
    echo -e "   ${YELLOW}./start.sh${NC} or ${YELLOW}python start.py${NC}"
    exit 1
fi
