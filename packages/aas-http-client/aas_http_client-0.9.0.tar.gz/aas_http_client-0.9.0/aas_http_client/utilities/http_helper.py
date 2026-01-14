"""Helper methods for HTTP operations."""

import json
import logging

from requests.models import Response

logger = logging.getLogger(__name__)

STATUS_CODE_200 = 200
STATUS_CODE_201 = 201
STATUS_CODE_204 = 204
STATUS_CODE_404 = 404


def log_response(response: Response, log_level: int = logging.ERROR):  # noqa: C901, PLR0912
    """Extracts and logs error messages from an HTTP response.

    This method parses the response content for error details, messages, or error fields,
    and logs each error message found. If the response cannot be decoded as JSON,
    it logs the raw response content. Always logs the HTTP status code.

    :param response: The HTTP response object to extract and log errors from
    :param log_level: The logging level to use (default is logging.ERROR)
    """
    result_error_messages: list[str] = []

    try:
        response_content_dict: dict = json.loads(response.content)

        if "detail" in response_content_dict:
            detail: dict = response_content_dict.get("detail", {})
            if "error" in detail:
                error: str = detail.get("error", "")
                result_error_messages.append(f"{error}")
            else:
                result_error_messages.append(f"{detail}")

        elif "messages" in response_content_dict or "Messages" in response_content_dict:
            messages: list = response_content_dict.get("messages", [])

            if not messages:
                messages = response_content_dict.get("Messages", [])

            for message in messages:
                if isinstance(message, dict) and "message" in message:
                    result_error_messages.append(message["message"])
                else:
                    result_error_messages.append(str(message))
        elif "error" in response_content_dict:
            result_error_messages.append(response_content_dict.get("error", ""))

        if len(result_error_messages) == 0 and response.text:
            result_error_messages.append(response.text)

    except json.JSONDecodeError:
        if response.content and response.content != "b''":
            result_error_messages.append(response.content)

    logger.log(log_level, f"Status code: {response.status_code}")
    for result_error_message in result_error_messages:
        logger.log(log_level, result_error_message)

    logger.debug(f"Full response content: {response.content}")
