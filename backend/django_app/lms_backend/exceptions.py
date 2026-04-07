"""
Custom exception handler for consistent API error format across the LMS.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Returns JSON errors in a consistent format:
    {
        "success": false,
        "error": {
            "code": "validation_error",
            "message": "Human-readable message",
            "details": {...}
        }
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'success': False,
            'error': {
                'code': _get_error_code(response.status_code),
                'message': _get_error_message(response.data),
                'details': response.data,
            }
        }
        response.data = error_data
    else:
        # Unhandled exception — return 500
        logger.exception("Unhandled exception in view: %s", exc)
        response = Response(
            {
                'success': False,
                'error': {
                    'code': 'internal_server_error',
                    'message': 'An unexpected error occurred. Please try again.',
                    'details': {},
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def _get_error_code(status_code):
    codes = {
        400: 'bad_request',
        401: 'unauthorized',
        403: 'forbidden',
        404: 'not_found',
        405: 'method_not_allowed',
        409: 'conflict',
        422: 'validation_error',
        429: 'rate_limited',
        500: 'internal_server_error',
    }
    return codes.get(status_code, 'error')


def _get_error_message(data):
    if isinstance(data, dict):
        if 'detail' in data:
            return str(data['detail'])
        # Flatten field errors into a single message
        for key, val in data.items():
            if isinstance(val, list) and val:
                return f"{key}: {val[0]}"
            elif isinstance(val, str):
                return f"{key}: {val}"
    elif isinstance(data, list) and data:
        return str(data[0])
    return 'An error occurred.'
