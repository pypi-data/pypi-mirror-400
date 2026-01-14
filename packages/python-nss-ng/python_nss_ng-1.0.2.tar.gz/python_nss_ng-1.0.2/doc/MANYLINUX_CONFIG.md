<!--
SPDX-License-Identifier: MPL-2.0
SPDX-FileCopyrightText: 2025 The Linux Foundation
-->

# Manylinux Configuration

## Overview

This document describes the manylinux platform tag configuration for
python-nss-ng wheel builds. The project uses `auditwheel` to repair wheels
for broad PyPI and pip compatibility across different Linux distributions.

## What is Manylinux?

Manylinux is a standard for building Python wheels that work across
Linux distributions. Different manylinux versions target different base
glibc versions:

| Tag              | glibc Version | Compatible Distributions           |
| ---------------- | ------------- | ---------------------------------- |
| `manylinux2014`  | 2.17          | RHEL 7+, Ubuntu 14.04+, Debian 8+  |
| `manylinux_2_28` | 2.28          | RHEL 8+, Ubuntu 20.04+, Debian 11+ |
| `manylinux_2_34` | 2.34          | RHEL 9+, Ubuntu 22.04+, Fedora 35+ |

## Current Configuration

python-nss-ng uses **manylinux_2_34** (glibc 2.34+) for wheel
builds. This provides compatibility with:

- Ubuntu 22.04 LTS and newer
- Fedora 35 and newer
- RHEL 9 and newer
- Debian 12 and newer

### Why manylinux_2_34?

The project builds against NSS 3.117+ which requires modern system libraries.
Using manylinux_2_34:

- ✅ Ensures compatibility with modern NSS/NSPR libraries
- ✅ Targets current LTS distributions (Ubuntu 22.04+)
- ✅ Provides good balance of compatibility and modernity
- ✅ Aligns with Fedora's NSS 3.117+ needs

## Build Configuration

### GitHub Actions Workflow

The workflow files configure the manylinux version:

**File**: `.github/workflows/build-test-release.yaml`

```yaml
- name: "Build Python project"
  uses: modeseven-lfreleng-actions/python-build-action@refactor-build-action
  with:
    auditwheel: true
    manylinux_version: manylinux_2_34
    build_formats: wheel
```

**File**: `.github/workflows/build-test.yaml`

```yaml
- name: "Build Python project"
  uses: modeseven-lfreleng-actions/python-build-action@refactor-build-action
  with:
    auditwheel: true
    manylinux_version: manylinux_2_34
```

### Build Action Parameters

The `python-build-action` accepts two parameters for wheel repair:

#### `auditwheel`

- **Type**: boolean
- **Default**: `false`
- **Description**: Enable/disable auditwheel wheel repair
- **Usage**: Set to `true` to repair wheels for manylinux compatibility
- **python-nss-ng setting**: `true`

#### `manylinux_version`

- **Type**: string
- **Default**: `manylinux2014`
- **Description**: Target manylinux platform tag
- **Valid values**:
  - `manylinux2014` - glibc 2.17+
  - `manylinux_2_28` - glibc 2.28+
  - `manylinux_2_34` - glibc 2.34+
  - `manylinux_2_35` - glibc 2.35+
- **python-nss-ng setting**: `manylinux_2_34`

## Changing the Manylinux Version

### For More Compatibility (Older Systems)

If you need wheels to work on older distributions, edit the workflow files:

```yaml
with:
  auditwheel: true
  manylinux_version: manylinux_2_28  # glibc 2.28+
```

**Note**: This may require building against older NSS/NSPR versions. NSS
3.117+ may not be available on older distributions.

### For Newer Systems

If you target recent distributions:

```yaml
with:
  auditwheel: true
  manylinux_version: manylinux_2_35  # glibc 2.35+
```

### Disabling Auditwheel

To build wheels without manylinux tags (not recommended for PyPI):

```yaml
with:
  auditwheel: false
```

This will produce wheels with platform-specific tags like
`linux_x86_64.whl` which PyPI will reject.

## How Auditwheel Works

When enabled, auditwheel:

1. **Analyzes** the wheel to check library dependencies
2. **Repairs** the wheel by:
   - Bundling necessary shared libraries into the wheel
   - Updating the platform tag to manylinux_*
   - Ensuring glibc compatibility
3. **Validates** that the wheel meets manylinux standards

### Auditwheel Process

```bash
# What happens during build:
auditwheel show python_nss_ng-*.whl
auditwheel repair python_nss_ng-*.whl \
  --plat-name manylinux_2_34 \
  -w wheelhouse/
```

### If Auditwheel Fails

The build action has fallback behavior:

- If `auditwheel repair` fails, the action keeps the original wheel
- The action logs a warning but the build continues
- This allows the action to build wheels even if repair isn't possible

## Verification

### Check Wheel Platform Tag

After building, verify the wheel has the correct tag:

```bash
# Wheel filename should contain the manylinux tag:
python_nss_ng-0.1.0-cp310-cp310-manylinux_2_34_x86_64.whl
                            ^^^^^^^^^^^^^^^^
```

### Check Wheel Contents

```bash
# Check for bundled NSS/NSPR libraries:
unzip -l python_nss_ng-*.whl | grep "\.so"
```

Should show bundled shared libraries for NSS/NSPR if the action included them.

### Test on Target System

```bash
# On Ubuntu 22.04 or Fedora 35+:
pip install python_nss_ng-*.whl
python -c "import nss.nss; print(nss.nss.nss_get_version())"
```

Expected output: NSS version string (e.g., "3.117.0")

## PyPI Requirements

PyPI requires specific platform tags:

- ✅ **Accepted**: `manylinux_*` tags
- ❌ **Rejected**: `linux_*` tags
- ❌ **Rejected**: Platform-specific tags without manylinux

**Always use auditwheel** when building wheels for PyPI distribution.

## Troubleshooting

### Wheel Rejected by PyPI

**Error**: "Invalid platform tag"

**Solution**: Ensure you set `auditwheel: true` in the workflow files.

### Incompatible with Older Systems

**Error**: "ImportError: /lib64/libc.so.6: version 'GLIBC_2.34' not found"

**Cause**: Wheel built with `manylinux_2_34` installed on system with glibc <
2.34.

**Solution**: Build with an older manylinux version:

```yaml
manylinux_version: manylinux_2_28
```

Or document the base OS needs in README.

### Auditwheel Repair Fails

**Error**: "cannot repair to manylinux_2_34"

**Possible causes**:

1. NSS/NSPR libraries depend on symbols not in target glibc
2. NSS/NSPR version too new for the target
3. Missing library dependencies

**Solutions**:

- Check NSS/NSPR library versions in build environment
- Try a newer manylinux version: `manylinux_2_35`
- Build NSS/NSPR from source with appropriate compatibility flags
- Verify NSS/NSPR pkg-config configuration

### NSS Library Not Found at Runtime

**Error**: "ImportError: libnss3.so: cannot open shared object file"

**Cause**: NSS libraries not bundled in wheel or not in system library path.

**Solution**: Auditwheel should bundle NSS/NSPR libraries. Check:

```bash
unzip -l python_nss_ng-*.whl | grep libnss
```

If libraries are missing, auditwheel may have failed. Check CI logs.

## Architecture Support

The project supports both x86_64 and aarch64 (ARM64):

```yaml
strategy:
  matrix:
    arch: ['x86_64', 'aarch64']
```

Auditwheel handles both architectures automatically, producing:

- `manylinux_2_34_x86_64.whl`
- `manylinux_2_34_aarch64.whl`

## Testing Matrix

The project tests wheels on:

| Platform      | Arch    | Python Versions             |
| ------------- | ------- | --------------------------- |
| Fedora Latest | x86_64  | 3.9, 3.10, 3.11, 3.12, 3.14 |
| Fedora Latest | aarch64 | 3.9, 3.10, 3.11, 3.12, 3.14 |
| macOS Latest  | arm64   | 3.9, 3.10, 3.11, 3.12, 3.13 |

macOS wheels don't use manylinux tags (they use macosx_* tags).

## NSS/NSPR Compatibility

### Base Versions

- **NSS**: 3.100+ (3.117+ recommended)
- **NSPR**: 4.35+

### Library Detection

The build process uses pkg-config to find NSS/NSPR:

```bash
pkg-config --modversion nss
pkg-config --modversion nspr
```

### Custom Library Paths

If NSS/NSPR are in non-standard locations, set environment variable:

```bash
export NSS_INCLUDE_ROOTS="/custom/path/include:/another/path/include"
```

## Distribution-Specific Notes

### Ubuntu 22.04 LTS

- ✅ Ships with glibc 2.35 (compatible with manylinux_2_34)
- ✅ NSS 3.68+ in repositories
- ⚠️ May need to build NSS from source for 3.117+

### Fedora 35+

- ✅ Ships with NSS 3.117+
- ✅ glibc 2.34+
- ✅ Fully compatible out of the box

### RHEL 9

- ✅ Ships with glibc 2.34
- ✅ NSS 3.79+
- ⚠️ May need newer NSS for full feature support

### Debian 12

- ✅ Ships with glibc 2.36
- ✅ NSS 3.87+
- ⚠️ May need NSS update for 3.117+

## References

- [PEP 600 -- Future manylinux platform tags](https://peps.python.org/pep-0600/)
- [PEP 599 -- manylinux2014 platform tag](https://peps.python.org/pep-0599/)
- [Auditwheel Documentation](https://github.com/pypa/auditwheel)
<!-- markdownlint-disable-next-line MD013 -->
- [Python Packaging User Guide](https://packaging.python.org/guides/distributing-packages-using-setuptools/#platform-wheels)
- [NSS Documentation](https://firefox-source-docs.mozilla.org/security/nss/)
<!-- markdownlint-disable-next-line MD013 -->
- [python-build-action Manylinux Docs](https://github.com/modeseven-lfreleng-actions/python-build-action/blob/main/docs/MANYLINUX_CONFIG.md)

## Summary

- **Current Setting**: `manylinux_2_34` (glibc 2.34+)
- **Auditwheel**: Enabled in all release and test builds
- **Rationale**: Balance modern NSS 3.117+ requirements with broad
  compatibility
- **Supported Platforms**: x86_64 and aarch64
- **Base OS**: Ubuntu 22.04, Fedora 35, RHEL 9, Debian 12
- **NSS Version**: 3.100+ required, 3.117+ recommended
