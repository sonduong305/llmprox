# llmprox/api/views.py
import logging
from typing import Any, Dict

import litellm
from adrf.decorators import api_view
from litellm import ModelResponse, acompletion
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.response import Response

from .exceptions import InvalidRequestError, LLMError
from .serializers import LLMCompletionSerializer

logger = logging.getLogger(__name__)

litellm.drop_params = True


async def process_llm_request(validated_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Asynchronously process the LLM request with validated data
    """
    try:
        response: ModelResponse = await acompletion(
            model=validated_data["model"],
            messages=validated_data["messages"],
            temperature=validated_data.get("temperature", 0.7),
            max_tokens=validated_data.get("max_tokens", 1000),
            top_p=validated_data.get("top_p", 1.0),
            frequency_penalty=validated_data.get("frequency_penalty", 0.0),
            presence_penalty=validated_data.get("presence_penalty", 0.0),
            stop=validated_data.get("stop", None),
        )

        return {
            "messages": [{"content": response.choices[0].message.content}],
            "metadata": {
                "model": response.model,
                "usage": response.usage,
                "created": response.created,
            },
        }
    except Exception as e:
        logger.error(f"Error in LLM request: {str(e)}", exc_info=True)
        raise LLMError(detail=str(e))


@api_view(["POST"])
@permission_classes([])
async def llm_completion(request):
    """
    Async view that handles LLM processing with enhanced validation and error handling
    """
    try:
        # Validate request data using serializer
        serializer = LLMCompletionSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid request data: {serializer.errors}")
            raise InvalidRequestError(detail=serializer.errors)

        # Process the request asynchronously with validated data
        response = await process_llm_request(serializer.validated_data)

        return Response(
            {"status": "success", "data": response}, status=status.HTTP_200_OK
        )

    except InvalidRequestError as e:
        return Response(
            {"status": "error", "error": "Invalid request", "details": e.detail},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except LLMError as e:
        return Response(
            {
                "status": "error",
                "error": "LLM processing error",
                "message": str(e.detail),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        logger.error(f"Unexpected error in llm_completion: {str(e)}", exc_info=True)
        return Response(
            {
                "status": "error",
                "error": "Internal server error",
                "message": "An unexpected error occurred while processing your request",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
