from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from litellm import completion

@api_view(['POST'])
def llm_completion(request):
    """
    Forward LLM completion requests to the appropriate provider via LiteLLM
    """
    try:
        # Extract request parameters
        model = request.data.get('model', 'gpt-3.5-turbo')
        messages = request.data.get('messages', [])
        
        if not messages:
            return Response(
                {"error": "Messages array is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Forward request to LiteLLM
        response = completion(
            model=model,
            messages=messages,
            api_key=settings.OPENAI_API_KEY  # We'll add this to settings later
        )

        return Response(response)

    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
