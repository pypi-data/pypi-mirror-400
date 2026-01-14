"""
Test script for the logger with multiprocessing support.
This verifies that the lazy-loading proxy pattern works correctly
across multiple processes spawned by ProcessPoolExecutor.
"""

import os
from concurrent.futures import ProcessPoolExecutor, as_completed


def worker_task(worker_id: int) -> dict:
    """
    Worker function that performs logging operations.
    This runs in a separate process.

    Args:
        worker_id: Unique identifier for this worker

    Returns:
        dict: Results from the worker process
    """
    # Import logger inside the worker to trigger lazy initialization
    from commons.logger.logger import logger

    # Get the PID for verification
    pid = os.getpid()

    # Log various levels
    logger.info("Worker %s started in PID %s", worker_id, pid)
    logger.debug("Debug message from worker %s", worker_id)
    logger.warning("Warning from worker %s", worker_id)

    # Test exception logging
    try:
        raise ValueError(f"Test exception from worker {worker_id}")
    except Exception:
        logger.error("Worker %s caught an exception", worker_id)

    # Return results for verification
    return {
        "worker_id": worker_id,
        "pid": pid,
        "logger_name": logger.name,
        "logger_id": id(logger),
    }


def test_multiprocessing_logging():
    """
    Main test function that spawns multiple processes and verifies logging.
    """
    print("=" * 80)
    print("Testing Logger with ProcessPoolExecutor")
    print("=" * 80)

    # Log from main process
    from commons.logger.logger import logger

    main_pid = os.getpid()
    logger.info("Main process started with PID %s", main_pid)

    # Test basic logging in main process
    logger.info("Test from main process - INFO")
    logger.warning("Test from main process - WARNING")
    logger.error("Test from main process - ERROR")

    print("\n" + "-" * 80)
    print("Spawning worker processes...")
    print("-" * 80 + "\n")

    # Spawn multiple worker processes
    num_workers = 3
    results = []

    with ProcessPoolExecutor(
        max_workers=num_workers, max_tasks_per_child=1
    ) as executor:
        # Submit all worker tasks
        futures = [executor.submit(worker_task, i) for i in range(num_workers)]

        # Wait for all to complete and collect results
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                logger.info("Worker %s completed successfully", result["worker_id"])
            except Exception:
                logger.critical("Worker failed with error", exc_info=True)

    print("\n" + "-" * 80)
    print("Test Results Summary")
    print("-" * 80)

    # Verify results
    print(f"\nMain process PID: {main_pid}")
    print(f"Number of workers: {len(results)}")

    # Verify each worker got its own PID
    pids = [r["pid"] for r in results]
    print(f"Worker PIDs: {pids}")

    # Verify no duplicate PIDs (each process is unique)
    if len(pids) == len(set[str](pids)):
        print("✅ All workers ran in separate processes")
    else:
        print("❌ Some workers shared the same PID")

    # Verify logger instances
    logger_ids = [r["logger_id"] for r in results]
    if len(logger_ids) == len(set(logger_ids)):
        print("✅ Each process got its own logger instance")
    else:
        print("❌ Some processes shared the same logger instance")

    # Test final log message
    logger.info("Main process completed successfully")

    print("\n" + "=" * 80)
    print("Test completed!")
    print("=" * 80)


def test_exception_logging():
    """
    Test detailed exception logging with tracebacks.
    """
    from commons.logger.logger import logger

    print("\n" + "=" * 80)
    print("Testing Exception Logging")
    print("=" * 80 + "\n")

    # Test nested exception
    try:
        try:
            raise ValueError("Inner exception")
        except ValueError as e:
            raise RuntimeError("Outer exception") from e
    except RuntimeError:
        logger.error("Nested exception test", exc_info=True)

    # Test critical error
    try:
        raise KeyError("Critical error test")
    except KeyError:
        logger.critical("This is a critical error", exc_info=True)

    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Run the tests
    test_multiprocessing_logging()
    test_exception_logging()
