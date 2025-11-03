#!/bin/bash
set -euo pipefail

# Quick Test Runner - 使用現有開發環境執行測試
# Philosophy: "實用主義 - 使用已有的資源" - Linus Torvalds

echo "🚀 Quick API Contract Test Runner"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
CONTAINER_NAME="dev_web_app_service"
TEST_PATH="/app/tests"

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${RED}❌ Container $CONTAINER_NAME is not running${NC}"
    echo ""
    echo "Please start the development environment:"
    echo "  cd ../../"
    echo "  docker-compose up -d"
    exit 1
fi

echo -e "${GREEN}✅ Found running container: $CONTAINER_NAME${NC}"
echo ""

# Step 1: Static validation first
echo "📋 Step 1: Static Validation"
echo "----------------------------"
python3 validate_tests.py
VALIDATION_EXIT=$?

if [ $VALIDATION_EXIT -ne 0 ]; then
    echo -e "${RED}❌ Static validation failed${NC}"
    exit $VALIDATION_EXIT
fi

echo ""

# Step 2: Run tests in container
echo "🧪 Step 2: Running Tests in Container"
echo "--------------------------------------"

# Install test dependencies in container if needed
echo "Installing test dependencies..."
docker exec $CONTAINER_NAME pip install pytest pytest-cov pyyaml --quiet 2>&1 | tail -3

echo ""
echo "Executing tests..."
docker exec $CONTAINER_NAME pytest tests/ -v --tb=short

TEST_EXIT=$?

echo ""
echo "===================================="

if [ $TEST_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Tests failed with exit code: $TEST_EXIT${NC}"
fi

echo "===================================="

exit $TEST_EXIT
