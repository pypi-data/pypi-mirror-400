# Test Runner Scripts

## run-all-tests.sh

Comprehensive test runner that handles all setup and execution automatically.

### Quick Start

```bash
# Run all tests (full setup + C extension build)
./scripts/run-all-tests.sh

# Quick mode: pure Python tests only (fastest, no C build)
./scripts/run-all-tests.sh --quick
```

### Options

```text
--quick          Run only pure Python tests (no C extension needed)
--setup-only     Only setup, don't run tests
--skip-build     Skip C extension build
--clean          Clean everything and start fresh
--help           Show help message
```

### What It Does

1. **Checks dependencies**: uv, pkg-config, NSS, NSPR
2. **Creates virtual environment**: Using uv
3. **Installs dependencies**: pytest, hypothesis, mypy, etc.
4. **Builds C extension**: Compiles NSS/NSPR bindings (if not --quick)
5. **Sets up certificates**: Creates test PKI database (if C extension built)
6. **Runs tests**: All tests or pure Python only

### Examples

```bash
# First time setup + run all tests
./scripts/run-all-tests.sh

# Fast iteration during development (pure Python only)
./scripts/run-all-tests.sh --quick

# Just setup the environment, don't run tests
./scripts/run-all-tests.sh --setup-only

# Clean everything and start fresh
./scripts/run-all-tests.sh --clean

# Build C extension but skip running tests
./scripts/run-all-tests.sh --setup-only
```

### Requirements

- **uv**: Fast Python package manager
  - Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **NSS/NSPR**: Required for full tests (optional for --quick mode)
  - macOS: `brew install nss nspr`
  - Linux: `sudo apt-get install libnss3-dev libnspr4-dev`

### Exit Codes

- `0`: All tests passed
- `1`: Some tests failed
- `>1`: Setup error

### Logs

Build and setup logs are saved to `/tmp/`:

- `/tmp/nss-build.log`: C extension build output
- `/tmp/nss-certs.log`: Certificate setup output

---

**Last Updated**: January 2025
