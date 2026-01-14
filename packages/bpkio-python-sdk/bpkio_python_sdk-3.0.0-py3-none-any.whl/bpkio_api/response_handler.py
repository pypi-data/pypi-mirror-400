import json

from loguru import logger

import bpkio_api.exceptions as errors
from bpkio_api.caching import clear_cache
from bpkio_api.helpers.recorder import SessionRecorder


def postprocess_response(response):
    """Checks whether or not the response was successful."""

    headers = response.request.headers
    body = response.request.body
    if "Authorization" in headers:
        auth = headers.get("Authorization")
        headers["Authorization"] = auth[0:10] + "*****" + auth[-5:]

    logger.debug(response.request.method + " " + response.request.url)
    logger.debug(f"headers: {headers}")
    logger.debug(f"body: {body}")
    logger.debug(f"> ({response.status_code}) -> {response.text}")

    # Record into the session
    SessionRecorder.record(response)

    if 200 <= response.status_code < 300:
        # invalidate cache for operations that change lists of resources
        if response.request.method in ("PUT", "DELETE", "POST"):
            clear_cache()

        # Pass through the response.
        return response

    if response.status_code >= 500:
        raise errors.BroadpeakIoApiError(
            url=response.url,
            status_code=response.status_code,
            message=response.text,
            reason=response.reason,
        )

    if response.status_code == 404:
        raise errors.NotFoundError(
            url=response.url,
            status_code=response.status_code,
            message=response.text,
            reason=response.reason,
        )

    response_payload = json.loads(response.text)

    # Handle 401 Unauthorized (including password expired)
    if response.status_code == 401:
        message = response_payload.get("message", "").lower()
        if "password has expired" in message or "password expired" in message:
            raise errors.PasswordExpiredError(
                response_payload.get("message", "Your password has expired")
            )
        raise errors.UnauthorizedError(
            url=response.url,
            status_code=response.status_code,
            message=response_payload.get("message", "Unauthorized"),
            reason=response.reason,
        )

    if response.status_code == 403:
        if (
            "existing" in response_payload["message"]
            or "with the same" in response_payload["message"]
        ):
            raise errors.ResourceExistsError(
                url=response.url,
                status_code=response.status_code,
                message=response_payload["message"],
                reason=response.reason,
            )

        raise errors.AccessForbiddenError(
            url=response.url,
            status_code=response.status_code,
            message=response_payload["message"],
            reason=response.reason,
        )
    else:
        raise errors.BroadpeakIoApiError(
            url=response.url,
            status_code=response.status_code,
            message=response_payload["message"],
            reason=response.reason,
        )


def extract_count(response):
    return int(response.headers["x-pagination-total-count"])
