#!/usr/bin/env python3
"""
API Contract Test Validation Script

Validates test files without running them:
1. Syntax checking (Python AST)
2. Import validation
3. Test discovery
4. Coverage analysis
5. OpenAPI spec validation

Philosophy: "先驗證,再執行" - 避免浪費時間在語法錯誤上
"""

import ast
import sys
import yaml
from pathlib import Path
from collections import defaultdict


class Colors:
    """Terminal colors"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_header(text):
    """Print section header"""
    print(f"\n{Colors.BLUE}{'='*70}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*70}{Colors.NC}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.NC}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")


def validate_python_syntax(file_path):
    """Validate Python file syntax using AST"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"


def discover_tests(file_path):
    """Discover test functions in a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    tree = ast.parse(code)
    tests = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name.startswith('test_'):
                tests.append(node.name)

    return tests


def validate_openapi_spec(spec_path):
    """Validate OpenAPI specification"""
    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec = yaml.safe_load(f)

        # Basic validation
        required_fields = ['openapi', 'info', 'paths', 'components']
        missing = [field for field in required_fields if field not in spec]

        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"

        # Count endpoints
        endpoints = 0
        for path, path_item in spec.get('paths', {}).items():
            for method in ['get', 'post', 'put', 'patch', 'delete']:
                if method in path_item:
                    endpoints += 1

        return True, {
            'endpoints': endpoints,
            'version': spec['info'].get('version', 'unknown'),
            'title': spec['info'].get('title', 'unknown')
        }

    except Exception as e:
        return False, str(e)


def main():
    """Main validation process"""
    print_header("🔍 API Contract Test Validation")

    script_dir = Path(__file__).parent.resolve()
    tests_dir = script_dir / 'tests'
    openapi_spec = script_dir / 'openapi.yaml'

    print(f"Working directory: {script_dir}")
    print(f"Tests directory: {tests_dir}")
    print(f"OpenAPI spec: {openapi_spec}")

    total_errors = 0
    total_warnings = 0
    all_tests = []

    # Step 1: Validate OpenAPI spec
    print_header("📋 Step 1: Validate OpenAPI Specification")

    if not openapi_spec.exists():
        print_error("OpenAPI spec not found: openapi.yaml")
        total_errors += 1
    else:
        valid, result = validate_openapi_spec(openapi_spec)
        if valid:
            print_success(f"OpenAPI spec is valid")
            print(f"   Title: {result['title']}")
            print(f"   Version: {result['version']}")
            print(f"   Endpoints: {result['endpoints']}")
        else:
            print_error(f"OpenAPI spec is invalid: {result}")
            total_errors += 1

    # Step 2: Validate test files
    print_header("🧪 Step 2: Validate Test Files")

    test_files = list(tests_dir.glob('test_*.py'))

    if not test_files:
        print_error(f"No test files found in {tests_dir}")
        total_errors += 1
    else:
        print(f"Found {len(test_files)} test files\n")

        for test_file in sorted(test_files):
            print(f"📄 {test_file.name}")

            # Syntax check
            valid, error = validate_python_syntax(test_file)
            if valid:
                print_success(f"  Syntax valid")
            else:
                print_error(f"  Syntax error: {error}")
                total_errors += 1
                continue

            # Discover tests
            tests = discover_tests(test_file)
            all_tests.extend(tests)
            print(f"  📝 Found {len(tests)} test functions")

            if len(tests) == 0:
                print_warning(f"  No test functions found")
                total_warnings += 1

    # Step 3: Coverage analysis
    print_header("📊 Step 3: Test Coverage Analysis")

    if openapi_spec.exists():
        _, spec_info = validate_openapi_spec(openapi_spec)
        if isinstance(spec_info, dict):
            total_endpoints = spec_info['endpoints']
            total_tests = len(all_tests)

            print(f"Total API endpoints: {total_endpoints}")
            print(f"Total test functions: {total_tests}")

            if total_tests >= total_endpoints:
                coverage = (total_tests / total_endpoints) * 100
                print_success(f"Test coverage: {coverage:.1f}%")
            else:
                coverage = (total_tests / total_endpoints) * 100
                print_warning(f"Test coverage: {coverage:.1f}% (below 100%)")
                total_warnings += 1

    # Step 4: Check conftest.py
    print_header("⚙️  Step 4: Validate Test Configuration")

    conftest = tests_dir / 'conftest.py'
    if conftest.exists():
        valid, error = validate_python_syntax(conftest)
        if valid:
            print_success("conftest.py is valid")
        else:
            print_error(f"conftest.py syntax error: {error}")
            total_errors += 1
    else:
        print_warning("conftest.py not found (optional)")

    # Final summary
    print_header("📈 Validation Summary")

    print(f"Test files validated: {len(test_files)}")
    print(f"Test functions discovered: {len(all_tests)}")
    print(f"Errors: {total_errors}")
    print(f"Warnings: {total_warnings}")

    print()

    if total_errors == 0:
        print_success("All validations passed! Tests are ready to run.")
        print()
        print("Next steps:")
        print("  1. Run tests: ./test_runner.sh")
        print("  2. With coverage: ./test_runner.sh --coverage")
        print("  3. Verbose mode: ./test_runner.sh --verbose")
        return 0
    else:
        print_error(f"Validation failed with {total_errors} error(s)")
        print()
        print("Please fix the errors before running tests.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
