from __future__ import annotations

import hashlib
import hmac
import logging
from base64 import b64decode
from functools import wraps
from typing import Any, Callable

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden

from .settings import TEST_MODE, WEBHOOK_SECURITY_TOKEN

logger = logging.getLogger(__name__)


def _hmac(token: bytes, text: bytes) -> bytes:
    """
    Calculate SHA1 HMAC digest from request body and token.

    Args:
        token: bytes, the webhook token from Amiqus API settings.
        text: string, the text to hash.

    Return the SHA1 HMAC as a string.

    """
    return hmac.new(token, text, hashlib.sha256).digest()


def _match(token: bytes, request: HttpRequest) -> bool:
    """
    Calculate signature and return True if it matches header.

    Args:
        token: string, the webhook_token.
        request: an HttpRequest object from which the body content and
            X-Signature header will be extracted and matched.

    Returns True if there is a match.

    """
    signature_b64 = request.headers.get("x-aqid-signature")
    expected_signature = _hmac(token, request.body)
    received_signature = b64decode(signature_b64)
    return hmac.compare_digest(received_signature, expected_signature)


def verify_signature() -> Callable:
    """
    View function decorator used to verify Amiqus webhook signatures.

    This function uses the WEBHOOK_SECURITY_TOKEN specified in settings to calculate
    the HMAC. If it doesn't exist, then this decorator will immediately fail
    hard with an ImproperlyConfigured exception.

    If TEST_MODE is on (AMIQUS_TEST_MODE setting) then the verification will
    be ignored.

    See: https://amiqus.github.io/developers/api#tag/Webhooks

    Each webhook URL is associated with a secret token. This is
    visible in the amiqus dashboard for a given webhook.

    Events sent to your application will be signed using this token:
    verifying the request signature on your server prevents attackers
    from imitating valid webhooks. The HMAC digest signature, generated
    using SHA-1, will be stored in a X-Signature header.

    When you receive an event, you should compute a hash using your
    secret token, and ensure that the X-Signature sent by Amiqus
    matches that hash.

    If the HMAC signatures don't match, return a 403

    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def _wrapped_func(
            request: HttpRequest, *args: Any, **kwargs: Any
        ) -> HttpResponse:
            if TEST_MODE:
                logger.debug(
                    "Ignoring Amiqus callback verification (AMIQUS_TEST_MODE enabled)"
                )
                return func(request, *args, **kwargs)
            if not WEBHOOK_SECURITY_TOKEN:
                raise ImproperlyConfigured("Missing AMIQUS_WEBHOOK_SECURITY_TOKEN")
            if _match(WEBHOOK_SECURITY_TOKEN, request):
                return func(request, *args, **kwargs)
            else:
                # logging as a warning means it'll likely appear in logs,
                # but it's by design - if people are sending invalid requests
                # we need to know.
                logger.warning("Amiqus callback request verification failed.")
                return HttpResponseForbidden("Invalid X-Signature")

        return _wrapped_func

    return decorator
