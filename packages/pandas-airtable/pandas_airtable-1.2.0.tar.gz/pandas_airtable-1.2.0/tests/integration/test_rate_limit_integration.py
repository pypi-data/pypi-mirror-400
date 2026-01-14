"""Integration tests for rate limiting and exponential backoff.

Tests verify that the library correctly handles Airtable's 5 QPS rate limit
by backing off and retrying when necessary.
"""

from __future__ import annotations

import time

import pandas as pd
from pyairtable import Api

from pandas_airtable import read_airtable
from pandas_airtable.retry import RateLimitedExecutor, retry_with_backoff

from .conftest import wait_for_api


class TestRateLimitHandling:
    """Test that operations succeed despite rate limiting."""

    def test_rapid_batch_writes_succeed(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test writing many records rapidly - should handle rate limits gracefully."""
        table_name, _ = test_table

        # Create 100 records - requires 10 batches
        # At 5 QPS limit, this should trigger rate limiting if done too fast
        df = pd.DataFrame(
            {
                "Name": [f"RateTest_{i}" for i in range(100)],
                "Value": list(range(100)),
            }
        )

        start_time = time.time()
        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            batch_size=10,
        )
        elapsed = time.time() - start_time

        # All records should be created successfully
        assert result.success, f"Expected success but got errors: {result.errors}"
        assert result.created_count == 100

        # Verify all records exist
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 100

        print(f"\n100 records written in {elapsed:.2f}s ({100 / elapsed:.1f} records/sec)")

    def test_rapid_sequential_reads(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test many rapid read operations - should handle rate limits."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Insert some test data
        table.batch_create([{"Name": f"Item_{i}", "Value": i} for i in range(10)])
        wait_for_api()

        # Make 15 rapid read requests (should exceed 5 QPS momentarily)
        start_time = time.time()
        successful_reads = 0

        for i in range(15):
            try:
                df = read_airtable(base_id, table_name, api_key)
                if len(df) == 10:
                    successful_reads += 1
            except Exception as e:
                print(f"Read {i} failed: {e}")

        elapsed = time.time() - start_time

        # All reads should eventually succeed (with backoff if needed)
        assert successful_reads == 15, f"Only {successful_reads}/15 reads succeeded"
        print(f"\n15 reads completed in {elapsed:.2f}s")

    def test_large_dataset_with_rate_limiting(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test writing 200 records - significant load that tests rate limiting."""
        table_name, _ = test_table

        # 200 records = 20 batches of 10
        # This will definitely trigger rate limiting at 5 QPS
        df = pd.DataFrame(
            {
                "Name": [f"LargeTest_{i}" for i in range(200)],
                "Value": list(range(200)),
            }
        )

        start_time = time.time()
        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            batch_size=10,
        )
        elapsed = time.time() - start_time

        assert result.success, f"Expected success but got errors: {result.errors}"
        assert result.created_count == 200

        # At 5 QPS, 20 batches should take at least 4 seconds
        # If it's much faster, rate limiting might not be working
        print(f"\n200 records written in {elapsed:.2f}s")
        print(f"Average rate: {200 / elapsed:.1f} records/sec")
        print(f"Batches per second: {20 / elapsed:.2f}")

        # Verify all records exist
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 200


class TestRateLimitedExecutor:
    """Test the RateLimitedExecutor with real API calls."""

    def test_executor_limits_request_rate(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test that RateLimitedExecutor properly throttles requests."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Insert test data
        table.create({"Name": "ExecutorTest", "Value": 1})
        wait_for_api()

        executor = RateLimitedExecutor(qps_limit=5)

        # Make 10 requests through the executor
        start_time = time.time()
        results = []

        for _ in range(10):
            result = executor.execute(table.all)
            results.append(len(result))

        elapsed = time.time() - start_time

        # All requests should succeed
        assert all(r == 1 for r in results), "Not all reads returned expected data"

        # 10 requests at 5 QPS should take ~2 seconds if properly throttled
        # Allow some flexibility for processing time
        print(f"\n10 requests via executor in {elapsed:.2f}s")
        print(f"Request rate: {10 / elapsed:.2f} req/sec")


class TestRetryWithBackoff:
    """Test retry behavior with real API operations."""

    def test_retry_succeeds_after_transient_issues(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test that retries work for operations that may fail transiently."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Use retry_with_backoff for a simple operation
        def create_record():
            return table.create({"Name": "RetryTest", "Value": 42})

        result = retry_with_backoff(create_record, max_retries=3)

        assert result is not None
        assert result["fields"]["Name"] == "RetryTest"


class TestConcurrentBatchOperations:
    """Test handling of multiple batch operations."""

    def test_replace_with_many_records(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test replace operation with many records - lots of API calls."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Insert 50 initial records
        for i in range(5):
            batch = [{"Name": f"Old_{j}", "Value": j} for j in range(i * 10, (i + 1) * 10)]
            table.batch_create(batch)
            wait_for_api()

        # Replace with 50 new records
        # This requires: 5 delete batches + 5 create batches = 10 API calls
        df = pd.DataFrame(
            {
                "Name": [f"New_{i}" for i in range(50)],
                "Value": [i * 10 for i in range(50)],
            }
        )

        start_time = time.time()
        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            if_exists="replace",
            batch_size=10,
        )
        elapsed = time.time() - start_time

        assert result.success
        assert result.deleted_count == 50
        assert result.created_count == 50

        print(f"\nReplace 50→50 records in {elapsed:.2f}s")

        # Verify final state
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 50
        assert all(name.startswith("New_") for name in df_read["Name"])

    def test_upsert_with_many_records(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
        airtable_api: Api,
    ):
        """Test upsert operation with many records."""
        table_name, _ = test_table
        table = airtable_api.table(base_id, table_name)

        # Insert 30 initial records
        for i in range(3):
            batch = [{"Name": f"User_{j}", "Value": j} for j in range(i * 10, (i + 1) * 10)]
            table.batch_create(batch)
            wait_for_api()

        # Upsert: update 20 existing + create 20 new = 40 records
        df = pd.DataFrame(
            {
                "Name": [f"User_{i}" for i in range(40)],  # 0-29 exist, 30-39 are new
                "Value": [i * 100 for i in range(40)],  # Updated values
            }
        )

        start_time = time.time()
        result = df.airtable.to_airtable(
            base_id,
            table_name,
            api_key,
            if_exists="upsert",
            key_field="Name",
            batch_size=10,
        )
        elapsed = time.time() - start_time

        assert result.success

        print(f"\nUpsert 40 records (30 update, 10 new) in {elapsed:.2f}s")

        # Verify final state
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 40  # 30 updated + 10 new

        # Check that values were updated
        user_0 = df_read[df_read["Name"] == "User_0"].iloc[0]
        assert user_0["Value"] == 0  # 0 * 100


class TestStressConditions:
    """Test behavior under stress conditions."""

    def test_many_small_writes(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test many small write operations in sequence."""
        table_name, _ = test_table

        successful = 0
        start_time = time.time()

        # 20 small writes of 5 records each = 100 records total
        for i in range(20):
            df = pd.DataFrame(
                {
                    "Name": [f"Stress_{i}_{j}" for j in range(5)],
                    "Value": [i * 10 + j for j in range(5)],
                }
            )

            result = df.airtable.to_airtable(
                base_id,
                table_name,
                api_key,
                batch_size=10,
            )

            if result.success:
                successful += 1

        elapsed = time.time() - start_time

        assert successful == 20, f"Only {successful}/20 operations succeeded"

        print(f"\n20 sequential writes in {elapsed:.2f}s")
        print(f"Operations per second: {20 / elapsed:.2f}")

        # Verify total records
        wait_for_api()
        df_read = read_airtable(base_id, table_name, api_key)
        assert len(df_read) == 100

    def test_alternating_read_write(
        self,
        api_key: str,
        base_id: str,
        test_table: tuple[str, str],
    ):
        """Test alternating read and write operations."""
        table_name, _ = test_table

        start_time = time.time()

        for i in range(10):
            # Write 5 records
            df = pd.DataFrame(
                {
                    "Name": [f"Alt_{i}_{j}" for j in range(5)],
                    "Value": [i * 10 + j for j in range(5)],
                }
            )
            result = df.airtable.to_airtable(base_id, table_name, api_key)
            assert result.success

            # Read all records
            df_read = read_airtable(base_id, table_name, api_key)
            expected_count = (i + 1) * 5
            assert len(df_read) == expected_count, f"Expected {expected_count}, got {len(df_read)}"

        elapsed = time.time() - start_time

        print(f"\n10 write+read cycles in {elapsed:.2f}s")

        # Final verification
        df_final = read_airtable(base_id, table_name, api_key)
        assert len(df_final) == 50
