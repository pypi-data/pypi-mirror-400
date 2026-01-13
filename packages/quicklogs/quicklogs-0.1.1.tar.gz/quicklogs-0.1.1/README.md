```python
"""
Examples of using the structured logger with Loki optimization.
"""

from quicklogs import (
    clear_request_context,
    configure_loki_logging,
    generate_request_id,
    get_struct_logger,
    set_request_context,
)


# Example 1: Basic service initialization
def initialize_service_logging():
    """Initialize logging for a service."""
    configure_loki_logging(
        app_name="dl-api-service",
        environment="production",
        extra_labels={"team": "platform", "service_type": "api"},
        log_level="INFO",
    )

    logger = get_struct_logger("service.init")
    logger.info("service_started", version="1.2.3", config_loaded=True)


# Example 2: Web request handling with context
async def handle_api_request(request):
    """Example of handling an API request with proper logging context."""
    # Generate request ID for correlation
    request_id = generate_request_id()
    trace_id = request.headers.get("X-Trace-ID", generate_request_id())

    # Set request context
    set_request_context(
        request_id=request_id,
        trace_id=trace_id,
        method=request.method,
        path=request.path,
        user_id=request.user.id if request.user else None,
    )

    logger = get_struct_logger("api.handler")

    try:
        logger.info("request_started", remote_ip=request.remote_addr)

        # Process request
        result = await process_request(request)

        logger.info("request_completed", status_code=200, response_time_ms=42.3)

        return result

    except Exception as e:
        logger.error("request_failed", error_type=type(e).__name__, exc_info=True)
        raise
    finally:
        clear_request_context()


# Example 3: Background task logging
def process_batch_job(job_id, items):
    """Example of logging in a background job."""
    logger = get_struct_logger("batch.processor", job_id=job_id, total_items=len(items))

    logger.info("job_started")

    processed = 0
    failed = 0

    for item in items:
        try:
            # Process item
            process_item(item)
            processed += 1

            # Log progress every 100 items
            if processed % 100 == 0:
                logger.info(
                    "job_progress",
                    processed=processed,
                    failed=failed,
                    remaining=len(items) - processed - failed,
                )

        except Exception as e:
            failed += 1
            logger.warning("item_failed", item_id=item.id, error=str(e), exc_info=True)

    logger.info(
        "job_completed",
        processed=processed,
        failed=failed,
        success_rate=processed / len(items) if items else 0,
    )


# Example 4: Database operations
class DatabaseLogger:
    """Example of logging database operations."""

    def __init__(self, db_name):
        self.logger = get_struct_logger("db.operations", database=db_name)

    def log_query(self, query, params, duration_ms):
        """Log a database query."""
        # Don't log sensitive data
        sanitized_query = query[:100] + "..." if len(query) > 100 else query

        self.logger.debug(
            "query_executed",
            query=sanitized_query,
            duration_ms=duration_ms,
            param_count=len(params) if params else 0,
        )

    def log_connection_pool_stats(self, stats):
        """Log connection pool statistics."""
        self.logger.info(
            "connection_pool_stats",
            active=stats["active"],
            idle=stats["idle"],
            total=stats["total"],
            wait_time_ms=stats.get("wait_time_ms"),
        )


# Example 5: Monitoring and metrics
def log_service_metrics(metrics):
    """Example of logging service metrics for Loki."""
    logger = get_struct_logger("metrics")

    # Log as structured data that can be queried in Loki
    logger.info(
        "service_metrics",
        cpu_percent=metrics["cpu_percent"],
        memory_mb=metrics["memory_mb"],
        active_connections=metrics["active_connections"],
        request_rate_per_sec=metrics["request_rate"],
        error_rate_per_sec=metrics["error_rate"],
        p95_latency_ms=metrics["p95_latency"],
    )


# Example 6: Development vs Production
def setup_logging_for_environment():
    """Configure logging based on environment."""
    import os

    is_development = os.getenv("ENVIRONMENT") == "development"

    configure_loki_logging(
        app_name="dl-service",
        environment=os.getenv("ENVIRONMENT", "production"),
        log_level="DEBUG" if is_development else "INFO",
        enable_console_renderer=is_development,  # Pretty print in dev
        include_process_info=is_development,  # Include PID/thread in dev
        max_string_length=5000 if is_development else 1000,
    )


if __name__ == "__main__":
    # Demo the examples
    initialize_service_logging()

    # Simulate some operations
    logger = get_struct_logger("examples.demo")
    logger.info("examples_executed", examples_count=6)
```