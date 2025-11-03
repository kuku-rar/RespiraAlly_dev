#!/bin/bash
set -euo pipefail

# API Contract Test Runner
# This script runs API contract tests in a clean Docker environment
# Philosophy: "不污染系統,使用正確的工具" - Linus Torvalds

echo "🚀 RespiraAlly API Contract Test Runner"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TEST_IMAGE="respirally-test:latest"
CONTAINER_NAME="respirally-api-test"

# Parse arguments
VERBOSE=false
COVERAGE=false
STOP_ON_FAIL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -x|--stop-on-fail)
            STOP_ON_FAIL=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -v, --verbose       Run tests with verbose output"
            echo "  -c, --coverage      Generate coverage report"
            echo "  -x, --stop-on-fail  Stop on first test failure"
            echo "  -h, --help          Show this help message"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Function to cleanup
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
}

# Set trap for cleanup
trap cleanup EXIT

# Step 1: Build test Docker image
echo "📦 Step 1: Building test Docker image..."
echo "----------------------------------------"

cat > "$SCRIPT_DIR/Dockerfile.test" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables for testing
ENV FLASK_ENV=testing
ENV TESTING=1

CMD ["pytest", "tests/", "-v"]
EOF

docker build -f "$SCRIPT_DIR/Dockerfile.test" -t "$TEST_IMAGE" "$SCRIPT_DIR" 2>&1 | tail -20

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker image built successfully${NC}"
echo ""

# Step 2: Run tests in Docker container
echo "🧪 Step 2: Running API contract tests..."
echo "----------------------------------------"

# Build pytest command
PYTEST_CMD="pytest tests/"

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=app --cov-report=term-missing --cov-report=html:htmlcov"
fi

if [ "$STOP_ON_FAIL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -x"
fi

# Run tests
docker run --name "$CONTAINER_NAME" \
    --rm \
    -e TESTING=1 \
    -e FLASK_ENV=testing \
    "$TEST_IMAGE" \
    $PYTEST_CMD

TEST_EXIT_CODE=$?

echo ""
echo "=========================================="

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "📊 Test Summary:"
    echo "  - Total tests: Check output above"
    echo "  - Status: PASSED"
    echo "  - Coverage: $([ "$COVERAGE" = true ] && echo "Generated in htmlcov/" || echo "Not generated (use -c flag)")"
else
    echo -e "${RED}❌ Tests failed with exit code: $TEST_EXIT_CODE${NC}"
    echo ""
    echo "💡 Debugging tips:"
    echo "  1. Check test output above for errors"
    echo "  2. Run with --verbose flag for more details"
    echo "  3. Use --stop-on-fail to stop at first failure"
fi

echo "=========================================="

exit $TEST_EXIT_CODE
