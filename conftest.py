# llmprox/api/tests/conftest.py

import pytest
from rest_framework.test import APIRequestFactory


@pytest.fixture
def api_factory():
    return APIRequestFactory()


@pytest.fixture
def sample_completion_request():
    return {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello!"}],
        "temperature": 0.7,
        "max_tokens": 1000,
    }


@pytest.fixture
def mock_completion_response():
    class MockChoice:
        def __init__(self):
            self.message = type(
                "Message", (), {"content": "Hello! How can I help you today?"}
            )()

    class MockResponse:
        def __init__(self):
            self.choices = [MockChoice()]
            self.model = "gpt-3.5-turbo"
            self.usage = {
                "total_tokens": 10,
                "prompt_tokens": 5,
                "completion_tokens": 5,
            }
            self.created = 1616461000

    return MockResponse()
