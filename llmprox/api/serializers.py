from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=["system", "user", "assistant"],
        required=True,
        error_messages={
            "invalid_choice": "Role must be one of: system, user, assistant"
        },
    )
    content = serializers.CharField(
        required=True,
        max_length=4096,
        error_messages={
            "required": "Message content is required",
            "max_length": "Message content exceeds maximum length of 4096 characters",
        },
    )


class LLMCompletionSerializer(serializers.Serializer):
    model = serializers.CharField(
        required=True,
        max_length=100,
        error_messages={"max_length": "Model name is too long"},
    )
    messages = MessageSerializer(
        many=True,
        required=True,
        error_messages={
            "required": "Messages array is required",
            "empty": "Messages array cannot be empty",
        },
    )
    temperature = serializers.FloatField(
        default=0.7,
        min_value=0.0,
        max_value=2.0,
        error_messages={
            "min_value": "Temperature must be >= 0",
            "max_value": "Temperature must be <= 2",
        },
    )
    max_tokens = serializers.IntegerField(
        default=1000,
        min_value=1,
        max_value=4096,
        error_messages={
            "min_value": "max_tokens must be >= 1",
            "max_value": "max_tokens must be <= 4096",
        },
    )
    top_p = serializers.FloatField(
        default=1.0, min_value=0.0, max_value=1.0, required=False
    )
    frequency_penalty = serializers.FloatField(
        default=0.0, min_value=-2.0, max_value=2.0, required=False
    )
    presence_penalty = serializers.FloatField(
        default=0.0, min_value=-2.0, max_value=2.0, required=False
    )
    stop = serializers.ListField(
        child=serializers.CharField(max_length=100), required=False, max_length=4
    )
