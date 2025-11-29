import re
from functools import wraps
from time import time
from django.http import HttpResponse

_rate_memory = {}

SANITIZE_PATTERN = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F]')
TAG_PATTERN = re.compile(r'<\s*script[^>]*>|<\s*/\s*script\s*>', re.IGNORECASE)
ANGLE_PATTERN = re.compile(r'[<>]')


def sanitize_input(value):
    """Basic sanitizer: remove control chars, strip script tags, neutralize angle brackets.
    Returns sanitized string or original if not str.
    """
    if not isinstance(value, str):
        return value
    v = value.strip()
    v = SANITIZE_PATTERN.sub('', v)
    v = TAG_PATTERN.sub('', v)
    # Replace angle brackets with entities to avoid HTML interpretation
    v = ANGLE_PATTERN.sub('', v)
    return v


def rate_limit(limit=10, window=60, key='ip'):
    """Simple in-memory rate limit decorator (development stub).
    limit: max requests per window seconds.
    key: 'ip' or 'user'.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            identifier = None
            if key == 'user' and request.user.is_authenticated:
                identifier = f'user:{request.user.id}'
            else:
                # Fallback to IP
                identifier = request.META.get('REMOTE_ADDR', 'unknown')
            now = time()
            bucket = _rate_memory.setdefault(identifier, [])
            # Purge old timestamps
            bucket = [t for t in bucket if now - t < window]
            _rate_memory[identifier] = bucket
            if len(bucket) >= limit:
                return HttpResponse('Rate limit exceeded', status=429)
            bucket.append(now)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
