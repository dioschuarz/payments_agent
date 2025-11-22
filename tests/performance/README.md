# Performance Tests

This directory contains performance and load tests for the Send Money Agent.

## Target Performance

- **Request Rate**: 1000 requests per minute (approximately 16.67 requests per second)
- **Latency**: < 2 seconds for simple requests
- **Concurrency**: Support for multiple concurrent sessions
- **Success Rate**: > 95% under load

## Running Performance Tests

### Prerequisites

1. Start the application (Docker or local):
   ```bash
   docker compose up -d
   # or
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. Ensure the API is accessible at `http://localhost:8000`

### Run All Performance Tests

```bash
pytest tests/performance/ -v
```

### Run Specific Test

```bash
pytest tests/performance/test_rate_limiting.py::TestRateLimiting::test_requests_per_minute -v
```

## Test Cases

### `test_single_request_latency`
- **Purpose**: Verify individual request latency
- **Target**: < 2 seconds per request
- **Method**: Single request timing

### `test_concurrent_requests`
- **Purpose**: Test concurrent request handling
- **Target**: Handle 10 concurrent requests successfully
- **Method**: Parallel request execution

### `test_requests_per_minute`
- **Purpose**: Test sustained request rate
- **Target**: 60 requests per minute (baseline test)
- **Method**: Timed request distribution over 60 seconds

### `test_health_endpoint_performance`
- **Purpose**: Verify health endpoint can handle high throughput
- **Target**: > 50 requests per second
- **Method**: 100 rapid health check requests

### `test_session_isolation`
- **Purpose**: Verify session isolation under load
- **Target**: Maintain separate contexts for different sessions
- **Method**: Multiple concurrent sessions with follow-up messages

## Notes

- These tests use a reduced load (60 req/min) to avoid hitting API rate limits
- For full 1000 req/min testing, use a production environment with proper API quotas
- Tests are designed to be non-destructive and use unique session IDs

## Interpreting Results

- **Success Rate**: Should be > 95% under normal load
- **Average Latency**: Should be < 3 seconds
- **Throughput**: Should maintain target rate without degradation

