from django.conf import settings
from rest_framework import authentication, exceptions


class APITokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            raise exceptions.AuthenticationFailed("No authentication token provided")

        try:
            # Expected format: "Token <token>"
            auth_parts = auth_header.split()
            if auth_parts[0].lower() != "token":
                raise exceptions.AuthenticationFailed(
                    "Invalid authentication header format"
                )

            if len(auth_parts) != 2:
                raise exceptions.AuthenticationFailed(
                    "Invalid authentication header format"
                )

            token = auth_parts[1]

            # Compare with the fixed token from settings
            if token != settings.API_TOKEN:
                raise exceptions.AuthenticationFailed("Invalid token")

        except Exception as e:
            raise exceptions.AuthenticationFailed("Invalid authentication token")

        # Return None for user since we're not using user authentication
        return (None, None)
