#!/usr/bin/env python3
"""
API Contract Tests Runner

This script runs all API contract tests and generates a coverage report.
It ensures that all API endpoints maintain their contracts during refactoring.

Usage:
    python run_contract_tests.py              # Run all tests
    python run_contract_tests.py --coverage   # Run with coverage report
    python run_contract_tests.py --verbose    # Run with verbose output
"""

import subprocess
import sys
import yaml
from pathlib import Path
import argparse


def load_openapi_spec():
    """載入 OpenAPI 規格"""
    spec_path = Path(__file__).parent / 'openapi.yaml'
    with open(spec_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def count_endpoints(spec):
    """統計 API 端點數量"""
    paths = spec.get('paths', {})
    endpoint_count = 0
    for path, path_item in paths.items():
        for method in ['get', 'post', 'put', 'patch', 'delete']:
            if method in path_item:
                endpoint_count += 1
    return endpoint_count


def run_tests(verbose=False, coverage=False):
    """執行測試"""
    print("🚀 啟動 API 契約測試...")
    print("=" * 70)

    # 載入 OpenAPI 規格
    spec = load_openapi_spec()
    total_endpoints = count_endpoints(spec)
    print(f"📊 OpenAPI 規格包含 {total_endpoints} 個 API 端點")
    print("=" * 70)

    # 建構 pytest 指令
    cmd = ['pytest', 'tests/']

    if verbose:
        cmd.append('-v')
    else:
        cmd.append('-q')

    if coverage:
        cmd.extend([
            '--cov=app',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov'
        ])

    # 執行測試
    print(f"\n🔧 執行指令: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=Path(__file__).parent)

    print("\n" + "=" * 70)
    if result.returncode == 0:
        print("✅ 所有 API 契約測試通過!")
    else:
        print("❌ 部分測試失敗,請檢查輸出")

    if coverage:
        print(f"\n📊 覆蓋率報告已生成: htmlcov/index.html")

    print("=" * 70)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description='Run API Contract Tests')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Run tests with verbose output')
    parser.add_argument('-c', '--coverage', action='store_true',
                       help='Generate coverage report')

    args = parser.parse_args()

    exit_code = run_tests(verbose=args.verbose, coverage=args.coverage)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
