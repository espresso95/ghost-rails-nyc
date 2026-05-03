from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Mapping

from app.models.errors import ModelProviderError


def post_json(
    url: str,
    payload: Mapping[str, Any],
    headers: Mapping[str, str] | None = None,
    timeout_seconds: int = 60,
    label: str = "model provider",
) -> Mapping[str, Any]:
    request_headers = {
        "Content-Type": "application/json",
        **(dict(headers) if headers else {}),
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=request_headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise ModelProviderError(f"{label} returned HTTP {error.code}: {body}") from error
    except urllib.error.URLError as error:
        raise ModelProviderError(f"{label} request failed: {error.reason}") from error

    if not body:
        return {}

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as error:
        raise ModelProviderError(f"{label} returned invalid JSON") from error

    if not isinstance(parsed, dict):
        raise ModelProviderError(f"{label} returned an unexpected JSON shape")

    return parsed

