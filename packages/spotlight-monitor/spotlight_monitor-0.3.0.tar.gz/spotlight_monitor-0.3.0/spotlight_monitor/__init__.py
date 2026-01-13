"""
Spotlight SDK

AI-powered service monitoring with Sentry-style exception tracking.

Usage:
    from spotlight_monitor import Spotlight

    app = FastAPI()
    spotlight = Spotlight(api_key="sp_xxx")
    spotlight.instrument(app)

    # Optional: custom validators
    @spotlight.validator(endpoint="/pills/*")
    def check_pills(request, response):
        if not response.get("pills"):
            return False, "No pills returned"
        return True, None

    # Manual exception capture
    try:
        risky_operation()
    except Exception as e:
        spotlight.capture_exception(e)
        raise
"""
from .client import Spotlight
from .models import RequestMetric, ValidationResult, HealthCheck, MetricsBatch
from .validators import ValidatorRegistry, validator
from .exceptions import (
    Breadcrumb,
    RequestContext,
    capture_exception,
    ExceptionInfo,
)

__version__ = "0.2.0"
__all__ = [
    "Spotlight",
    "RequestMetric",
    "ValidationResult",
    "HealthCheck",
    "MetricsBatch",
    "ValidatorRegistry",
    "validator",
    "Breadcrumb",
    "RequestContext",
    "capture_exception",
    "ExceptionInfo",
]