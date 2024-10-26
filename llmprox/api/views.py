import json
from typing import AsyncGenerator

from django.conf import settings
from django.http import StreamingHttpResponse
from litellm import acompletion
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


async def stream_response(generator: AsyncGenerator) -> StreamingHttpResponse:
    """Stream the LLM response chunks to the client"""
    async def event_stream():
        try:
            async for chunk in generator:
                if chunk:
                    yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        }
    )


@api_view(["POST"])
@permission_classes([])  # This makes this specific endpoint public
async def llm_completion(request):
    """
    Forward LLM completion requests to the appropriate provider via LiteLLM
    with streaming support
    """
    try:
        # Extract request parameters
        model = request.data.get("model", "gpt-3.5-turbo")
        messages = request.data.get("messages", [])
        stream = request.data.get("stream", True)  # Default to streaming

        if not messages:
            return Response(
                {"error": "Messages array is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Forward request to LiteLLM
        response = await acompletion(
            model=model,
            messages=messages,
            api_key=settings.OPENAI_API_KEY,
            stream=stream
        )

        if stream:
            return await stream_response(response)
        
        return Response(response)

    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
