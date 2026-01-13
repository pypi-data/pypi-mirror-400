"""
Test tasks for debugging and testing the task worker system.
These tasks cover various scenarios to help test the runner's behavior.
"""
import asyncio
import logging
import random
import time
from typing import Optional

from fastpluggy_plugin.tasks_worker import TaskWorker


log = logging.getLogger(__name__)


# ============================================================================
# Exception Tasks - Test error handling
# ============================================================================

@TaskWorker.register(
    name="test.exception.value_error",
    description="Raises a ValueError for testing error handling",
    tags=["test", "exception", "error"],
    topic="test_exceptions",
    allow_concurrent=True,
)
def task_raise_value_error(message: str = "Test ValueError"):
    """Raises a ValueError for testing error handling."""
    log.info(f"About to raise ValueError: {message}")
    raise ValueError(message)


@TaskWorker.register(
    name="test.exception.type_error",
    description="Raises a TypeError for testing error handling",
    tags=["test", "exception", "error"],
    topic="test_exceptions",
    allow_concurrent=True,
)
def task_raise_type_error(message: str = "Test TypeError"):
    """Raises a TypeError for testing error handling."""
    log.info(f"About to raise TypeError: {message}")
    raise TypeError(message)


@TaskWorker.register(
    name="test.exception.import_error",
    description="Raises an ImportError (fatal exception)",
    tags=["test", "exception", "fatal"],
    topic="test_exceptions",
    allow_concurrent=True,
)
def task_raise_import_error(message: str = "Test ImportError"):
    """Raises an ImportError for testing fatal exceptions."""
    log.info(f"About to raise ImportError: {message}")
    raise ImportError(message)


@TaskWorker.register(
    name="test.exception.timeout_error",
    description="Raises a TimeoutError (retriable exception)",
    tags=["test", "exception", "retriable"],
    topic="test_exceptions",
    max_retries=3,
    allow_concurrent=True,
)
def task_raise_timeout_error(message: str = "Test TimeoutError"):
    """Raises a TimeoutError for testing retriable exceptions."""
    log.info(f"About to raise TimeoutError: {message}")
    raise TimeoutError(message)


@TaskWorker.register(
    name="test.exception.connection_error",
    description="Raises a ConnectionError (retriable exception)",
    tags=["test", "exception", "retriable"],
    topic="test_exceptions",
    max_retries=3,
    allow_concurrent=True,
)
def task_raise_connection_error(message: str = "Test ConnectionError"):
    """Raises a ConnectionError for testing retriable exceptions."""
    log.info(f"About to raise ConnectionError: {message}")
    raise ConnectionError(message)


@TaskWorker.register(
    name="test.exception.random_failure",
    description="Randomly fails based on failure rate",
    tags=["test", "exception", "random"],
    topic="test_exceptions",
    max_retries=2,
    allow_concurrent=True,
)
def task_random_failure(failure_rate: float = 0.5):
    """Randomly fails based on failure_rate (0.0 to 1.0)."""
    if random.random() < failure_rate:
        log.warning(f"Random failure triggered (rate={failure_rate})")
        raise RuntimeError(f"Random failure (rate={failure_rate})")
    log.info(f"Task succeeded (failure_rate={failure_rate})")
    return {"success": True, "failure_rate": failure_rate}


# ============================================================================
# Waiting/Sleeping Tasks - Test timing and concurrency
# ============================================================================

@TaskWorker.register(
    name="test.sleep.short",
    description="Sleeps for a short duration (default 1 second)",
    tags=["test", "sleep", "timing"],
    topic="test_timing",
    allow_concurrent=True,
)
def task_sleep_short(seconds: float = 1.0):
    """Sleeps for a short duration (default 1 second)."""
    log.info(f"Sleeping for {seconds} seconds...")
    time.sleep(seconds)
    log.info(f"Woke up after {seconds} seconds")
    return {"slept_seconds": seconds}


@TaskWorker.register(
    name="test.sleep.medium",
    description="Sleeps for a medium duration (default 5 seconds)",
    tags=["test", "sleep", "timing"],
    topic="test_timing",
    allow_concurrent=True,
)
def task_sleep_medium(seconds: float = 5.0):
    """Sleeps for a medium duration (default 5 seconds)."""
    log.info(f"Sleeping for {seconds} seconds...")
    time.sleep(seconds)
    log.info(f"Woke up after {seconds} seconds")
    return {"slept_seconds": seconds}


@TaskWorker.register(
    name="test.sleep.long",
    description="Sleeps for a long duration (default 30 seconds)",
    tags=["test", "sleep", "timing"],
    topic="test_timing",
    allow_concurrent=True,
)
def task_sleep_long(seconds: float = 30.0):
    """Sleeps for a long duration (default 30 seconds)."""
    log.info(f"Sleeping for {seconds} seconds...")
    time.sleep(seconds)
    log.info(f"Woke up after {seconds} seconds")
    return {"slept_seconds": seconds}


@TaskWorker.register(
    name="test.sleep.random",
    description="Sleeps for a random duration",
    tags=["test", "sleep", "timing", "random"],
    topic="test_timing",
    allow_concurrent=True,
)
def task_sleep_random(min_seconds: float = 1.0, max_seconds: float = 10.0):
    """Sleeps for a random duration between min and max seconds."""
    duration = random.uniform(min_seconds, max_seconds)
    log.info(f"Sleeping for random duration: {duration:.2f} seconds...")
    time.sleep(duration)
    log.info(f"Woke up after {duration:.2f} seconds")
    return {"slept_seconds": duration, "min": min_seconds, "max": max_seconds}


@TaskWorker.register(
    name="test.async.sleep",
    description="Async task that sleeps for specified duration",
    tags=["test", "async", "sleep", "timing"],
    topic="test_async",
    allow_concurrent=True,
)
async def task_async_sleep(seconds: float = 2.0):
    """Async task that sleeps for specified duration."""
    log.info(f"Async sleeping for {seconds} seconds...")
    await asyncio.sleep(seconds)
    log.info(f"Async woke up after {seconds} seconds")
    return {"async_slept_seconds": seconds}


# ============================================================================
# CPU Intensive Tasks - Test performance and resource usage
# ============================================================================

def fibonacci(n: int) -> int:
    """Calculate fibonacci number recursively (inefficient by design)."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


@TaskWorker.register(
    name="test.cpu.fibonacci",
    description="Calculate Fibonacci number (CPU intensive)",
    tags=["test", "cpu", "performance"],
    topic="test_performance",
    allow_concurrent=True,
)
def task_fibonacci(n: int = 30):
    """Calculate nth Fibonacci number (CPU intensive)."""
    log.info(f"Calculating fibonacci({n})...")
    start_time = time.time()
    result = fibonacci(n)
    elapsed = time.time() - start_time
    log.info(f"fibonacci({n}) = {result}, took {elapsed:.3f}s")
    return {"n": n, "result": result, "elapsed_seconds": elapsed}


def is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


@TaskWorker.register(
    name="test.cpu.find_primes",
    description="Find all prime numbers up to max (CPU intensive)",
    tags=["test", "cpu", "performance"],
    topic="test_performance",
    allow_concurrent=True,
)
def task_find_primes(max_number: int = 100000):
    """Find all prime numbers up to max_number (CPU intensive)."""
    log.info(f"Finding primes up to {max_number}...")
    start_time = time.time()
    primes = [n for n in range(2, max_number + 1) if is_prime(n)]
    elapsed = time.time() - start_time
    log.info(f"Found {len(primes)} primes up to {max_number}, took {elapsed:.3f}s")
    return {
        "max_number": max_number,
        "count": len(primes),
        "elapsed_seconds": elapsed,
        "largest_prime": primes[-1] if primes else None
    }


@TaskWorker.register(
    name="test.cpu.matrix_multiply",
    description="Multiply random matrices (CPU intensive)",
    tags=["test", "cpu", "performance", "matrix"],
    topic="test_performance",
    allow_concurrent=True,
)
def task_matrix_multiply(size: int = 100):
    """Multiply two random matrices (CPU intensive)."""
    log.info(f"Multiplying {size}x{size} matrices...")
    start_time = time.time()

    # Create two random matrices
    matrix_a = [[random.random() for _ in range(size)] for _ in range(size)]
    matrix_b = [[random.random() for _ in range(size)] for _ in range(size)]

    # Multiply matrices
    result = [[0 for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            for k in range(size):
                result[i][j] += matrix_a[i][k] * matrix_b[k][j]

    elapsed = time.time() - start_time
    log.info(f"Matrix multiplication ({size}x{size}) completed in {elapsed:.3f}s")
    return {
        "size": size,
        "elapsed_seconds": elapsed,
        "operations": size ** 3
    }


# ============================================================================
# Memory Intensive Tasks - Test memory usage
# ============================================================================

@TaskWorker.register(
    name="test.memory.allocate",
    description="Allocate specified amount of memory",
    tags=["test", "memory", "performance"],
    topic="test_memory",
    allow_concurrent=True,
)
def task_allocate_memory(megabytes: int = 100):
    """Allocate specified amount of memory (in MB)."""
    log.info(f"Allocating {megabytes}MB of memory...")
    start_time = time.time()

    # Allocate memory as a list of bytes
    data = bytearray(megabytes * 1024 * 1024)
    # Fill with some data to ensure allocation
    for i in range(0, len(data), 1024):
        data[i] = i % 256

    elapsed = time.time() - start_time
    log.info(f"Allocated {megabytes}MB in {elapsed:.3f}s")

    # Sleep a bit to keep memory allocated
    time.sleep(2)

    return {
        "megabytes_allocated": megabytes,
        "elapsed_seconds": elapsed,
        "bytes": len(data)
    }


@TaskWorker.register(
    name="test.memory.large_list",
    description="Create a large list of objects",
    tags=["test", "memory", "performance"],
    topic="test_memory",
    allow_concurrent=True,
)
def task_create_large_list(elements: int = 1000000):
    """Create a large list of objects."""
    log.info(f"Creating list with {elements} elements...")
    start_time = time.time()

    large_list = [{"id": i, "value": random.random(), "data": f"item_{i}"} for i in range(elements)]

    elapsed = time.time() - start_time
    log.info(f"Created list with {len(large_list)} elements in {elapsed:.3f}s")

    return {
        "elements": len(large_list),
        "elapsed_seconds": elapsed,
        "sample": large_list[:3] if large_list else []
    }


# ============================================================================
# I/O Tasks - Test I/O operations
# ============================================================================

@TaskWorker.register(
    name="test.io.write_file",
    description="Write a temporary file of specified size",
    tags=["test", "io", "file"],
    topic="test_io",
    allow_concurrent=True,
)
def task_write_temp_file(size_kb: int = 100, filename: Optional[str] = None):
    """Write a temporary file of specified size."""
    import tempfile
    import os

    if filename is None:
        fd, filepath = tempfile.mkstemp(prefix="task_test_", suffix=".dat")
        os.close(fd)
    else:
        filepath = filename

    log.info(f"Writing {size_kb}KB to {filepath}...")
    start_time = time.time()

    with open(filepath, 'wb') as f:
        # Write in chunks
        chunk_size = 1024
        for _ in range(size_kb):
            f.write(b'X' * chunk_size)

    elapsed = time.time() - start_time
    file_size = os.path.getsize(filepath)

    log.info(f"Wrote {file_size} bytes to {filepath} in {elapsed:.3f}s")

    return {
        "filepath": filepath,
        "size_bytes": file_size,
        "size_kb": size_kb,
        "elapsed_seconds": elapsed
    }


# ============================================================================
# Progress/Logging Tasks - Test logging and progress updates
# ============================================================================

@TaskWorker.register(
    name="test.logging.progress_steps",
    description="Task that logs progress at each step",
    tags=["test", "logging", "progress"],
    topic="test_logging",
    allow_concurrent=True,
)
def task_progress_steps(steps: int = 10, delay_per_step: float = 1.0):
    """Task that logs progress at each step."""
    log.info(f"Starting task with {steps} steps...")

    for i in range(1, steps + 1):
        log.info(f"Progress: Step {i}/{steps} ({i*100//steps}%)")
        time.sleep(delay_per_step)

    log.info(f"Completed all {steps} steps!")
    return {"completed_steps": steps, "delay_per_step": delay_per_step}


@TaskWorker.register(
    name="test.logging.detailed",
    description="Task that generates various log levels",
    tags=["test", "logging", "levels"],
    topic="test_logging",
    allow_concurrent=True,
)
def task_detailed_logging(log_count: int = 20):
    """Task that generates various log levels."""
    log.info(f"Generating {log_count} log messages at various levels...")

    for i in range(log_count):
        level = i % 5
        if level == 0:
            log.debug(f"Debug message {i}")
        elif level == 1:
            log.info(f"Info message {i}")
        elif level == 2:
            log.warning(f"Warning message {i}")
        elif level == 3:
            log.error(f"Error message {i}")
        else:
            log.critical(f"Critical message {i}")
        time.sleep(0.1)

    return {"log_messages_generated": log_count}


# ============================================================================
# Combined/Complex Tasks - Test complex scenarios
# ============================================================================

@TaskWorker.register(
    name="test.complex.mixed_operations",
    description="Task combining sleep, CPU, and memory operations",
    tags=["test", "complex", "mixed"],
    topic="test_complex",
    allow_concurrent=True,
)
def task_mixed_operations(
    sleep_seconds: float = 2.0,
    fibonacci_n: int = 25,
    allocate_mb: int = 50
):
    """Task that combines multiple operations."""
    log.info("Starting mixed operations task...")
    results = {}

    # Sleep
    log.info(f"Step 1: Sleeping for {sleep_seconds}s...")
    time.sleep(sleep_seconds)
    results["slept_seconds"] = sleep_seconds

    # CPU work
    log.info(f"Step 2: Calculating fibonacci({fibonacci_n})...")
    fib_result = fibonacci(fibonacci_n)
    results["fibonacci"] = {"n": fibonacci_n, "result": fib_result}

    # Memory allocation
    log.info(f"Step 3: Allocating {allocate_mb}MB...")
    data = bytearray(allocate_mb * 1024 * 1024)
    results["allocated_mb"] = allocate_mb

    log.info("Mixed operations completed!")
    return results


@TaskWorker.register(
    name="test.simple.success",
    description="Simple task that always succeeds",
    tags=["test", "simple", "success"],
    topic="test_simple",
    allow_concurrent=True,
)
def task_success():
    """Simple task that always succeeds."""
    log.info("Task executing successfully")
    return {"status": "success", "message": "Task completed without errors"}


@TaskWorker.register(
    name="test.simple.return_value",
    description="Task that returns the provided value",
    tags=["test", "simple", "return"],
    topic="test_simple",
    allow_concurrent=True,
)
def task_with_return_value(value: str = "test"):
    """Task that returns the provided value."""
    log.info(f"Returning value: {value}")
    return {"returned_value": value, "type": type(value).__name__}


# ============================================================================
# Stress Test Tasks
# ============================================================================

@TaskWorker.register(
    name="test.stress.operations",
    description="Stress test that performs many operations",
    tags=["test", "stress", "performance"],
    topic="test_stress",
    allow_concurrent=True,
)
def task_stress_test(
    duration_seconds: float = 10.0,
    operations_per_second: int = 100
):
    """Stress test that performs many operations."""
    log.info(f"Starting stress test for {duration_seconds}s at {operations_per_second} ops/sec...")

    start_time = time.time()
    operations_done = 0

    while time.time() - start_time < duration_seconds:
        # Do some work
        for _ in range(operations_per_second):
            _ = sum(range(100))
            operations_done += 1
        time.sleep(1)

    elapsed = time.time() - start_time
    log.info(f"Stress test completed: {operations_done} operations in {elapsed:.3f}s")

    return {
        "duration_seconds": elapsed,
        "operations": operations_done,
        "ops_per_second": operations_done / elapsed
    }