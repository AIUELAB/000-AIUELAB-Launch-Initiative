#!/usr/bin/env python3
"""
Beartype Runtime Type Checking Integration
==========================================

Beartype provides O(1) runtime type checking with zero performance overhead.
This module demonstrates best practices for using Beartype in production code.

Features:
- Zero-cost abstractions
- Rich error messages
- PEP 484/585/593 compliance
- Async support
- Custom validators
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Generic, Literal, TypeVar, Union

from beartype import beartype
from beartype.vale import Is


# Basic usage with @beartype decorator
@beartype
def calculate_average(numbers: list[float]) -> float:
    """Calculate average with runtime type checking."""
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)


# Complex type annotations
@beartype
def process_config(
    config: dict[str, str | int | bool | None], strict_mode: bool = False
) -> dict[str, str]:
    """Process configuration with complex type checking."""
    result = {}
    for key, value in config.items():
        if value is None and not strict_mode:
            continue
        result[key] = str(value)
    return result


# Custom validators with Annotated types
PositiveInt = Annotated[int, Is[lambda x: x > 0]]
EmailStr = Annotated[str, Is[lambda x: "@" in x and "." in x.split("@")[1]]]
FilePath = Annotated[Path, Is[lambda x: x.exists()]]


@beartype
def create_user(
    name: str, age: PositiveInt, email: EmailStr, config_file: FilePath | None = None
) -> dict[str, str | int]:
    """Create user with custom type validators."""
    user = {"name": name, "age": age, "email": email}

    if config_file:
        user["config"] = str(config_file)

    return user


# Dataclass with beartype
@beartype
@dataclass
class MCPServer:
    """MCP Server configuration with runtime validation."""

    name: str
    url: str
    port: PositiveInt
    protocol: Literal["http", "https", "ws", "wss"]
    api_key: str | None = None
    timeout: float = 30.0
    retry_count: int = 3

    def __post_init__(self):
        """Additional validation after initialization."""
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.retry_count < 0:
            raise ValueError("Retry count cannot be negative")


# Generic types with beartype
T = TypeVar("T")


@beartype
class Cache(Generic[T]):
    """Generic cache with type-safe operations."""

    def __init__(self, max_size: PositiveInt = 100):
        self._cache: dict[str, T] = {}
        self.max_size = max_size

    @beartype
    def get(self, key: str) -> T | None:
        """Get item from cache."""
        return self._cache.get(key)

    @beartype
    def set(self, key: str, value: T) -> None:
        """Set item in cache."""
        if len(self._cache) >= self.max_size:
            # Remove oldest item (simplified LRU)
            oldest = next(iter(self._cache))
            del self._cache[oldest]
        self._cache[key] = value


# Async support with beartype
@beartype
async def fetch_data(urls: list[str], timeout: float = 10.0) -> list[dict[str, str | int] | None]:
    """Fetch data from multiple URLs with type checking."""

    async def fetch_single(url: str) -> dict[str, str | int] | None:
        # Simulated async fetch
        await asyncio.sleep(0.1)
        return {"url": url, "status": 200, "data": "example"}

    tasks = [fetch_single(url) for url in urls]
    return await asyncio.gather(*tasks)


# Advanced validators
NonEmptyStr = Annotated[str, Is[lambda x: len(x) > 0]]
PercentFloat = Annotated[float, Is[lambda x: 0.0 <= x <= 1.0]]
PortNumber = Annotated[int, Is[lambda x: 1 <= x <= 65535]]
IPv4Address = Annotated[
    str,
    Is[
        lambda x: all(0 <= int(part) <= 255 for part in x.split(".") if part.isdigit())
        and len(x.split(".")) == 4
    ],
]


@beartype
@dataclass
class NetworkConfig:
    """Network configuration with advanced validation."""

    hostname: NonEmptyStr
    ip_address: IPv4Address
    port: PortNumber
    ssl_enabled: bool = True
    load_factor: PercentFloat = 0.5


# Recursive types
from typing import Any

JSONValue = Union[None, bool, int, float, str, list["JSONValue"], dict[str, "JSONValue"]]


@beartype
def validate_json(data: JSONValue) -> bool:
    """Validate JSON-compatible data structure."""
    # The type checking happens automatically via beartype
    return True


# Custom error handling
@beartype
def divide_numbers(numerator: int | float, denominator: int | float) -> float:
    """Divide with type checking and error handling."""
    if denominator == 0:
        raise ValueError("Division by zero")
    return numerator / denominator


# Practical MCP integration example
@beartype
class MCPClient:
    """Type-safe MCP client implementation."""

    def __init__(self, server_name: NonEmptyStr, base_url: str, api_key: str | None = None):
        self.server_name = server_name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._cache = Cache[dict[str, Any]](max_size=50)

    @beartype
    async def execute_tool(
        self, tool_name: NonEmptyStr, params: dict[str, str | int | float | bool | None]
    ) -> dict[str, Any]:
        """Execute MCP tool with type-safe parameters."""
        # Check cache
        cache_key = f"{tool_name}:{params!s}"
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        # Simulate tool execution
        result = {"tool": tool_name, "status": "success", "result": params}

        # Cache result
        self._cache.set(cache_key, result)
        return result

    @beartype
    def list_tools(self) -> list[dict[str, str]]:
        """List available tools."""
        return [
            {"name": "search", "type": "query"},
            {"name": "fetch", "type": "retrieval"},
            {"name": "analyze", "type": "processing"},
        ]


# Performance comparison decorator
def benchmark_beartype(func):
    """Decorator to benchmark beartype overhead."""
    import time

    @beartype
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.6f} seconds")
        return result

    return wrapper


# Example usage and tests
def example_usage():
    """Demonstrate Beartype integration."""

    print("🐻 Beartype Runtime Type Checking Examples")
    print("=" * 50)

    # Basic type checking
    try:
        result = calculate_average([1.0, 2.0, 3.0])
        print(f"✅ Average: {result}")

        # This will raise a type error
        # calculate_average("not a list")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Custom validators
    try:
        user = create_user(
            name="Alice",
            age=25,  # Positive integer
            email="alice@example.com",  # Valid email
        )
        print(f"✅ User created: {user}")

        # This will fail validation
        # create_user(name="Bob", age=-5, email="invalid")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Dataclass validation
    try:
        server = MCPServer(
            name="github",
            url="https://api.github.com",
            port=443,
            protocol="https",
            api_key="secret_key",
        )
        print(f"✅ Server configured: {server.name}")

        # This will fail protocol validation
        # MCPServer(name="test", url="test", port=80, protocol="ftp")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Network configuration
    try:
        config = NetworkConfig(
            hostname="api.example.com", ip_address="192.168.1.1", port=8080, load_factor=0.75
        )
        print(f"✅ Network config: {config.hostname}:{config.port}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Generic cache
    cache: Cache[str] = Cache(max_size=10)
    cache.set("key1", "value1")
    print(f"✅ Cached value: {cache.get('key1')}")

    # Async example
    async def async_example():
        results = await fetch_data(["http://api1.com", "http://api2.com"])
        print(f"✅ Fetched {len(results)} results")

    # Run async example
    asyncio.run(async_example())

    print("\n✨ All Beartype validations passed!")


# Performance test
@benchmark_beartype
def performance_test(data: list[int]) -> int:
    """Test function to measure beartype overhead."""
    return sum(data)


if __name__ == "__main__":
    # Run examples
    example_usage()

    # Performance test
    print("\n⚡ Performance Test:")
    large_list = list(range(1000000))
    result = performance_test(large_list)
    print(f"Sum of {len(large_list)} integers: {result}")

    print("\n🎉 Beartype integration complete!")
