"""
API Key authentication for business/developer API access.
"""
import hashlib
import hmac

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class APIKeyAuthentication(BaseAuthentication):
    """
    Authenticates requests using API key via Authorization header.
    Format: Authorization: Bearer sp_live_xxxxx
    """
    keyword = "Bearer"

    def authenticate(self, request):
        from apps.accounts.models import APIKey

        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header.startswith(f"{self.keyword} "):
            return None

        token = header[len(self.keyword) + 1:].strip()
        if not token:
            return None

        # Determine environment from key prefix
        environment = "production" if token.startswith("sp_live_") else "sandbox"

        # Hash the token for lookup
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        api_key = APIKey.objects.filter(
            key_hash=token_hash,
            environment=environment,
            is_active=True,
        ).select_related("business", "business__owner").first()

        if not api_key:
            raise AuthenticationFailed("Invalid API key")

        if api_key.is_expired:
            raise AuthenticationFailed("API key has expired")

        return (api_key.business.owner, api_key)

    def authenticate_header(self, request):
        return self.keyword
