<!--
SPDX-License-Identifier: MPL-2.0
SPDX-FileCopyrightText: 2025 The Linux Foundation
-->

# Mutation Testing Guide

## What is Mutation Testing?

Mutation testing validates the **effectiveness** of your test suite by
intentionally introducing bugs (mutations) into the code and checking if the
tests catch them.

If a test suite passes even when the code has been "mutated" (broken), it
means your tests aren't actually verifying that behavior.

---

## Why Mutation Testing?

**Problem**: You can have 100% code coverage but still miss bugs.

**Example**:

```python
# Original code
def is_valid_key_size(size):
    return size >= 2048  # ✅ Correct

# Mutated code
def is_valid_key_size(size):
    return size > 2048   # ❌ Changed >= to >

# If tests still pass, they're not testing the boundary!
```

**Mutation testing finds these gaps.**

---

## Tools

### 1. mutmut (Recommended)

**Installation**:

```bash
pip install mutmut
```

**Basic Usage**:

```bash
# Run mutation testing on source code
mutmut run --paths-to-mutate=src/

# See results
mutmut results

# Show specific mutations
mutmut show <mutation-id>
```

### 2. cosmic-ray (Alternative)

**Installation**:

```bash
pip install cosmic-ray
```

**Usage**:

```bash
# Initialize
cosmic-ray init config.toml session.sqlite -- python -m pytest test/

# Execute
cosmic-ray exec session.sqlite

# Report
cosmic-ray report session.sqlite
```

---

## Configuration

### mutmut Configuration

Create `.mutmut-config.py` in project root:

```python
# .mutmut-config.py

def pre_mutation(context):
    """Called before each mutation."""
    pass

def post_mutation(context):
    """Called after each mutation."""
    pass
```

Or use `pyproject.toml`:

```toml
[tool.mutmut]
paths_to_mutate = "src/"
backup = false
runner = "python -m pytest -x"
tests_dir = "test/"
```

---

## Running Mutation Testing

### Quick Start

```bash
# 1. Install mutmut
pip install mutmut

# 2. Run mutation testing on a single file
mutmut run --paths-to-mutate=src/deprecations.py

# 3. Check results
mutmut results

# 4. View survivors (mutations not caught)
mutmut show
```

### Full Test Suite

```bash
# Run on all pure Python modules
mutmut run --paths-to-mutate=src/deprecations.py,src/secure_logging.py,src/nss_context.py

# Run with specific test command
mutmut run --paths-to-mutate=src/ --runner="pytest test/ -x"

# Run in parallel (faster)
mutmut run --paths-to-mutate=src/ --use-coverage
```

---

## Understanding Results

### Mutation States

- **Killed** ✅ - Test failed (caught the mutation) - GOOD
- **Survived** ❌ - Test passed (didn't catch mutation) - BAD
- **Timeout** ⏱️ - Test took too long
- **Suspicious** ⚠️ - Test passed but with warnings

### Goal

**Target**: 80%+ mutations killed

Lower than 80% means tests aren't catching bugs effectively.

---

## Common Mutations

mutmut applies these mutations:

1. **Comparison operators**: `>` → `>=`, `==` → `!=`
2. **Arithmetic operators**: `+` → `-`, `*` → `/`
3. **Boolean operators**: `and` → `or`, `not` → remove
4. **Numbers**: `0` → `1`, `1` → `0`
5. **Strings**: `"text"` → `"XXtextXX"`
6. **Return values**: `return x` → `return None`

---

## Example Session

```bash
$ mutmut run --paths-to-mutate=src/deprecations.py

- Mutation testing starting -

These are the steps:
1. A full test suite run will be made to make sure we
   can run the tests successfully and we know how long
   it takes (to detect infinite loops for example)
2. Mutants will be generated and checked

Results so far:
Survived: 3
Killed: 45
Timeout: 0
Suspicious: 0
Skipped: 2
Total: 50

$ mutmut results
To apply a mutant on disk:
    mutmut apply <id>

To show a mutant:
    mutmut show <id>

Survived 🙁 (3)

---- src/deprecations.py (3) ----
1, 5, 12

$ mutmut show 1
--- src/deprecations.py
+++ src/deprecations.py
@@ -15,7 +15,7 @@

 def is_deprecated(symbol):
     """Check if symbol is deprecated."""
-    return symbol in DEPRECATED_SYMBOLS
+    return symbol not in DEPRECATED_SYMBOLS
```

This shows a mutation that **survived** - the tests didn't catch when we
inverted the logic!

---

## Improving Test Suite Based on Mutations

### Survivor #1: Boundary Condition

**Mutation**:

```python
# Original
if size >= 2048:

# Mutated (survived)
if size > 2048:
```

**Fix**: Add boundary test

```python
def test_key_size_boundary():
    assert is_valid_key_size(2048) == True  # Exact boundary
    assert is_valid_key_size(2047) == False
```

### Survivor #2: Return Value

**Mutation**:

```python
# Original
return True

# Mutated (survived)
return None
```

**Fix**: Test return type

```python
def test_returns_boolean():
    result = some_function()
    assert isinstance(result, bool)
    assert result is True  # Not just truthy
```

### Survivor #3: Exception Type

**Mutation**:

```python
# Original
raise ValueError("Invalid")

# Mutated (survived)
raise RuntimeError("Invalid")
```

**Fix**: Test specific exception

```python
def test_raises_value_error():
    with pytest.raises(ValueError) as exc_info:
        some_function()
    assert "Invalid" in str(exc_info.value)
```

---

## Best Practices

### 1. Start Small

```bash
# Don't mutate everything at once
mutmut run --paths-to-mutate=src/deprecations.py
```

### 2. Use Coverage First

```bash
# Only mutate covered code
mutmut run --use-coverage
```

### 3. Fix Survivors Incrementally

```bash
# Show survivors
mutmut results

# Fix one at a time
mutmut show 1
# Add test
# Re-run
mutmut run --rerun-all
```

### 4. Integrate into CI

```yaml
# .github/workflows/mutation-testing.yml
name: Mutation Testing
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  mutmut:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run mutation testing
        run: |
          pip install mutmut
          mutmut run --use-coverage
          mutmut results
```

---

## For python-nss-ng

### Recommended Approach

**Phase 1**: Pure Python modules (no C compilation)

```bash
mutmut run --paths-to-mutate=src/deprecations.py \
  --runner="pytest test/test_deprecations.py -x"
mutmut run --paths-to-mutate=src/secure_logging.py \
  --runner="pytest test/test_secure_logging.py -x"
mutmut run --paths-to-mutate=src/nss_context.py \
  --runner="pytest test/test_nss_context.py -x"
```

**Phase 2**: Review survivors

```bash
mutmut results
mutmut show <id>
```

**Phase 3**: Add tests for survivors

```bash
# Add missing tests
# Re-run specific mutations
mutmut run --rerun-all
```

### Expected Results

**Good mutation score**: 75-85% killed

- Pure Python code should be easier to test
- Some mutations might be equivalent (don't change behavior)

**Areas to focus**:

- Boundary conditions
- Exception types
- Return values
- Boolean logic

---

## Limitations

### Equivalent Mutants

Some mutations don't change behavior:

```python
# Original
if x > 0:
    return True
return False

# Mutated (equivalent)
if x >= 1:  # Same for integers!
    return True
return False
```

These are **false positives** - ignore them.

### Performance

Mutation testing is **slow**:

- Each mutation requires running full test suite
- 100 mutations = 100 test suite runs

**Solutions**:

- Use `--use-coverage` to skip unmutated code
- Run in parallel
- Run on schedule, not every commit

---

## Integration with Existing Tests

### Current Test Suite

We have **317+ tests** with **100% pure Python pass rate**.

Mutation testing will validate these tests are **effective**, not just passing.

### Commands

```bash
# Quick check on one module
mutmut run --paths-to-mutate=src/deprecations.py

# Full run on all pure Python
mutmut run --paths-to-mutate=src/deprecations.py,src/secure_logging.py,src/nss_context.py

# With coverage filter
mutmut run --use-coverage --paths-to-mutate=src/
```

---

## Metrics

### Mutation Score

```text
Mutation Score = (Killed / (Killed + Survived)) × 100%
```

**Target**: 80%+

**python-nss-ng baseline** (to be measured):

- Run initial mutation testing
- Establish baseline
- Improve iteratively

---

## Resources

- **mutmut**: <https://github.com/boxed/mutmut>
- **cosmic-ray**: <https://cosmic-ray.readthedocs.io/>
- **PIT (Java)**: <https://pitest.org/> (reference implementation)
- **Stryker (JavaScript)**: <https://stryker-mutator.io/>

---

## Next Steps

1. **Install**: `pip install mutmut`
2. **Run**: `mutmut run --paths-to-mutate=src/deprecations.py`
3. **Review**: `mutmut results`
4. **Improve**: Add tests for survivors
5. **Iterate**: Re-run until 80%+ killed

---

**Last Updated**: January 2025
**Status**: Ready to use
**For Questions**: See main test documentation
