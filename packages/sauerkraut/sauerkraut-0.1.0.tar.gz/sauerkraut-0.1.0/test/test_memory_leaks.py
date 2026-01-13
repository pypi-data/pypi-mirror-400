#!/usr/bin/env python3
"""Memory leak test script for Sauerkraut.

This script measures memory usage across repeated operations to detect memory leaks.
Run on different git commits and compare output to verify leak fixes.

Usage:
    python3 test_memory_leaks.py
    python3 test_memory_leaks.py --iterations 2000
"""

import argparse
import gc
import subprocess
import sys
import tracemalloc
from dataclasses import dataclass

import sauerkraut as skt


@dataclass
class TestResult:
    name: str
    iterations: int
    start_mb: float
    end_mb: float
    peak_mb: float
    growth_mb: float
    kb_per_iter: float
    passed: bool


def get_git_commit() -> str:
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd="..",
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def get_memory_mb() -> tuple[float, float]:
    """Return (current_mb, peak_mb) from tracemalloc."""
    current, peak = tracemalloc.get_traced_memory()
    return current / (1024 * 1024), peak / (1024 * 1024)


def reset_memory_tracking():
    """Reset tracemalloc peak and force garbage collection."""
    gc.collect()
    gc.collect()
    tracemalloc.reset_peak()


# Global counter for test functions
_call_count = 0


def _copy_frame_fn():
    """Function that copies its own frame."""
    global _call_count
    _call_count += 1
    local_var = 42
    frame_bytes = skt.copy_current_frame(serialize=True)
    if _call_count % 2 == 1:
        return frame_bytes
    return local_var + _call_count


def test_repeated_frame_copy(iterations: int) -> TestResult:
    """Test repeated frame copying for memory leaks.

    This tests:
    - Frame copy capsule destructor fix
    - PyFrame_GetBack() reference leak fix
    """
    global _call_count

    reset_memory_tracking()
    start_mb, _ = get_memory_mb()

    for _ in range(iterations):
        _call_count = 0
        frame_bytes = _copy_frame_fn()
        # Let frame_bytes go out of scope
        del frame_bytes

        # Periodic GC to allow cleanup
        if _ % 100 == 0:
            gc.collect()

    gc.collect()
    end_mb, peak_mb = get_memory_mb()
    growth_mb = end_mb - start_mb
    kb_per_iter = (growth_mb * 1024) / iterations

    return TestResult(
        name="Repeated Frame Copy",
        iterations=iterations,
        start_mb=start_mb,
        end_mb=end_mb,
        peak_mb=peak_mb,
        growth_mb=growth_mb,
        kb_per_iter=kb_per_iter,
        passed=kb_per_iter < 1.0,  # Less than 1KB growth per iteration
    )


def test_serialize_deserialize_cycles(iterations: int) -> TestResult:
    """Test serialize/deserialize cycles for memory leaks.

    This tests:
    - Code object leak fixes in deserialization
    - pycode_strongref usage
    """
    global _call_count

    # Create one serialized frame to reuse
    _call_count = 0
    frame_bytes = _copy_frame_fn()

    reset_memory_tracking()
    start_mb, _ = get_memory_mb()

    for i in range(iterations):
        # Deserialize without running
        frame = skt.deserialize_frame(frame_bytes)
        del frame

        if i % 100 == 0:
            gc.collect()

    gc.collect()
    end_mb, peak_mb = get_memory_mb()
    growth_mb = end_mb - start_mb
    kb_per_iter = (growth_mb * 1024) / iterations

    return TestResult(
        name="Serialize/Deserialize Cycles",
        iterations=iterations,
        start_mb=start_mb,
        end_mb=end_mb,
        peak_mb=peak_mb,
        growth_mb=growth_mb,
        kb_per_iter=kb_per_iter,
        passed=kb_per_iter < 1.0,
    )


def test_run_frame_cycles(iterations: int) -> TestResult:
    """Test frame execution cycles for memory leaks.

    This tests:
    - f_executable.bits DECREF fix
    - Frame cleanup after execution
    """
    global _call_count

    # Create serialized frame
    _call_count = 0
    frame_bytes = _copy_frame_fn()

    reset_memory_tracking()
    start_mb, _ = get_memory_mb()

    for i in range(iterations):
        _call_count = 1  # Set so frame runs to completion
        result = skt.deserialize_frame(frame_bytes, run=True)
        del result

        if i % 50 == 0:
            gc.collect()

    gc.collect()
    end_mb, peak_mb = get_memory_mb()
    growth_mb = end_mb - start_mb
    kb_per_iter = (growth_mb * 1024) / iterations

    return TestResult(
        name="Run Frame Cycles",
        iterations=iterations,
        start_mb=start_mb,
        end_mb=end_mb,
        peak_mb=peak_mb,
        growth_mb=growth_mb,
        kb_per_iter=kb_per_iter,
        passed=kb_per_iter < 2.0,  # Slightly higher threshold for full execution
    )


def test_full_roundtrip_cycles(iterations: int) -> TestResult:
    """Test full copy-serialize-deserialize-run cycles.

    This is a comprehensive stress test of all operations.
    """
    global _call_count

    reset_memory_tracking()
    start_mb, _ = get_memory_mb()

    for i in range(iterations):
        # Full cycle: copy -> serialize -> deserialize -> run
        _call_count = 0
        frame_bytes = _copy_frame_fn()

        _call_count = 1
        result = skt.deserialize_frame(frame_bytes, run=True)

        del frame_bytes
        del result

        if i % 25 == 0:
            gc.collect()

    gc.collect()
    end_mb, peak_mb = get_memory_mb()
    growth_mb = end_mb - start_mb
    kb_per_iter = (growth_mb * 1024) / iterations

    return TestResult(
        name="Full Roundtrip Cycles",
        iterations=iterations,
        start_mb=start_mb,
        end_mb=end_mb,
        peak_mb=peak_mb,
        growth_mb=growth_mb,
        kb_per_iter=kb_per_iter,
        passed=kb_per_iter < 2.0,
    )


def print_header():
    """Print test header with environment info."""
    commit = get_git_commit()
    print("=" * 50)
    print("Sauerkraut Memory Leak Test")
    print("=" * 50)
    print(f"Python:  {sys.version.split()[0]}")
    print(f"Commit:  {commit}")
    print("=" * 50)
    print()


def print_result(result: TestResult):
    """Print a single test result."""
    status = "PASS" if result.passed else "WARN"
    print(f"Test: {result.name} ({result.iterations} iterations)")
    print(f"  Start:   {result.start_mb:.2f} MB")
    print(f"  End:     {result.end_mb:.2f} MB")
    print(f"  Peak:    {result.peak_mb:.2f} MB")
    print(f"  Growth:  {result.growth_mb:.2f} MB ({result.kb_per_iter:.2f} KB/iter)")
    print(f"  Status:  {status}")
    print()


def print_summary(results: list[TestResult]):
    """Print test summary."""
    passed = sum(1 for r in results if r.passed)
    total = len(results)

    print("=" * 50)
    print("Summary")
    print("=" * 50)
    print(f"  Total tests: {total}")
    print(f"  Passed:      {passed}")
    print(f"  Warnings:    {total - passed}")

    if passed == total:
        print("\nAll tests passed - no significant memory leaks detected.")
    else:
        print("\nWARNING: Some tests showed higher than expected memory growth.")
        print("This may indicate memory leaks.")


def main():
    parser = argparse.ArgumentParser(description="Test Sauerkraut for memory leaks")
    parser.add_argument(
        "--iterations", "-n",
        type=int,
        default=500,
        help="Base number of iterations (default: 500)"
    )
    args = parser.parse_args()

    # Start tracemalloc
    tracemalloc.start()

    print_header()

    # Scale iterations for different tests
    base = args.iterations
    tests = [
        (test_repeated_frame_copy, base * 2),      # 1000 default
        (test_serialize_deserialize_cycles, base), # 500 default
        (test_run_frame_cycles, base // 2),        # 250 default
        (test_full_roundtrip_cycles, base // 5),   # 100 default
    ]

    results = []
    for test_fn, iterations in tests:
        result = test_fn(iterations)
        print_result(result)
        results.append(result)

    print_summary(results)

    tracemalloc.stop()


if __name__ == "__main__":
    main()
