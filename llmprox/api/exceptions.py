from rest_framework import status
from rest_framework.exceptions import APIException


class LLMError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An error occurred while processing the LLM request"
    default_code = "llm_error"


class RateLimitError(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "Rate limit exceeded"
    default_code = "rate_limit_exceeded"


class InvalidRequestError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid request parameters"
    default_code = "invalid_request"
