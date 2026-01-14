from typing import Any, Dict, List, Optional
import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .exceptions import (
    AuthError,
    DuplicatedError,
    NotFoundError,
    PermissionDeniedError,
    UnauthorizedError,
    ValidationError,
    BadRequestError,
    ConflictError,
    InternalServerError,
    RateLimitExceededError,
    ServiceUnavailableError,
    GenericHttpError
)

logger = logging.getLogger(__name__)


def create_error_response(
    status_code: int,
    message: str,
    error: str,
    error_type: str,
    details: Optional[Any] = None,
    errors: Optional[List[Dict[str, Any]]] = None
) -> JSONResponse:
    """
    Create a standardized error response format
    """
    response_content = {
        "status_code": status_code or 500,
        "message": message,
        "error": error,
        "type": error_type,
    }

    if details:
        response_content["details"] = details
    if errors:
        response_content["errors"] = errors

    return JSONResponse(
        status_code=status_code or 500,
        content=response_content,
    )


def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    # Log full error details for Kubernetes logs and Application Insights
    logger.error(
        f"Request validation error - Path: {request.url.path}, Method: {request.method}, "
        f"Errors: {exc.errors()}"
    )

    # Return sanitized error response without technical details
    errors = [
        {
            "field": ".".join(str(x) for x in err["loc"]),
            "message": err["msg"],
        }
        for err in exc.errors()
    ]

    return create_error_response(
        status_code=422,
        message="Request validation failed",
        error="Invalid request data",
        error_type="RequestValidationError",
        errors=errors,
    )


def global_exception_handler(request: Request, exc: Exception):
    # Log full error details for Kubernetes logs and Application Insights
    logger.error(
        f"Unexpected error - Path: {request.url.path}, Method: {request.method}, "
        f"Error: {exc.__class__.__name__}: {exc}",
        exc_info=True
    )

    # Return generic error response without technical details
    return create_error_response(
        status_code=500,
        message="An unexpected error occurred",
        error="Internal server error",
        error_type="InternalServerError",
    )


def duplicated_error_handler(request: Request, exc: DuplicatedError):
    # Log full error details for Kubernetes logs and Application Insights
    logger.error(
        f"Duplicate error - Path: {request.url.path}, Method: {request.method}, "
        f"Detail: {exc.detail}"
    )

    # Return user-facing error without technical details
    return create_error_response(
        status_code=409,
        message="Duplicate entry found",
        error="Resource already exists",
        error_type="DuplicatedError",
    )


def auth_error_handler(request: Request, exc: AuthError):
    # Log full error details for Kubernetes logs and Application Insights
    logger.error(
        f"Authentication error - Path: {request.url.path}, Method: {request.method}, "
        f"Detail: {exc.detail}"
    )

    # Return generic auth error without technical details
    return create_error_response(
        status_code=403,
        message="Authentication failed",
        error="Access denied",
        error_type="AuthError",
    )


def not_found_error_handler(request: Request, exc: NotFoundError):
    # Log full error details for Kubernetes logs and Application Insights
    logger.error(
        f"Not found error - Path: {request.url.path}, Method: {request.method}, "
        f"Detail: {exc.detail}"
    )

    # Return generic not found error without technical details
    return create_error_response(
        status_code=404,
        message="Resource not found",
        error="The requested resource does not exist",
        error_type="NotFoundError",
    )


def validation_error_handler(request: Request, exc: ValidationError):
    # Log full error details for Kubernetes logs and Application Insights
    logger.error(
        f"Validation error - Path: {request.url.path}, Method: {request.method}, "
        f"Detail: {exc.detail}"
    )

    # Return generic validation error without technical details
    return create_error_response(
        status_code=422,
        message="Validation failed",
        error="Invalid data provided",
        error_type="ValidationError",
    )


def permission_denied_error_handler(request: Request, exc: PermissionDeniedError):
    # Log full error details for Kubernetes logs and Application Insights
    logger.error(
        f"Permission denied - Path: {request.url.path}, Method: {request.method}, "
        f"Detail: {exc.detail}"
    )

    # Return generic permission error without technical details
    return create_error_response(
        status_code=403,
        message="Permission denied",
        error="You do not have permission to access this resource",
        error_type="PermissionDeniedError",
    )


def unauthorized_error_handler(request: Request, exc: UnauthorizedError):
    # Log full error details for Kubernetes logs and Application Insights
    logger.error(
        f"Unauthorized access - Path: {request.url.path}, Method: {request.method}, "
        f"Detail: {exc.detail}"
    )

    # Return generic unauthorized error without technical details
    return create_error_response(
        status_code=401,
        message="Unauthorized access",
        error="Authentication required",
        error_type="UnauthorizedError",
    )

def bad_request_error_handler(request: Request, exc: BadRequestError):
    # Log full error details for Kubernetes logs and Application Insights
    logger.error(
        f"Bad request - Path: {request.url.path}, Method: {request.method}, "
        f"Detail: {exc.detail}"
    )

    # Return generic bad request error without technical details
    return create_error_response(
        status_code=400,
        message="Bad request",
        error="Invalid request",
        error_type="BadRequestError",
    )


def conflict_error_handler(request: Request, exc: ConflictError):
    # Log full error details for Kubernetes logs and Application Insights
    logger.error(
        f"Conflict error - Path: {request.url.path}, Method: {request.method}, "
        f"Detail: {exc.detail}"
    )

    # Return generic conflict error without technical details
    return create_error_response(
        status_code=409,
        message="Conflict occurred",
        error="Request conflicts with current state",
        error_type="ConflictError",
    )


def internal_server_error_handler(request: Request, exc: InternalServerError):
    # Log full error details for Kubernetes logs and Application Insights
    logger.error(
        f"Internal server error - Path: {request.url.path}, Method: {request.method}, "
        f"Detail: {exc.detail}",
        exc_info=True
    )

    # Return generic error without technical details
    return create_error_response(
        status_code=500,
        message="Internal server error",
        error="An internal error occurred",
        error_type="InternalServerError",
    )


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceededError):
    # Log full error details for Kubernetes logs and Application Insights
    logger.warning(
        f"Rate limit exceeded - Path: {request.url.path}, Method: {request.method}, "
        f"Detail: {exc.detail}"
    )

    # Return generic rate limit error without technical details
    return create_error_response(
        status_code=429,
        message="Rate limit exceeded",
        error="Too many requests",
        error_type="RateLimitExceededError",
    )


def service_unavailable_handler(request: Request, exc: ServiceUnavailableError):
    # Log full error details for Kubernetes logs and Application Insights
    logger.error(
        f"Service unavailable - Path: {request.url.path}, Method: {request.method}, "
        f"Detail: {exc.detail}"
    )

    # Return generic service unavailable error without technical details
    return create_error_response(
        status_code=503,
        message="Service is currently unavailable",
        error="Service temporarily unavailable",
        error_type="ServiceUnavailableError",
    )

def generic_http_error_handler(request: Request, exc: GenericHttpError):
    # Log full error details for Kubernetes logs and Application Insights
    logger.error(
        f"HTTP error - Path: {request.url.path}, Method: {request.method}, "
        f"Status: {exc.status_code}, Type: {exc.error_type}, Detail: {exc.detail}"
    )

    # Return error without technical details
    return create_error_response(
        status_code=exc.status_code,
        message=exc.message or "An error occurred",
        error="Request failed",
        error_type=exc.error_type or "GenericHttpError",
    )