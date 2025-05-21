#!/bin/bash

# Script to run API tests in Docker
# Usage: ./run_docker_tests.sh [test_type]
# test_type: all, health, paths, api (default: all)

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}     REPPORT API TESTING SUITE         ${NC}"
echo -e "${BLUE}========================================${NC}"

# Determine which tests to run
TEST_TYPE=${1:-all}

# Ensure containers are running
echo -e "${BLUE}Checking if Docker containers are running...${NC}"
CONTAINERS_RUNNING=$(docker ps --filter "name=repport-backend" --format "{{.Names}}" | wc -l)

if [ "$CONTAINERS_RUNNING" -eq 0 ]; then
    echo -e "${RED}Docker containers are not running.${NC}"
    echo -e "${BLUE}Starting Docker containers...${NC}"
    docker-compose up -d
    echo -e "${BLUE}Waiting for containers to initialize (15 seconds)...${NC}"
    sleep 15
else
    echo -e "${GREEN}Docker containers already running.${NC}"
fi

# Function to run a test and check its success
run_test() {
    TEST_NAME=$1
    TEST_CMD=$2
    
    echo -e "\n${BLUE}Running $TEST_NAME tests...${NC}"
    echo -e "${BLUE}----------------------------------------${NC}"
    
    if $TEST_CMD; then
        echo -e "\n${GREEN}✓ $TEST_NAME tests passed${NC}"
        return 0
    else
        echo -e "\n${RED}✗ $TEST_NAME tests failed${NC}"
        return 1
    fi
}

# Keep track of test results
PASSED_TESTS=0
TOTAL_TESTS=0

# Run health tests
if [[ "$TEST_TYPE" == "all" || "$TEST_TYPE" == "health" ]]; then
    run_test "API Health" "python backend/scripts/tests/api_health_test.py"
    RESULT=$?
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    PASSED_TESTS=$((PASSED_TESTS + (1 - RESULT)))
fi

# Run path analysis
if [[ "$TEST_TYPE" == "all" || "$TEST_TYPE" == "paths" ]]; then
    run_test "API Path Analyzer" "python backend/scripts/tests/fix_api_paths.py"
    RESULT=$?
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    PASSED_TESTS=$((PASSED_TESTS + (1 - RESULT)))
fi

# Run comprehensive API tests
if [[ "$TEST_TYPE" == "all" || "$TEST_TYPE" == "api" ]]; then
    run_test "Comprehensive API" "python backend/scripts/tests/api_test.py"
    RESULT=$?
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    PASSED_TESTS=$((PASSED_TESTS + (1 - RESULT)))
fi

# Print summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}             TEST SUMMARY              ${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Tests run: $TOTAL_TESTS"
echo -e "Tests passed: $PASSED_TESTS"

if [ "$PASSED_TESTS" -eq "$TOTAL_TESTS" ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi 