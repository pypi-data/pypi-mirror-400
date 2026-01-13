#!/bin/bash
#
# Test All Scripts
#
# Runs all MuleSoft developer scripts against example projects
# to verify they work correctly.
#

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
EXAMPLES_DIR="$SCRIPT_DIR"

# Detect Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python not found. Please install Python 3.7+"
    exit 1
fi

echo "🧪 Testing All MuleSoft Developer Scripts"
echo "Using: $PYTHON_CMD"
echo "=========================================="
echo ""

PASSED=0
FAILED=0

test_script() {
    local script_name=$1
    local command=$2
    local expected_exit=$3
    
    echo -n "Testing $script_name... "
    
    if eval "$command" > /tmp/test_output.log 2>&1; then
        ACTUAL_EXIT=0
    else
        ACTUAL_EXIT=$?
    fi
    
    if [ "$ACTUAL_EXIT" -eq "$expected_exit" ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (expected exit $expected_exit, got $ACTUAL_EXIT)"
        echo "  Command: $command"
        echo "  Output:"
        head -5 /tmp/test_output.log | sed 's/^/    /'
        ((FAILED++))
        return 1
    fi
}

# Test Config Validator - Good Project (should pass)
test_script "Config Validator (good project)" \
    "cd $PROJECT_ROOT/config-validator && $PYTHON_CMD validate-properties.py --project-path $EXAMPLES_DIR/sample-mule-project" \
    0

# Test Config Validator - Bad Project (should fail)
test_script "Config Validator (bad project)" \
    "cd $PROJECT_ROOT/config-validator && $PYTHON_CMD validate-properties.py --project-path $EXAMPLES_DIR/sample-mule-project-with-issues" \
    1

# Test Security Scanner - Bad Project (should find issues)
test_script "Security Scanner (bad project)" \
    "cd $PROJECT_ROOT/security-scanner && $PYTHON_CMD secret-scan.py --path $EXAMPLES_DIR/sample-mule-project-with-issues --format json" \
    0

# Test API Validator - Good Project (warnings are OK, no errors)
test_script "API Validator (good project)" \
    "cd $PROJECT_ROOT/api-validator && $PYTHON_CMD raml-vs-flow-check.py --project-path $EXAMPLES_DIR/sample-mule-project --format json" \
    0

# Test MUnit Analyzer - Good Project
test_script "MUnit Analyzer (good project)" \
    "cd $PROJECT_ROOT/munit-analyzer && $PYTHON_CMD munit-coverage.py --project-path $EXAMPLES_DIR/sample-mule-project --format json" \
    0

# Test Log Analyzer - Sample Logs (should find issues - that's the point!)
test_script "Log Analyzer (sample logs)" \
    "cd $PROJECT_ROOT/log-analyzer && $PYTHON_CMD analyze-logs.py $EXAMPLES_DIR/sample-logs/application.log --format json" \
    1

# Test Runtime Diagnostics - Good Project
test_script "Runtime Diagnostics (good project)" \
    "cd $PROJECT_ROOT/runtime-diagnostics && bash mule-runtime-check.sh $EXAMPLES_DIR/sample-mule-project --format json" \
    0

# Test Help Commands (should all work)
echo ""
echo "Testing help commands..."
for script in \
    "$PROJECT_ROOT/config-validator/validate-properties.py" \
    "$PROJECT_ROOT/security-scanner/secret-scan.py" \
    "$PROJECT_ROOT/api-validator/raml-vs-flow-check.py" \
    "$PROJECT_ROOT/munit-analyzer/munit-coverage.py" \
    "$PROJECT_ROOT/log-analyzer/analyze-logs.py"; do
    if $PYTHON_CMD "$script" --help > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $(basename $script) --help"
        ((PASSED++))
    else
        echo -e "  ${RED}✗${NC} $(basename $script) --help"
        ((FAILED++))
    fi
done

# Summary
echo ""
echo "=========================================="
echo "Test Summary:"
echo -e "  ${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "  ${RED}Failed: $FAILED${NC}"
    exit 1
else
    echo -e "  ${GREEN}Failed: $FAILED${NC}"
    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
fi

