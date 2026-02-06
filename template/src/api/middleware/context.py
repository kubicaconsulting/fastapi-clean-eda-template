from fastapi import Request

from infra.logging import get_logger
from infra.monitoring import tracer


logger = get_logger(__name__)


async def context_middleware(request: Request, call_next):
    # Start a new span for the incoming request
    with tracer.start_as_current_span("http_request") as span:
        # Get the current trace and span IDs
        span_context = span.get_span_context()
        trace_id = f"{span_context.trace_id:032x}"
        span_id = f"{span_context.span_id:016x}"

        # Add IDs to the logging context for the duration of the request
        with logger.contextualize(trace_id=trace_id, span_id=span_id):
            response = await call_next(request)
            return response
