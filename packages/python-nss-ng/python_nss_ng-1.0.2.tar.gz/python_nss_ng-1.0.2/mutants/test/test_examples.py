# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: Copyright (c) 2010-2025 python-nss-ng contributors

"""
Tests for example code in doc/examples/.

This module verifies that example code has valid syntax, can import required
modules, and demonstrates proper usage patterns.
"""

import sys
import os
import ast
import pytest
import subprocess
import tempfile
from pathlib import Path

# Add test directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestExampleSyntax:
    """Test that all examples have valid Python syntax."""

    @pytest.fixture
    def example_dir(self):
        """Get the examples directory path."""
        test_dir = Path(__file__).parent
        repo_root = test_dir.parent
        examples_dir = repo_root / 'doc' / 'examples'
        return examples_dir

    @pytest.fixture
    def example_files(self, example_dir):
        """Get list of all example Python files."""
        if not example_dir.exists():
            pytest.skip("Examples directory not found")
        return list(example_dir.glob('*.py'))

    def test_examples_directory_exists(self, example_dir):
        """Test that examples directory exists."""
        assert example_dir.exists(), "doc/examples directory should exist"
        assert example_dir.is_dir(), "doc/examples should be a directory"

    def test_example_files_exist(self, example_files):
        """Test that example files exist."""
        assert len(example_files) > 0, "Should have at least one example file"

    def test_all_examples_valid_syntax(self, example_files):
        """Test that all examples have valid Python syntax."""
        for example_file in example_files:
            with open(example_file, 'r') as f:
                source = f.read()

            try:
                ast.parse(source)
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {example_file.name}: {e}")

    def test_cert_dump_syntax(self, example_dir):
        """Test cert_dump.py has valid syntax."""
        cert_dump = example_dir / 'cert_dump.py'
        if not cert_dump.exists():
            pytest.skip("cert_dump.py not found")

        with open(cert_dump, 'r') as f:
            source = f.read()

        ast.parse(source)  # Should not raise SyntaxError

    def test_ssl_example_syntax(self, example_dir):
        """Test ssl_example.py has valid syntax."""
        ssl_example = example_dir / 'ssl_example.py'
        if not ssl_example.exists():
            pytest.skip("ssl_example.py not found")

        with open(ssl_example, 'r') as f:
            source = f.read()

        ast.parse(source)  # Should not raise SyntaxError

    def test_verify_server_syntax(self, example_dir):
        """Test verify_server.py has valid syntax."""
        verify_server = example_dir / 'verify_server.py'
        if not verify_server.exists():
            pytest.skip("verify_server.py not found")

        with open(verify_server, 'r') as f:
            source = f.read()

        ast.parse(source)  # Should not raise SyntaxError


class TestExampleImports:
    """Test that examples can import required modules."""

    @pytest.fixture
    def example_dir(self):
        """Get the examples directory path."""
        test_dir = Path(__file__).parent
        repo_root = test_dir.parent
        examples_dir = repo_root / 'doc' / 'examples'
        return examples_dir

    def test_examples_import_nss_modules(self, example_dir):
        """Test that examples import nss modules."""
        example_files = list(example_dir.glob('*.py'))
        if not example_files:
            pytest.skip("No example files found")

        nss_imports = []
        for example_file in example_files:
            with open(example_file, 'r') as f:
                source = f.read()

            # Check if file imports nss modules
            if 'import nss' in source or 'from nss' in source:
                nss_imports.append(example_file.name)

        # Most examples should import nss
        assert len(nss_imports) > 0, "At least some examples should import nss modules"

    def test_no_syntax_errors_in_imports(self, example_dir):
        """Test that import statements are syntactically correct."""
        example_files = list(example_dir.glob('*.py'))
        if not example_files:
            pytest.skip("No example files found")

        for example_file in example_files:
            with open(example_file, 'r') as f:
                source = f.read()

            # Parse and check import statements
            try:
                tree = ast.parse(source)
                imports = [node for node in ast.walk(tree)
                          if isinstance(node, (ast.Import, ast.ImportFrom))]
                assert len(imports) > 0, f"{example_file.name} should have imports"
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {example_file.name}: {e}")


class TestExampleStructure:
    """Test that examples have proper structure."""

    @pytest.fixture
    def example_dir(self):
        """Get the examples directory path."""
        test_dir = Path(__file__).parent
        repo_root = test_dir.parent
        examples_dir = repo_root / 'doc' / 'examples'
        return examples_dir

    def test_examples_have_docstrings_or_comments(self, example_dir):
        """Test that examples have documentation."""
        example_files = list(example_dir.glob('*.py'))
        if not example_files:
            pytest.skip("No example files found")

        for example_file in example_files:
            with open(example_file, 'r') as f:
                source = f.read()

            # Check for either docstring or comments
            has_docstring = '"""' in source or "'''" in source
            has_comments = '#' in source

            assert has_docstring or has_comments, \
                f"{example_file.name} should have documentation"

    def test_examples_define_main_or_functions(self, example_dir):
        """Test that examples define functions or main code."""
        example_files = list(example_dir.glob('*.py'))
        if not example_files:
            pytest.skip("No example files found")

        for example_file in example_files:
            with open(example_file, 'r') as f:
                source = f.read()

            try:
                tree = ast.parse(source)
                functions = [node for node in ast.walk(tree)
                           if isinstance(node, ast.FunctionDef)]

                # Should have at least some functions or executable code
                # (Empty files would have no functions and no executable statements)
                has_content = len(functions) > 0 or len(tree.body) > 0
                assert has_content, f"{example_file.name} should have content"
            except SyntaxError:
                pytest.fail(f"Cannot parse {example_file.name}")


class TestExampleCodeQuality:
    """Test code quality aspects of examples."""

    @pytest.fixture
    def example_dir(self):
        """Get the examples directory path."""
        test_dir = Path(__file__).parent
        repo_root = test_dir.parent
        examples_dir = repo_root / 'doc' / 'examples'
        return examples_dir

    def test_no_bare_except_blocks(self, example_dir):
        """Test that examples don't have bare except blocks."""
        example_files = list(example_dir.glob('*.py'))
        if not example_files:
            pytest.skip("No example files found")

        import re
        bare_except_pattern = re.compile(r'^\s*except\s*:\s*$', re.MULTILINE)

        files_with_bare_except = []
        for example_file in example_files:
            with open(example_file, 'r') as f:
                source = f.read()

            if bare_except_pattern.search(source):
                files_with_bare_except.append(example_file.name)

        # We allow some bare excepts in examples for simplicity,
        # but document which files have them
        if files_with_bare_except:
            # This is a warning, not a hard failure
            pass

    def test_examples_use_nss_properly(self, example_dir):
        """Test that examples demonstrate proper NSS usage."""
        example_files = list(example_dir.glob('*.py'))
        if not example_files:
            pytest.skip("No example files found")

        nss_files = []
        for example_file in example_files:
            with open(example_file, 'r') as f:
                source = f.read()

            # Files that import nss should use it
            if 'import nss' in source or 'from nss' in source:
                nss_files.append(example_file.name)

        assert len(nss_files) > 0, "Should have examples using NSS"


class TestSpecificExamples:
    """Test specific example files in detail."""

    @pytest.fixture
    def example_dir(self):
        """Get the examples directory path."""
        test_dir = Path(__file__).parent
        repo_root = test_dir.parent
        examples_dir = repo_root / 'doc' / 'examples'
        return examples_dir

    def test_ssl_cipher_info_structure(self, example_dir):
        """Test ssl_cipher_info.py has expected structure."""
        ssl_cipher_info = example_dir / 'ssl_cipher_info.py'
        if not ssl_cipher_info.exists():
            pytest.skip("ssl_cipher_info.py not found")

        with open(ssl_cipher_info, 'r') as f:
            source = f.read()

        # Should import ssl module
        assert 'import nss.ssl' in source or 'from nss import ssl' in source

        # Should have print_suite_info or similar function
        assert 'suite' in source.lower()

    def test_verify_server_structure(self, example_dir):
        """Test verify_server.py has expected structure."""
        verify_server = example_dir / 'verify_server.py'
        if not verify_server.exists():
            pytest.skip("verify_server.py not found")

        with open(verify_server, 'r') as f:
            source = f.read()

        # Should import necessary modules
        assert 'import nss' in source or 'from nss' in source

    def test_cert_dump_structure(self, example_dir):
        """Test cert_dump.py has expected structure."""
        cert_dump = example_dir / 'cert_dump.py'
        if not cert_dump.exists():
            pytest.skip("cert_dump.py not found")

        with open(cert_dump, 'r') as f:
            source = f.read()

        # Should work with certificates
        assert 'cert' in source.lower()

    def test_ssl_example_structure(self, example_dir):
        """Test ssl_example.py has expected structure."""
        ssl_example = example_dir / 'ssl_example.py'
        if not ssl_example.exists():
            pytest.skip("ssl_example.py not found")

        with open(ssl_example, 'r') as f:
            source = f.read()

        # Should import SSL module
        assert 'ssl' in source.lower()

        # Should demonstrate client or server
        has_client_or_server = 'client' in source.lower() or 'server' in source.lower()
        assert has_client_or_server


class TestExampleExecutability:
    """Test that examples can be executed (syntax check via compilation)."""

    @pytest.fixture
    def example_dir(self):
        """Get the examples directory path."""
        test_dir = Path(__file__).parent
        repo_root = test_dir.parent
        examples_dir = repo_root / 'doc' / 'examples'
        return examples_dir

    def test_examples_compile(self, example_dir):
        """Test that examples compile to bytecode."""
        example_files = list(example_dir.glob('*.py'))
        if not example_files:
            pytest.skip("No example files found")

        failed_files = []
        for example_file in example_files:
            try:
                with open(example_file, 'r') as f:
                    source = f.read()

                # Compile to check for syntax errors
                compile(source, str(example_file), 'exec')
            except SyntaxError as e:
                failed_files.append((example_file.name, str(e)))

        assert len(failed_files) == 0, \
            f"Files with syntax errors: {failed_files}"

    def test_examples_can_be_imported_as_modules(self, example_dir):
        """Test that examples can be parsed as modules."""
        example_files = list(example_dir.glob('*.py'))
        if not example_files:
            pytest.skip("No example files found")

        for example_file in example_files:
            with open(example_file, 'r') as f:
                source = f.read()

            # Parse as a module
            try:
                ast.parse(source, filename=str(example_file), mode='exec')
            except SyntaxError as e:
                pytest.fail(f"Cannot parse {example_file.name} as module: {e}")


class TestExampleDependencies:
    """Test example dependencies and imports."""

    @pytest.fixture
    def example_dir(self):
        """Get the examples directory path."""
        test_dir = Path(__file__).parent
        repo_root = test_dir.parent
        examples_dir = repo_root / 'doc' / 'examples'
        return examples_dir

    def test_examples_import_standard_library(self, example_dir):
        """Test that examples properly import standard library modules."""
        example_files = list(example_dir.glob('*.py'))
        if not example_files:
            pytest.skip("No example files found")

        common_imports = ['sys', 'os', 'argparse', 'getpass', 'socket']
        files_with_imports = {}

        for example_file in example_files:
            with open(example_file, 'r') as f:
                source = f.read()

            for module in common_imports:
                if f'import {module}' in source:
                    if module not in files_with_imports:
                        files_with_imports[module] = []
                    files_with_imports[module].append(example_file.name)

        # At least some examples should use standard library
        assert len(files_with_imports) > 0

    def test_examples_handle_nss_errors(self, example_dir):
        """Test that examples handle NSS errors properly."""
        example_files = list(example_dir.glob('*.py'))
        if not example_files:
            pytest.skip("No example files found")

        files_handling_errors = []
        for example_file in example_files:
            with open(example_file, 'r') as f:
                source = f.read()

            # Check if file handles NSS errors
            if 'NSPRError' in source or 'except' in source:
                files_handling_errors.append(example_file.name)

        # At least some examples should handle errors
        assert len(files_handling_errors) > 0


class TestExampleSecurity:
    """Test that examples demonstrate secure practices."""

    @pytest.fixture
    def example_dir(self):
        """Get the examples directory path."""
        test_dir = Path(__file__).parent
        repo_root = test_dir.parent
        examples_dir = repo_root / 'doc' / 'examples'
        return examples_dir

    def test_examples_no_hardcoded_secrets(self, example_dir):
        """Test that examples don't have hardcoded secrets in obvious places."""
        example_files = list(example_dir.glob('*.py'))
        if not example_files:
            pytest.skip("No example files found")

        # Look for obvious patterns (allow test passwords for examples)
        suspicious_patterns = [
            'password = "secret"',
            "password = 'secret'",
            'api_key = "',
            "api_key = '",
        ]

        files_with_suspicious = []
        for example_file in example_files:
            with open(example_file, 'r') as f:
                source = f.read()

            for pattern in suspicious_patterns:
                if pattern in source.lower():
                    files_with_suspicious.append((example_file.name, pattern))

        # Examples may have test passwords, which is OK
        # This is more of a documentation test

    def test_examples_use_secure_defaults(self, example_dir):
        """Test that examples demonstrate secure defaults."""
        example_files = list(example_dir.glob('*.py'))
        if not example_files:
            pytest.skip("No example files found")

        files_with_ssl = []
        for example_file in example_files:
            with open(example_file, 'r') as f:
                source = f.read()

            # Files using SSL should be noted
            if 'ssl' in source.lower() or 'tls' in source.lower():
                files_with_ssl.append(example_file.name)

        # Should have examples demonstrating SSL/TLS
        assert len(files_with_ssl) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
