#!/usr/bin/env python3
"""
Performance testing script for the application
"""

import statistics
import sys
import time
from pathlib import Path

import psutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import AppConfig, Application, calculate_sum, validate_email


class PerformanceTester:
    """Performance testing utilities."""

    def __init__(self):
        self.results = []

    def measure_time(self, func, *args, **kwargs):
        """Measure execution time of a function."""
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        return result, end - start

    async def measure_async_time(self, func, *args, **kwargs):
        """Measure execution time of an async function."""
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()
        return result, end - start

    def measure_memory(self):
        """Get current memory usage."""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB

    def run_benchmark(self, name: str, func, iterations: int = 100):
        """Run a benchmark test."""
        print(f"\n🔬 Testing: {name}")
        print(f"   Iterations: {iterations}")

        times = []
        memory_before = self.measure_memory()

        for _ in range(iterations):
            _, elapsed = self.measure_time(func)
            times.append(elapsed)

        memory_after = self.measure_memory()
        memory_used = memory_after - memory_before

        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0

        result = {
            "name": name,
            "iterations": iterations,
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "std_dev": std_dev,
            "memory_used": memory_used,
            "ops_per_sec": 1 / avg_time if avg_time > 0 else 0,
        }

        self.results.append(result)

        print(f"   ✅ Avg: {avg_time*1000:.2f}ms")
        print(f"   📊 Min: {min_time*1000:.2f}ms, Max: {max_time*1000:.2f}ms")
        print(f"   💾 Memory: {memory_used:.2f}MB")
        print(f"   ⚡ Ops/sec: {result['ops_per_sec']:.0f}")

        return result


def test_calculate_sum_performance():
    """Test calculate_sum performance."""
    test_data = list(range(1000))
    return calculate_sum(test_data)


def test_validate_email_performance():
    """Test email validation performance."""
    emails = [
        "test@example.com",
        "invalid.email",
        "user.name+tag@example.co.uk",
        "notanemail",
        "test@sub.domain.com",
    ]
    results = []
    for email in emails:
        results.append(validate_email(email))
    return results


def test_app_initialization():
    """Test application initialization."""
    config = AppConfig.from_env()
    app = Application(config)
    return app


def test_file_operations():
    """Test file I/O operations."""
    test_file = Path("test_temp.txt")

    # Write test
    content = "Test content\n" * 100
    test_file.write_text(content)

    # Read test
    read_content = test_file.read_text()

    # Cleanup
    test_file.unlink()

    return len(read_content)


def test_json_processing():
    """Test JSON processing."""
    import json

    data = {
        "users": [
            {"id": i, "name": f"User{i}", "email": f"user{i}@example.com"} for i in range(100)
        ],
        "metadata": {"timestamp": time.time(), "version": "1.0.0"},
    }

    # Serialize
    json_str = json.dumps(data)

    # Deserialize
    parsed = json.loads(json_str)

    return len(json_str)


def test_ollama_mock():
    """Test Ollama integration (mocked)."""

    # This is a mock test - real Ollama would be much slower
    def mock_chat(prompt):
        # Simulate processing time
        time.sleep(0.01)
        return f"Response to: {prompt[:20]}..."

    return mock_chat("Test prompt")


def main():
    """Run all performance tests."""
    print("🚀 Performance Testing Suite")
    print("=" * 50)

    tester = PerformanceTester()

    # Run benchmarks
    tester.run_benchmark("Calculate Sum (1000 items)", test_calculate_sum_performance, 1000)
    tester.run_benchmark("Email Validation (5 emails)", test_validate_email_performance, 500)
    tester.run_benchmark("App Initialization", test_app_initialization, 10)
    tester.run_benchmark("File Operations", test_file_operations, 50)
    tester.run_benchmark("JSON Processing", test_json_processing, 100)
    tester.run_benchmark("Ollama Mock", test_ollama_mock, 50)

    # Summary
    print("\n" + "=" * 50)
    print("📊 Performance Summary")
    print("=" * 50)

    total_time = sum(r["avg_time"] * r["iterations"] for r in tester.results)
    total_memory = sum(r["memory_used"] for r in tester.results)

    print(f"\n⏱️  Total execution time: {total_time:.2f}s")
    print(f"💾 Total memory used: {total_memory:.2f}MB")

    # Performance grade
    if total_time < 5:
        grade = "A+ 🏆 Excellent!"
    elif total_time < 10:
        grade = "A 🎯 Very Good"
    elif total_time < 20:
        grade = "B ✅ Good"
    else:
        grade = "C ⚠️ Needs Optimization"

    print(f"\n🎓 Performance Grade: {grade}")

    # Recommendations
    print("\n💡 Recommendations:")
    for result in tester.results:
        if result["avg_time"] > 0.1:  # 100ms
            print(f"   ⚠️ {result['name']} is slow ({result['avg_time']*1000:.0f}ms)")
        if result["memory_used"] > 10:  # 10MB
            print(f"   💾 {result['name']} uses high memory ({result['memory_used']:.1f}MB)")

    return 0 if grade.startswith("A") else 1


if __name__ == "__main__":
    sys.exit(main())
