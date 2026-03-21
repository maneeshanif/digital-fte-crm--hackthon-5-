#!/usr/bin/env python3
"""
FTE Test Runner and Validator
Run all tests and generate validation report
"""

import subprocess
import json
import time
from pathlib import Path
from datetime import datetime


def run_command(cmd, description):
    """Run a command and return result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    start_time = time.time()

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        elapsed = time.time() - start_time

        success = result.returncode == 0
        print(f"\n✅ {description}: {'PASSED' if success else 'FAILED'}")
        print(f"Time: {elapsed:.2f}s")

        return {
            "name": description,
            "success": success,
            "time": elapsed,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        print(f"\n❌ {description}: TIMEOUT (>300s)")
        return {
            "name": description,
            "success": False,
            "time": 300,
            "error": "timeout"
        }
    except Exception as e:
        print(f"\n❌ {description}: ERROR - {str(e)}")
        return {
            "name": description,
            "success": False,
            "time": 0,
            "error": str(e)
        }


def run_all_tests():
    """Run complete test suite"""

    print("="*60)
    print("FTE PROTOTYPE VALIDATION TEST SUITE")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "summary": {}
    }

    # 1. Agent functional tests
    results["tests"].append(run_command(
        "uv run pytest tests/test_agent.py -v",
        "Agent Functional Tests"
    ))

    # 2. MCP server tests
    results["tests"].append(run_command(
        "uv run pytest tests/test_mcp_server.py -v",
        "MCP Server Tests"
    ))

    # 3. Edge case tests
    results["tests"].append(run_command(
        "uv run pytest tests/test_edge_cases.py -v",
        "Edge Case Tests"
    ))

    # 4. Performance tests
    results["tests"].append(run_command(
        "uv run pytest tests/test_performance.py -v",
        "Performance Tests"
    ))

    # 5. All tests
    results["tests"].append(run_command(
        "uv run pytest tests/ -v --cov=src --cov-report=term-missing",
        "All Tests with Coverage"
    ))

    # Calculate summary
    total = len(results["tests"])
    passed = sum(1 for t in results["tests"] if t["success"])
    failed = total - passed
    success_rate = (passed / total * 100) if total > 0 else 0

    results["summary"] = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "success_rate": success_rate,
        "total_time": sum(t["time"] for t in results["tests"])
    }

    # Generate report
    generate_validation_report(results)

    return results


def generate_validation_report(results):
    """Generate detailed validation report"""

    report = f"""
# FTE Prototype Validation Report

**Generated:** {results['timestamp']}
**Status:** {'✅ PASSED' if results['summary']['success_rate'] >= 80 else '❌ FAILED'}

## Test Summary

| Metric | Value |
|--------|--------|
| Total Tests | {results['summary']['total']} |
| Passed | {results['summary']['passed']} |
| Failed | {results['summary']['failed']} |
| Success Rate | {results['summary']['success_rate']:.1f}% |
| Total Time | {results['summary']['total_time']:.2f}s |

## Test Results

"""

    for test in results["tests"]:
        status_icon = "✅" if test["success"] else "❌"
        report += f"""
### {status_icon} {test['name']}

**Status:** {'PASSED' if test['success'] else 'FAILED'}
**Time:** {test['time']:.2f}s

"""

        if not test["success"]:
            report += f"""
**Error:**
```
{test.get('error', test.get('stderr', 'Unknown error'))}
```

"""

    # Overall assessment
    report += """
## Overall Assessment

"""

    if results['summary']['success_rate'] >= 90:
        report += "**Status: PRODUCTION READY**\n\n"
        report += "All critical tests passing. Ready for Part 2 transition.\n"
    elif results['summary']['success_rate'] >= 75:
        report += "**Status: GOOD**\n\n"
        report += "Most tests passing. Minor issues need addressing.\n"
    elif results['summary']['success_rate'] >= 60:
        report += "**Status: ADEQUATE**\n\n"
        report += "Functional but needs improvement before production.\n"
    else:
        report += "**Status: NEEDS WORK**\n\n"
        report += "Significant issues found. Major rework required.\n"

    # Recommendations
    report += """
## Recommendations

1. Review failed tests and fix issues
2. Ensure coverage is above 80%
3. Validate performance meets baseline targets
4. Document any edge cases discovered
5. Update baseline metrics if performance improved

## Next Steps

After validation:
1. Address any critical failures
2. Prepare transition plan to Part 2
3. Document lessons learned
4. Update skills based on findings
"""

    # Save report
    report_path = Path("tests/validation_report.md")
    report_path.write_text(report)

    # Save JSON for programmatic access
    json_path = Path("tests/validation_results.json")
    json_path.write_text(json.dumps(results, indent=2))

    print("\n" + "="*60)
    print("VALIDATION COMPLETE")
    print("="*60)
    print(f"\nSuccess Rate: {results['summary']['success_rate']:.1f}%")
    print(f"\nReport saved to:")
    print(f"  - {report_path}")
    print(f"  - {json_path}")

    # Print summary
    if results['summary']['success_rate'] >= 90:
        print("\n🎉 Prototype is production ready!")
    elif results['summary']['success_rate'] >= 75:
        print("\n✅ Prototype is good. Minor improvements needed.")
    elif results['summary']['success_rate'] >= 60:
        print("\n⚠️  Prototype needs improvement.")
    else:
        print("\n❌ Prototype needs significant work.")


def main():
    """Main entry point"""
    # Check if tests directory exists
    if not Path("tests").exists():
        print("❌ Error: tests/ directory not found")
        print("Run scaffold scripts first to create test files")
        return 1

    # Check if pytest is installed
    try:
        subprocess.run(
            ["uv", "run", "python", "-c", "import pytest"],
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError:
        print("❌ Error: pytest not installed")
        print("Run: uv add --dev pytest pytest-asyncio")
        return 1

    # Run tests
    results = run_all_tests()

    # Return exit code based on success rate
    return 0 if results['summary']['success_rate'] >= 80 else 1


if __name__ == "__main__":
    exit(main())
