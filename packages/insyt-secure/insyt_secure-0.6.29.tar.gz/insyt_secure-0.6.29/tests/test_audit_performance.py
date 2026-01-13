"""
Performance test to verify audit logging doesn't impact response time.
"""
import time
import json
from insyt_secure.utils.audit_logger import AuditLogger

def test_compression_performance():
    """Test compression speed."""
    # Sample data
    query = "Calculate fibonacci sequence up to 100" * 10  # ~400 chars
    python_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = [fibonacci(i) for i in range(20)]
print(result)
""" * 10  # ~1000 chars
    
    extracted_data = json.dumps({"result": list(range(1000))})  # ~4000 chars
    
    # Initialize logger
    logger = AuditLogger(
        db_path="./data/perf_test_audit.db",
        max_size_gb=0.1,
        max_retention_days=30
    )
    
    # Test compression speed
    print("=" * 60)
    print("COMPRESSION PERFORMANCE TEST")
    print("=" * 60)
    
    start = time.time()
    query_compressed = logger._compress(query)
    t1 = time.time() - start
    print(f"\nQuery compression ({len(query)} chars):")
    print(f"  Time: {t1*1000:.2f}ms")
    print(f"  Size reduction: {len(query)} -> {len(query_compressed)} bytes ({(1-len(query_compressed)/len(query))*100:.1f}%)")
    
    start = time.time()
    code_compressed = logger._compress(python_code)
    t2 = time.time() - start
    print(f"\nCode compression ({len(python_code)} chars):")
    print(f"  Time: {t2*1000:.2f}ms")
    print(f"  Size reduction: {len(python_code)} -> {len(code_compressed)} bytes ({(1-len(code_compressed)/len(python_code))*100:.1f}%)")
    
    start = time.time()
    data_compressed = logger._compress(extracted_data)
    t3 = time.time() - start
    print(f"\nData compression ({len(extracted_data)} chars):")
    print(f"  Time: {t3*1000:.2f}ms")
    print(f"  Size reduction: {len(extracted_data)} -> {len(data_compressed)} bytes ({(1-len(data_compressed)/len(extracted_data))*100:.1f}%)")
    
    total_compression_time = (t1 + t2 + t3) * 1000
    print(f"\n{'='*60}")
    print(f"TOTAL COMPRESSION TIME: {total_compression_time:.2f}ms")
    print(f"{'='*60}")
    
    # Test full logging performance
    print("\n" + "=" * 60)
    print("FULL LOGGING PERFORMANCE TEST")
    print("=" * 60)
    
    times = []
    for i in range(10):
        start = time.time()
        logger.log_execution(
            query=query,
            python_code=python_code,
            user=f"test_user_{i}",
            status="success",
            extracted_data=extracted_data
        )
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
    
    print(f"\nLogging 10 executions:")
    print(f"  Min time: {min(times):.2f}ms")
    print(f"  Max time: {max(times):.2f}ms")
    print(f"  Avg time: {sum(times)/len(times):.2f}ms")
    print(f"  Total time: {sum(times):.2f}ms")
    
    if max(times) > 10:
        print(f"\n⚠️  WARNING: Some log operations took > 10ms")
        print(f"   This could impact response time if done synchronously!")
    else:
        print(f"\n✓ All operations completed in < 10ms")
    
    print("\n" + "=" * 60)
    print("RECOMMENDATION:")
    print("=" * 60)
    if max(times) > 5:
        print("✓ Audit logging should be done ASYNCHRONOUSLY after response")
        print("  is sent to avoid impacting time-sensitive responses.")
    else:
        print("✓ Audit logging is fast enough (<5ms) but async is still")
        print("  recommended for best practices and scalability.")
    print("=" * 60)


if __name__ == "__main__":
    test_compression_performance()
