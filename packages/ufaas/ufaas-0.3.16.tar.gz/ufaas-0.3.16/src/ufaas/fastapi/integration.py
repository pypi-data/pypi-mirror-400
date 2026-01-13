"""FastAPI integration utilities for UFaaS."""

from fastapi import Request
from fastapi.responses import JSONResponse

from ..exceptions import UFaaSError


def ufaas_exception_handler(request: Request, exc: UFaaSError) -> JSONResponse:
    """
    Handle UFaaS exceptions in FastAPI.

    Args:
        request: FastAPI request object
        exc: UFaaS exception to handle

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message, "error": exc.error},
    )


EXCEPTION_HANDLERS = {UFaaSError: ufaas_exception_handler}
