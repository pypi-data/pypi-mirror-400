#!/usr/bin/env bash

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TESTS_DIR="$PROJECT_ROOT/tests"

# Default options
RUN_UNIT=true
RUN_INTEGRATION=false
VERBOSE=false
COVERAGE=false
SHOW_SLOW=false
PARALLEL=false
MARKERS=""
SPECIFIC_TEST=""
FAIL_FAST=false
STDOUT=false

# Usage function
usage() {
    cat <<EOF
${CYAN}════════════════════════════════════════════════════════════════════${NC}
${CYAN}                    Vi SDK Test Runner${NC}
${CYAN}════════════════════════════════════════════════════════════════════${NC}

${GREEN}USAGE:${NC}
    $0 [OPTIONS]

${GREEN}OPTIONS:${NC}
    ${YELLOW}-h, --help${NC}              Show this help message
    ${YELLOW}-u, --unit${NC}              Run unit tests only (default)
    ${YELLOW}-i, --integration${NC}       Run integration tests only
    ${YELLOW}-a, --all${NC}               Run all tests (unit + integration)
    ${YELLOW}-v, --verbose${NC}           Run tests in verbose mode
    ${YELLOW}-c, --coverage${NC}          Run with coverage report
    ${YELLOW}-s, --show-slow${NC}         Show slow tests (durations)
    ${YELLOW}-S, --stdout${NC}            Enable printing to stdout (disable capture)
    ${YELLOW}-p, --parallel${NC}          Run tests in parallel
    ${YELLOW}-m, --marker MARKER${NC}     Run tests with specific marker
    ${YELLOW}-t, --test PATH${NC}         Run specific test file or function
    ${YELLOW}-f, --fail-fast${NC}         Stop on first failure
    ${YELLOW}--no-unit${NC}               Skip unit tests
    ${YELLOW}--no-integration${NC}        Skip integration tests

${GREEN}MARKERS:${NC}
    ${BLUE}unit${NC}                      Unit tests (with mocks)
    ${BLUE}integration${NC}               Integration tests (live API)
    ${BLUE}slow${NC}                      Slow-running tests
    ${BLUE}auth${NC}                      Authentication tests
    ${BLUE}validation${NC}                Validation tests
    ${BLUE}error${NC}                     Error handling tests
    ${BLUE}network${NC}                   Network/HTTP tests
    ${BLUE}client${NC}                    Client tests
    ${BLUE}dataset${NC}                   Dataset tests
    ${BLUE}asset${NC}                     Asset tests
    ${BLUE}model${NC}                     Model tests
    ${BLUE}flow${NC}                      Flow tests
    ${BLUE}run${NC}                       Run tests

${GREEN}EXAMPLES:${NC}
    # Run all unit tests
    $0 --unit

    # Run all tests with coverage
    $0 --all --coverage

    # Run integration tests in verbose mode
    $0 --integration --verbose

    # Run specific test file
    $0 --test tests/unit/test_auth.py

    # Run tests with marker
    $0 --marker auth --verbose

    # Run all tests in parallel with coverage
    $0 --all --parallel --coverage

    # Run only asset tests
    $0 --marker asset

${CYAN}════════════════════════════════════════════════════════════════════${NC}
EOF
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
    -h | --help)
        usage
        ;;
    -u | --unit)
        RUN_UNIT=true
        RUN_INTEGRATION=false
        shift
        ;;
    -i | --integration)
        RUN_UNIT=false
        RUN_INTEGRATION=true
        shift
        ;;
    -a | --all)
        RUN_UNIT=true
        RUN_INTEGRATION=true
        shift
        ;;
    -v | --verbose)
        VERBOSE=true
        shift
        ;;
    -c | --coverage)
        COVERAGE=true
        shift
        ;;
    -s | --show-slow)
        SHOW_SLOW=true
        shift
        ;;
    -S | --stdout)
        STDOUT=true
        shift
        ;;
    -p | --parallel)
        PARALLEL=true
        shift
        ;;
    -m | --marker)
        MARKERS="$2"
        shift 2
        ;;
    -t | --test)
        SPECIFIC_TEST="$2"
        shift 2
        ;;
    -f | --fail-fast)
        FAIL_FAST=true
        shift
        ;;
    --no-unit)
        RUN_UNIT=false
        shift
        ;;
    --no-integration)
        RUN_INTEGRATION=false
        shift
        ;;
    *)
        echo -e "${RED}Error: Unknown option $1${NC}"
        echo "Use -h or --help for usage information"
        exit 1
        ;;
    esac
done

# Print header
print_header() {
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                    Vi SDK Test Runner${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Print section
print_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Check if pytest is installed
check_pytest() {
    if ! command -v pytest &>/dev/null; then
        echo -e "${RED}Error: pytest is not installed${NC}"
        echo "Please install test dependencies:"
        echo "  pip install -e \".[dev]\""
        exit 1
    fi
}

# Check if in project root
check_directory() {
    if [[ ! -f "$PROJECT_ROOT/pyproject.toml" ]]; then
        echo -e "${RED}Error: Not in project root directory${NC}"
        echo "Please run this script from the project root or ci directory"
        exit 1
    fi
}

# Build pytest command
build_pytest_cmd() {
    local cmd="pytest"
    local target="$1"

    # Add target path
    cmd="$cmd $target"

    # Add verbose flag
    if [[ "$VERBOSE" == true ]]; then
        cmd="$cmd -v"
    fi

    # Add coverage flags
    if [[ "$COVERAGE" == true ]]; then
        cmd="$cmd --cov=vi --cov-report=term-missing --cov-report=html --cov-report=xml"
    fi

    # Add slow tests flag
    if [[ "$SHOW_SLOW" == true ]]; then
        cmd="$cmd --durations=10"
    fi

    # Add stdout flag (disable output capture)
    if [[ "$STDOUT" == true ]]; then
        cmd="$cmd -s"
    fi

    # Add parallel flag
    if [[ "$PARALLEL" == true ]]; then
        cmd="$cmd -n auto"
    fi

    # Add marker flag
    if [[ -n "$MARKERS" ]]; then
        cmd="$cmd -m \"$MARKERS\""
    fi

    # Add fail-fast flag
    if [[ "$FAIL_FAST" == true ]]; then
        cmd="$cmd -x"
    fi

    # Add color and output options
    cmd="$cmd --color=yes --tb=short"

    echo "$cmd"
}

# Run tests
run_tests() {
    local test_type="$1"
    local test_path="$2"

    print_section "$test_type"

    local cmd
    if [[ -n "$SPECIFIC_TEST" ]]; then
        cmd=$(build_pytest_cmd "$SPECIFIC_TEST")
    else
        cmd=$(build_pytest_cmd "$test_path")
    fi

    echo -e "${GREEN}Running:${NC} $cmd"
    echo ""

    cd "$PROJECT_ROOT"

    # Execute command
    if eval "$cmd"; then
        echo ""
        echo -e "${GREEN}✓ $test_type PASSED${NC}"
        return 0
    else
        echo ""
        echo -e "${RED}✗ $test_type FAILED${NC}"
        return 1
    fi
}

# Main execution
main() {
    print_header

    # Checks
    check_pytest
    check_directory

    # Configuration summary
    echo -e "${CYAN}Configuration:${NC}"
    echo "  Project Root: $PROJECT_ROOT"
    echo "  Tests Dir: $TESTS_DIR"
    echo "  Unit Tests: $RUN_UNIT"
    echo "  Integration Tests: $RUN_INTEGRATION"
    echo "  Verbose: $VERBOSE"
    echo "  Coverage: $COVERAGE"
    echo "  Show Slow: $SHOW_SLOW"
    echo "  Stdout: $STDOUT"
    echo "  Parallel: $PARALLEL"
    echo "  Fail Fast: $FAIL_FAST"
    [[ -n "$MARKERS" ]] && echo "  Markers: $MARKERS"
    [[ -n "$SPECIFIC_TEST" ]] && echo "  Specific Test: $SPECIFIC_TEST"

    local exit_code=0

    # Run unit tests
    if [[ "$RUN_UNIT" == true ]] && [[ -z "$SPECIFIC_TEST" ]]; then
        if ! run_tests "Unit Tests" "$TESTS_DIR/unit/"; then
            exit_code=1
            if [[ "$FAIL_FAST" == true ]]; then
                exit $exit_code
            fi
        fi
    fi

    # Run integration tests
    if [[ "$RUN_INTEGRATION" == true ]] && [[ -z "$SPECIFIC_TEST" ]]; then
        # Check for credentials
        if [[ -z "${DATATURE_VI_SECRET_KEY:-}" ]] && [[ ! -f "$TESTS_DIR/.test_config.json" ]]; then
            echo ""
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${YELLOW}  Warning: No credentials configured for integration tests${NC}"
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo "  Integration tests require either:"
            echo "    1. Environment variables (DATATURE_VI_SECRET_KEY, DATATURE_VI_ORGANIZATION_ID)"
            echo "    2. Config file at tests/.test_config.json"
            echo ""
            echo "  Tests will be skipped automatically."
            echo ""
        fi

        if ! run_tests "Integration Tests" "$TESTS_DIR/integrations/"; then
            exit_code=1
            if [[ "$FAIL_FAST" == true ]]; then
                exit $exit_code
            fi
        fi
    fi

    # Run specific test if provided
    if [[ -n "$SPECIFIC_TEST" ]]; then
        if ! run_tests "Specific Test" "$SPECIFIC_TEST"; then
            exit_code=1
        fi
    fi

    # Print summary
    echo ""
    print_section "Test Summary"

    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}✓ All tests passed successfully!${NC}"

        if [[ "$COVERAGE" == true ]]; then
            echo ""
            echo -e "${CYAN}Coverage reports generated:${NC}"
            echo "  - Terminal: (shown above)"
            echo "  - HTML: $PROJECT_ROOT/htmlcov/index.html"
            echo "  - XML: $PROJECT_ROOT/coverage.xml"
        fi
    else
        echo -e "${RED}✗ Some tests failed${NC}"
    fi

    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════${NC}"

    exit $exit_code
}

# Run main function
main
