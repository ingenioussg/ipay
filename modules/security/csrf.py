"""A per-session token on every form that changes something, so another website
cannot submit a form here on a signed-in person's behalf.

Works on any dict-like session, so it carries no Flask import and is tested
without starting the application.
"""

from __future__ import annotations

import hmac
import secrets

KEY = "csrf"


def csrf_token(session) -> str:
    """The session's token, created on first use."""
    token = session.get(KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        session[KEY] = token
    return token


def csrf_valid(session, submitted: object) -> bool:
    """True only when the form sent back this session's token."""
    token = session.get(KEY)
    if not token or not isinstance(submitted, str) or not submitted:
        return False
    # As bytes: compare_digest refuses str with non-ASCII characters, and a
    # forged form must get a refusal, not an error page.
    return hmac.compare_digest(token.encode("utf-8"), submitted.encode("utf-8"))
