import logging
import boto3
from botocore.exceptions import ClientError

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

from .utils import (
    parse_bearer,
    attrs_to_dict,
    cache_key_for_token,
)

logger = logging.getLogger(__name__)


def _unauthorized(message: str = "Unauthorized"):
    return JsonResponse({"detail": message}, status=401)


class CognitoAuthMiddleware:
    """
    Django middleware for authenticating APIs using AWS Cognito Access Tokens.

    Attaches to request:
        - request.cognito_user
        - request.cognito_attributes
        - request.cognito_token
    """

    def __init__(self, get_response):
        self.get_response = get_response

        self.region = (
            getattr(settings, "COGNITO_REGION", None)
            or getattr(settings, "AWS_REGION", None)
            or "ap-south-1"
        )

        self.bypass_paths = set(
            getattr(settings, "COGNITO_BYPASS_PATHS", [])
        )

        self.cache_seconds = int(
            getattr(settings, "COGNITO_GET_USER_CACHE_SECONDS", 0) or 0
        )

        self.client = boto3.client(
            "cognito-idp",
            region_name=self.region
        )

    def __call__(self, request):
        # Bypass public paths
        if request.path in self.bypass_paths:
            return self.get_response(request)

        # Read Authorization header
        auth_header = (
            getattr(request, "headers", {}).get("Authorization")
            or request.META.get("HTTP_AUTHORIZATION")
        )

        token = parse_bearer(auth_header)
        if not token:
            return _unauthorized(
                "Missing or invalid Authorization header (Bearer token required)"
            )

        # Cache lookup
        if self.cache_seconds:
            cached = cache.get(cache_key_for_token(token))
            if cached:
                self._attach(request, cached, token)
                return self.get_response(request)

        # Call Cognito
        try:
            resp = self.client.get_user(AccessToken=token)
            username = resp.get("Username")
            attributes = attrs_to_dict(resp.get("UserAttributes"))

            data = {
                "username": username,
                "attributes": attributes,
            }

            self._attach(request, data, token)

            if self.cache_seconds:
                cache.set(
                    cache_key_for_token(token),
                    data,
                    timeout=self.cache_seconds,
                )

        except ClientError as e:
            code = (e.response.get("Error") or {}).get("Code")
            logger.warning("Cognito auth failed: %s", code)
            return _unauthorized("Invalid or expired access token")

        return self.get_response(request)

    def _attach(self, request, data, token):
        request.cognito_user = data["username"]
        request.cognito_attributes = data["attributes"]
        request.cognito_token = token
