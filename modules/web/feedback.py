"""Shapes of the feedback the browser shows: error modals and toasts.

Plain dicts and strings, so views decide the HTTP response and this stays testable.
"""

from __future__ import annotations

import json


def problem(title: str, message: str = "", errors: dict | None = None) -> dict:
    """Body of a 4xx/5xx reply; the front end opens an error modal from it."""
    return {"title": title, "message": message, "errors": errors or {}}


def toast_header(message: str, variant: str = "success") -> str:
    """Value for an HX-Trigger header that makes the front end show a toast."""
    return json.dumps({"toast": {"message": message, "variant": variant}})
