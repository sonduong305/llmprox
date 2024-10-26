from unittest.mock import AsyncMock, patch

import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory

pytestmark = pytest.mark.django_db


@pytest.mark.asyncio
async def test_llm_completion_success():
    """Test successful completion request"""
    factory = APIRequestFactory()

    request_data = {
        "messages": [
            {
                "role": "system",
                "content": "You are an English -> Spanish translator. If a user writes something in English, reply by translating that into Spanish.",
            },
            {"role": "user", "content": "orange, apple, watermelon"},
        ]
    }

    request = factory.post(
        reverse("chat-completion"),
        request_data,
        format="json",
        HTTP_AUTHORIZATION=f"Token {settings.API_TOKEN}",
    )

    with patch(
        "llmprox.api.views.acompletion", new_callable=AsyncMock
    ) as mock_completion:
        mock_completion.return_value = AsyncMock(
            choices=[AsyncMock(message=AsyncMock(content="naranja, manzana, sandía"))],
            model="gpt-3.5-turbo",
            usage={"total_tokens": 10, "prompt_tokens": 5, "completion_tokens": 5},
            created=1616461000,
        )

        from llmprox.api.views import llm_completion

        response = await llm_completion(request)

        assert response.status_code == status.HTTP_200_OK
        assert "messages" in response.data
        assert response.data["messages"][0]["content"] == "naranja, manzana, sandía"
        assert "metadata" in response.data


@pytest.mark.asyncio
async def test_llm_completion_unauthorized():
    """Test unauthorized request handling"""
    factory = APIRequestFactory()

    request_data = {"messages": [{"role": "user", "content": "Hello!"}]}

    request = factory.post(reverse("chat-completion"), request_data, format="json")

    from llmprox.api.views import llm_completion

    response = await llm_completion(request)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_llm_completion_invalid_token():
    """Test invalid token handling"""
    factory = APIRequestFactory()

    request_data = {"messages": [{"role": "user", "content": "Hello!"}]}

    request = factory.post(
        reverse("chat-completion"),
        request_data,
        format="json",
        HTTP_AUTHORIZATION="Token invalid_token",
    )

    from llmprox.api.views import llm_completion

    response = await llm_completion(request)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_llm_completion_invalid_request():
    """Test invalid request handling"""
    factory = APIRequestFactory()

    # Invalid request data (missing required fields)
    request_data = {}

    request = factory.post(
        reverse("chat-completion"),
        request_data,
        format="json",
        HTTP_AUTHORIZATION=f"Token {settings.API_TOKEN}",
    )

    from llmprox.api.views import llm_completion

    response = await llm_completion(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data
    assert "details" in response.data


@pytest.mark.asyncio
async def test_llm_completion_llm_error():
    """Test LLM error handling"""
    factory = APIRequestFactory()

    request_data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello!"}],
    }

    request = factory.post(
        reverse("chat-completion"),
        request_data,
        format="json",
        HTTP_AUTHORIZATION=f"Token {settings.API_TOKEN}",
    )

    # Mock the litellm.acompletion function to raise an exception
    with patch(
        "llmprox.api.views.acompletion", new_callable=AsyncMock
    ) as mock_completion:
        mock_completion.side_effect = Exception("LLM Error")

        from llmprox.api.views import llm_completion

        response = await llm_completion(request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "error" in response.data
        assert "message" in response.data


@pytest.mark.asyncio
async def test_llm_completion_with_optional_params():
    """Test completion request with optional parameters"""
    factory = APIRequestFactory()

    request_data = {
        "messages": [{"role": "user", "content": "Hello!"}],
        "params": {
            "model": "gpt-3.5-turbo",
            "temperature": 0.5,
            "max_tokens": 500,
        },
    }

    request = factory.post(
        reverse("chat-completion"),
        request_data,
        format="json",
        HTTP_AUTHORIZATION=f"Token {settings.API_TOKEN}",
    )

    with patch(
        "llmprox.api.views.acompletion", new_callable=AsyncMock
    ) as mock_completion:
        mock_completion.return_value = AsyncMock(
            choices=[AsyncMock(message=AsyncMock(content="Custom response"))],
            model="gpt-3.5-turbo",
            usage={"total_tokens": 10, "prompt_tokens": 5, "completion_tokens": 5},
            created=1616461000,
        )

        from llmprox.api.views import llm_completion

        response = await llm_completion(request)

        assert response.status_code == status.HTTP_200_OK


# Add the serializer test
def test_llm_completion_serializer():
    """Test LLMCompletionSerializer validation"""
    from llmprox.api.serializers import LLMCompletionSerializer

    valid_data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello!"}],
        "temperature": 0.7,
        "max_tokens": 1000,
    }

    serializer = LLMCompletionSerializer(data=valid_data)
    assert serializer.is_valid()

    invalid_data = {
        "model": "gpt-3.5-turbo",
        # Missing messages field
        "temperature": 2.0,  # Invalid temperature value
    }

    serializer = LLMCompletionSerializer(data=invalid_data)
    assert not serializer.is_valid()
