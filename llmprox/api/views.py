# llmprox/chat/views.py
import logging

from adrf.decorators import api_view
from django.conf import settings
from litellm import acompletion
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.response import Response

logger = logging.getLogger(__name__)


async def process_llm_request(model: str, messages: list):
    """
    Asynchronously process the LLM request
    """
    try:
        response = await acompletion(
            model=model,
            messages=messages,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7,
            max_tokens=1000,
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
        logger.error(f"Error in LLM request: {str(e)}")
        raise


@api_view(["POST"])
@permission_classes([])
async def llm_completion(request):
    """
    Async view that handles LLM processing
    """
    try:
        # Extract and validate request data
        model = request.data.get("model", "gpt-3.5-turbo")
        messages = request.data.get("messages", [])

        if not messages:
            return Response(
                {"status": "error", "error": "Messages array is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Process the request asynchronously
        response = await process_llm_request(model, messages)

        return Response({"status": "success", "data": response})

    except Exception as e:
        logger.error(f"Error in llm_completion: {str(e)}", exc_info=True)
        return Response(
            {
                "status": "error",
                "error": str(e),
                "message": "An error occurred while processing your request",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
