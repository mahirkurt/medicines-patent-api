#!/bin/bash

# Patent Database API Test Script
# Usage: ./test-api.sh [API_URL]
# Example: ./test-api.sh https://your-app.railway.app

API_URL="${1:-http://localhost:3005}"

echo "========================================"
echo "Patent Database API Test Suite"
echo "========================================"
echo "Testing API at: $API_URL"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name=$1
    local endpoint=$2
    local expected_status=${3:-200}

    echo -n "Testing $name... "

    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL$endpoint")

    if [ "$response" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $response, expected $expected_status)"
        return 1
    fi
}

# Counter for results
PASS=0
FAIL=0

# Run tests
echo "1. Basic Endpoints"
echo "-------------------"

if test_endpoint "Root endpoint" "/"; then ((PASS++)); else ((FAIL++)); fi
if test_endpoint "Health check" "/health"; then ((PASS++)); else ((FAIL++)); fi
if test_endpoint "Statistics" "/api/statistics"; then ((PASS++)); else ((FAIL++)); fi

echo ""
echo "2. Patent Endpoints"
echo "-------------------"

if test_endpoint "Patent search" "/api/patents/search?q=cancer&limit=5"; then ((PASS++)); else ((FAIL++)); fi
if test_endpoint "Patent search with filters" "/api/patents/search?q=aspirin&company=pfizer"; then ((PASS++)); else ((FAIL++)); fi
if test_endpoint "Patents by drug" "/api/patents/drug/remdesivir"; then ((PASS++)); else ((FAIL++)); fi
if test_endpoint "Patents by company" "/api/patents/company/pfizer"; then ((PASS++)); else ((FAIL++)); fi

echo ""
echo "3. Drug Endpoints"
echo "-------------------"

if test_endpoint "Drug search" "/api/drugs/search?q=aspirin&limit=5"; then ((PASS++)); else ((FAIL++)); fi
if test_endpoint "Drug search with filters" "/api/drugs/search?q=cancer&phase=Launched"; then ((PASS++)); else ((FAIL++)); fi
if test_endpoint "Drugs by indication" "/api/drugs/search?indication=cancer"; then ((PASS++)); else ((FAIL++)); fi
if test_endpoint "Drugs by company" "/api/drugs/search?company=pfizer"; then ((PASS++)); else ((FAIL++)); fi

echo ""
echo "4. Analysis Endpoints"
echo "-------------------"

if test_endpoint "Patent landscape" "/api/analysis/patent-landscape"; then ((PASS++)); else ((FAIL++)); fi
if test_endpoint "Patent landscape (2024)" "/api/analysis/patent-landscape?year=2024"; then ((PASS++)); else ((FAIL++)); fi
if test_endpoint "Drug pipeline" "/api/analysis/drug-pipeline"; then ((PASS++)); else ((FAIL++)); fi
if test_endpoint "Expiry timeline" "/api/analysis/expiry-timeline"; then ((PASS++)); else ((FAIL++)); fi

echo ""
echo "5. Detailed Data Tests"
echo "-------------------"

# Get first drug ID
DRUG_ID=$(curl -s "$API_URL/api/drugs/search?limit=1" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
if [ -n "$DRUG_ID" ]; then
    if test_endpoint "Drug detail" "/api/drugs/$DRUG_ID"; then ((PASS++)); else ((FAIL++)); fi
else
    echo -e "${RED}✗ FAIL${NC} - Could not get drug ID"
    ((FAIL++))
fi

# Get first patent ID
PATENT_ID=$(curl -s "$API_URL/api/patents/search?limit=1" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
if [ -n "$PATENT_ID" ]; then
    if test_endpoint "Patent detail" "/api/patents/$PATENT_ID"; then ((PASS++)); else ((FAIL++)); fi
else
    echo -e "${RED}✗ FAIL${NC} - Could not get patent ID"
    ((FAIL++))
fi

echo ""
echo "6. Performance Tests"
echo "-------------------"

# Measure response time
echo -n "Response time (health)... "
TIME=$(curl -s -o /dev/null -w "%{time_total}" "$API_URL/health")
echo "${TIME}s"

echo -n "Response time (search)... "
TIME=$(curl -s -o /dev/null -w "%{time_total}" "$API_URL/api/patents/search?q=cancer&limit=10")
echo "${TIME}s"

echo ""
echo "========================================"
echo "Test Results"
echo "========================================"
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
TOTAL=$((PASS + FAIL))
echo "Total: $TOTAL"

SUCCESS_RATE=$((PASS * 100 / TOTAL))
echo "Success Rate: $SUCCESS_RATE%"

echo ""
if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed! ✗${NC}"
    exit 1
fi