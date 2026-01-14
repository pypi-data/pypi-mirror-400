#!/usr/bin/env bash
# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation

set -euo pipefail

#==============================================================================
# Comprehensive Test Runner for python-nss-ng
#==============================================================================
#
# This script handles all setup and runs all tests locally, including:
# - Checking dependencies (uv, NSS, NSPR)
# - Creating virtual environment
# - Installing test dependencies
# - Building C extension
# - Setting up test certificates
# - Running all tests (pure Python and NSS-dependent)
#
# Usage:
#   ./scripts/run-all-tests.sh [OPTIONS]
#
# Options:
#   --quick          Run only pure Python tests (no C extension needed)
#   --setup-only     Only setup, don't run tests
#   --skip-build     Skip C extension build
#   --rebuild        Clean build artifacts and rebuild C extension
#   --clean          Clean everything and start fresh
#   --help           Show this help message
#
#==============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Options
QUICK_MODE=false
SETUP_ONLY=false
SKIP_BUILD=false
CLEAN_MODE=false
REBUILD_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --setup-only)
            SETUP_ONLY=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --rebuild)
            REBUILD_MODE=true
            shift
            ;;
        --clean)
            CLEAN_MODE=true
            shift
            ;;
        --help)
            grep "^#" "$0" | grep -v "#!/" | sed 's/^# //'
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Helper functions
print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Clean mode
if [ "$CLEAN_MODE" = true ]; then
    print_header "Cleaning everything"

    print_info "Removing virtual environment..."
    rm -rf .venv

    print_info "Removing build artifacts..."
    rm -rf build/ dist/ ./*.egg-info .pytest_cache .coverage htmlcov/

    print_info "Removing test certificates..."
    rm -rf pki/

    print_info "Removing Python cache..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true

    print_success "Clean complete!"
    exit 0
fi

# Start
print_header "python-nss-ng Test Runner"
echo "Repository: $(pwd)"
echo "Mode: $([ "$QUICK_MODE" = true ] && echo "Quick (Pure Python only)" || echo "Full")"
echo ""

#==============================================================================
# Step 1: Check Dependencies
#==============================================================================
print_header "Step 1/6: Checking Dependencies"

# Check uv
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed!"
    echo ""
    echo "Please install uv:"
    echo "  macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  Or visit: https://github.com/astral-sh/uv"
    exit 1
else
    print_success "uv found: $(uv --version)"
fi

# Check pkg-config (needed to find NSS)
if ! command -v pkg-config &> /dev/null; then
    print_warning "pkg-config not found (needed for NSS detection)"
    if [ "$QUICK_MODE" = false ]; then
        echo ""
        echo "For full tests, install pkg-config:"
        echo "  macOS: brew install pkg-config"
        echo "  Linux: sudo apt-get install pkg-config"
        echo ""
        print_info "Continuing in quick mode (pure Python tests only)..."
        QUICK_MODE=true
    fi
else
    print_success "pkg-config found"
fi

# Check NSS/NSPR (only if not in quick mode)
if [ "$QUICK_MODE" = false ]; then
    if pkg-config --exists nss 2>/dev/null; then
        NSS_VERSION=$(pkg-config --modversion nss)
        print_success "NSS found: version $NSS_VERSION"
    else
        print_warning "NSS not found!"
        echo ""
        echo "For full tests, install NSS:"
        echo "  macOS: brew install nss"
        echo "  Linux: sudo apt-get install libnss3-dev libnspr4-dev"
        echo ""
        print_info "Switching to quick mode (pure Python tests only)..."
        QUICK_MODE=true
    fi
fi

#==============================================================================
# Step 2: Setup Virtual Environment
#==============================================================================
print_header "Step 2/6: Virtual Environment"

if [ ! -d ".venv" ]; then
    print_info "Creating virtual environment with uv..."
    uv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
# shellcheck source=/dev/null
source .venv/bin/activate
print_success "Virtual environment activated"

#==============================================================================
# Step 3: Install Dependencies
#==============================================================================
print_header "Step 3/6: Installing Dependencies"

print_info "Installing test dependencies with uv..."
uv pip install pytest pytest-cov pytest-timeout pytest-xdist hypothesis mypy

if [ "$QUICK_MODE" = false ] && [ "$SKIP_BUILD" = false ]; then
    print_info "Installing build dependencies..."
    uv pip install meson-python meson ninja
fi

print_success "Dependencies installed"

#==============================================================================
# Step 4: Build C Extension (if needed)
#==============================================================================
if [ "$QUICK_MODE" = false ] && [ "$SKIP_BUILD" = false ]; then
    print_header "Step 4/6: Building C Extension"

    # Clean build artifacts if rebuild mode is enabled
    if [ "$REBUILD_MODE" = true ]; then
        print_info "Cleaning build artifacts for clean rebuild..."
        rm -rf build/ dist/ ./*.egg-info
        rm -rf .venv/lib/python*/site-packages/nss*
        print_success "Build artifacts cleaned"
    fi

    print_info "Building python-nss-ng C extension..."
    # Use regular install (not editable) to avoid rebuild issues
    if uv pip install --force-reinstall --no-deps . 2>&1 | tee /tmp/nss-build.log; then
        print_success "C extension built and installed successfully"
        C_EXTENSION_BUILT=true
    else
        print_error "C extension build failed!"
        print_warning "Falling back to pure Python tests only"
        QUICK_MODE=true
        C_EXTENSION_BUILT=false
    fi
else
    print_header "Step 4/6: Skipping C Extension Build"
    print_info "Running in quick mode or build skipped"
    C_EXTENSION_BUILT=false
fi

#==============================================================================
# Step 5: Setup Test Certificates (if C extension built)
#==============================================================================
if [ "$C_EXTENSION_BUILT" = true ]; then
    print_header "Step 5/6: Setting Up Test Certificates"

    if [ ! -d "pki" ]; then
        print_info "Creating test certificate database..."
        if python test/setup_certs.py 2>&1 | tee /tmp/nss-certs.log; then
            print_success "Test certificates created"
        else
            print_warning "Certificate setup had warnings (check /tmp/nss-certs.log)"
            print_info "Tests may still work without system CA certs"
        fi
    else
        print_success "Test certificates already exist"
    fi
else
    print_header "Step 5/6: Skipping Certificate Setup"
    print_info "Not needed for pure Python tests"
fi

#==============================================================================
# Step 6: Run Tests
#==============================================================================
if [ "$SETUP_ONLY" = false ]; then
    print_header "Step 6/6: Running Tests"

    if [ "$QUICK_MODE" = true ]; then
        print_info "Running pure Python tests (no C extension needed)..."
        echo ""

        pytest test/test_deprecations.py \
               test/test_secure_logging.py \
               test/test_examples.py \
               test/test_util.py \
               test/test_type_hints.py \
               test/test_documentation_accuracy.py \
               test/test_property_based.py \
               test/test_thread_safety.py \
               -v --tb=short --color=yes

        TEST_EXIT_CODE=$?
    else
        print_info "Running ALL tests (including NSS-dependent)..."
        echo ""

        # Run tests serially for reliability with stable order
        # -p no:randomly disables test randomization to prevent NSS state corruption
        pytest test/ -n0 -p no:randomly -v --tb=short --color=yes

        TEST_EXIT_CODE=$?
    fi

    # Summary
    echo ""
    print_header "Test Summary"

    if [ $TEST_EXIT_CODE -eq 0 ]; then
        print_success "All tests passed!"
    else
        print_error "Some tests failed (exit code: $TEST_EXIT_CODE)"
        exit $TEST_EXIT_CODE
    fi
else
    print_header "Step 6/6: Skipping Tests (setup only)"
    print_success "Setup complete!"
fi

#==============================================================================
# Final Summary
#==============================================================================
echo ""
print_header "Summary"

echo "Environment:"
echo "  Virtual env: .venv/"
echo "  Python: $(python --version)"
echo "  Mode: $([ "$QUICK_MODE" = true ] && echo "Quick (Pure Python)" || echo "Full (with NSS)")"
echo ""

if [ "$SETUP_ONLY" = false ]; then
    echo "Tests completed successfully!"
else
    echo "Setup completed successfully!"
    echo ""
    echo "To run tests:"
    echo "  source .venv/bin/activate"
    if [ "$QUICK_MODE" = true ]; then
        echo "  pytest test/test_deprecations.py test/test_secure_logging.py \\"
        echo "         test/test_examples.py test/test_util.py \\"
        echo "         test/test_type_hints.py test/test_documentation_accuracy.py \\"
        echo "         test/test_property_based.py test/test_thread_safety.py -v"
    else
        echo "  pytest test/ -v"
    fi
fi

echo ""
print_info "For more options, run: $0 --help"
echo ""
