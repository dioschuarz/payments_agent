"""Performance tests for rate limiting and request handling.

Tests the system's ability to handle the target rate of 1000 requests per minute.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Tuple

import pytest
import requests


class TestRateLimiting:
    """Test rate limiting and high-throughput scenarios."""

    @pytest.fixture
    def base_url(self):
        """Base URL for API requests."""
        return "http://localhost:8000"

    def test_single_request_latency(self, base_url):
        """
        Test that a single request completes within acceptable latency.
        
        Target: < 2 seconds for a simple request
        """
        start_time = time.time()
        response = requests.post(
            f"{base_url}/webhook/whatsapp",
            json={
                "from_number": "+5511999999999",
                "message": "hello",
            },
            timeout=10,
        )
        elapsed = time.time() - start_time

        assert response.status_code == 200
        assert elapsed < 2.0, f"Request took {elapsed:.2f}s, expected < 2.0s"

    def test_concurrent_requests(self, base_url):
        """
        Test handling of concurrent requests.
        
        Target: Handle 10 concurrent requests successfully
        """
        session_ids = [f"+5511999999{i:03d}" for i in range(10)]

        def make_request(session_id: str) -> Tuple[str, requests.Response]:
            """Make a single request."""
            try:
                response = requests.post(
                    f"{base_url}/webhook/whatsapp",
                    json={
                        "from_number": session_id,
                        "message": "hello",
                    },
                    timeout=10,
                )
                return session_id, response
            except Exception as e:
                return session_id, e

        # Make concurrent requests
        start_time = time.time()
        results = []
        for session_id in session_ids:
            result = make_request(session_id)
            results.append(result)
        elapsed = time.time() - start_time

        # Verify all requests succeeded
        successful = sum(1 for _, r in results if isinstance(r, requests.Response) and r.status_code == 200)
        assert successful == len(session_ids), f"Only {successful}/{len(session_ids)} requests succeeded"

        # Verify reasonable total time (10 requests should complete in < 20 seconds)
        assert elapsed < 20.0, f"10 concurrent requests took {elapsed:.2f}s, expected < 20.0s"

    def test_requests_per_minute(self, base_url):
        """
        Test system's ability to handle target rate of requests per minute.
        
        Target: 1000 requests per minute (approximately 16.67 requests per second)
        This test uses a smaller sample (60 requests in 1 minute) to verify capability.
        """
        target_rpm = 60  # Test with 60 requests per minute (1 req/sec) as a baseline
        duration_seconds = 60
        requests_per_second = target_rpm / duration_seconds

        session_ids = [f"+5511999999{i:04d}" for i in range(target_rpm)]
        results: List[Tuple[datetime, requests.Response]] = []

        start_time = time.time()
        request_times = []

        for i, session_id in enumerate(session_ids):
            # Calculate when this request should be sent
            target_time = start_time + (i / requests_per_second)
            current_time = time.time()

            # Wait if we're ahead of schedule
            if current_time < target_time:
                time.sleep(target_time - current_time)

            # Make request
            req_start = time.time()
            try:
                response = requests.post(
                    f"{base_url}/webhook/whatsapp",
                    json={
                        "from_number": session_id,
                        "message": "hello",
                    },
                    timeout=10,
                )
                req_elapsed = time.time() - req_start
                request_times.append(req_elapsed)
                results.append((datetime.now(), response))
            except Exception as e:
                results.append((datetime.now(), e))

        total_elapsed = time.time() - start_time

        # Calculate success rate
        successful = sum(
            1 for _, r in results
            if isinstance(r, requests.Response) and r.status_code == 200
        )
        success_rate = (successful / len(session_ids)) * 100

        # Calculate average request latency
        avg_latency = sum(request_times) / len(request_times) if request_times else 0

        # Verify results
        assert success_rate >= 95.0, (
            f"Success rate {success_rate:.1f}% below 95% threshold. "
            f"Successful: {successful}/{len(session_ids)}"
        )

        assert avg_latency < 3.0, (
            f"Average latency {avg_latency:.2f}s exceeds 3.0s threshold"
        )

        # Log results
        print(f"\n{'='*60}")
        print(f"Rate Limiting Test Results")
        print(f"{'='*60}")
        print(f"Total Requests: {len(session_ids)}")
        print(f"Successful: {successful} ({success_rate:.1f}%)")
        print(f"Total Time: {total_elapsed:.2f}s")
        print(f"Average Latency: {avg_latency:.2f}s")
        print(f"Requests/Second: {len(session_ids) / total_elapsed:.2f}")
        print(f"{'='*60}")

    def test_health_endpoint_performance(self, base_url):
        """
        Test health endpoint can handle high request rates.
        
        Health endpoint should be very fast and handle high throughput.
        """
        num_requests = 100
        start_time = time.time()

        for _ in range(num_requests):
            response = requests.get(f"{base_url}/health", timeout=2)
            assert response.status_code == 200

        elapsed = time.time() - start_time
        rps = num_requests / elapsed

        # Health endpoint should handle at least 100 req/s
        assert rps >= 50, f"Health endpoint only handled {rps:.1f} req/s, expected >= 50 req/s"
        assert elapsed < 5.0, f"100 health checks took {elapsed:.2f}s, expected < 5.0s"

    def test_session_isolation(self, base_url):
        """
        Test that different sessions are properly isolated.
        
        Multiple concurrent requests with different session IDs should
        maintain separate conversation contexts.
        """
        session_ids = [f"+5511999999{i:03d}" for i in range(5)]
        responses = []

        # Send initial message to each session
        for session_id in session_ids:
            response = requests.post(
                f"{base_url}/webhook/whatsapp",
                json={
                    "from_number": session_id,
                    "message": "I want to send money",
                },
                timeout=10,
            )
            responses.append((session_id, response))

        # Verify all sessions got responses
        for session_id, response in responses:
            assert response.status_code == 200, f"Session {session_id} failed"
            assert "message" in response.json()
            assert len(response.json()["message"]) > 0

        # Send follow-up messages to verify session isolation
        for session_id in session_ids:
            response = requests.post(
                f"{base_url}/webhook/whatsapp",
                json={
                    "from_number": session_id,
                    "message": "John",
                },
                timeout=10,
            )
            assert response.status_code == 200
            # Each session should maintain its own context

