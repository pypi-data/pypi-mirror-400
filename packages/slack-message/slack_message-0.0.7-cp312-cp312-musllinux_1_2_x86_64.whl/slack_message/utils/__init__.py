import re
import inspect
import functools
from typing import Any
from datetime import datetime
from slack_sdk import WebClient


def get_all_users_paginated(client: WebClient):
    all_users = []
    cursor = None

    try:
        while True:
            if cursor:
                response = client.users_list(cursor=cursor, limit=1000)
            else:
                response = client.users_list(limit=1000)

            if response["ok"]:
                users = response["members"]
                all_users.extend(users)

                if response.get("response_metadata", {}).get("next_cursor"):
                    cursor = response["response_metadata"]["next_cursor"]
                else:
                    break
            else:
                print(f"Error: {response['error']}")
                break

    except Exception as e:
        print(f"Exception: {e}")

    return all_users


def get_all_channels_paginated(client: WebClient):
    all_channels = []
    cursor = None

    try:
        while True:
            if cursor:
                response = client.conversations_list(
                    types="public_channel",
                    cursor=cursor,
                    limit=1000
                )
            else:
                response = client.conversations_list(
                    types="public_channel",
                    limit=1000
                )

            if response["ok"]:
                channels = response["channels"]
                all_channels.extend(channels)

                if response.get("response_metadata", {}).get("next_cursor"):
                    cursor = response["response_metadata"]["next_cursor"]
                else:
                    break
            else:
                print(f"Error: {response['error']}")
                break

    except Exception as e:
        print(f"Exception: {e}")

    return all_channels


def is_valid_date_fmt(date_string: str):
    """
    Check if the input string is a valid date in 'YYYY-MM-DD' format.
    """
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"{date_string} is not in YYYY-MM-DD format: {e}")


def validate_options(func) -> Any:
    """
    Decorator to validate the 'options' parameter if it exists:
    - Must be an iterable (but not a string)
    - Each element must be convertible to a string
    - Each converted string must have a length greater than 0
    If the function doesn't have an 'options' parameter, no checks will be performed
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        if 'options' not in bound_args.arguments:
            return func(*args, **kwargs)

        options = bound_args.arguments['options']

        if isinstance(options, str):
            raise TypeError(
                "'options' must be an iterable collection (like list or tuple) of elements, "
                f"not a single string. For example: ['{options}'] instead of '{options}'"
            )

        try:
            iter(options)
        except TypeError:
            raise TypeError(
                "'options' must be an iterable collection (like list, tuple, or generator). "
                f"Received {type(options).__name__} which is not iterable."
            )

        for index, element in enumerate(options):
            try:
                str_element = str(element)
            except Exception as e:
                raise TypeError(
                    f"Element at index {index} (value: {repr(element)}) cannot be converted to a string. "
                    "All options must be convertible to non-empty strings. "
                    f"Conversion failed with error: {str(e)}"
                )

            if len(str_element) == 0:
                raise ValueError(
                    f"Element at index {index} (value: {repr(element)}) converts to an empty string. "
                    "All options must convert to strings with at least one non-empty character."
                )

        return func(*args, **kwargs)

    return wrapper


def validate_initial_time(func):
    """
    Decorator to validate the 'initial_time' parameter if it exists:
    - Must be a string in hh:mm format (24-hour or 12-hour time)
    - Hours must be 00-23
    - Minutes must be 00-59
    """
    # Regular expression pattern for hh:mm format
    time_pattern = re.compile(r'^(\d{2}):(\d{2})$')

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        if 'initial_time' not in bound_args.arguments:
            return func(*args, **kwargs)

        initial_time = bound_args.arguments['initial_time']
        if initial_time is None:
            return func(*args, **kwargs)

        if not isinstance(initial_time, str):
            raise TypeError(
                f"'initial_time' must be a string in hh:mm format. "
                f"Received {type(initial_time).__name__} instead."
            )

        match = time_pattern.match(initial_time)
        if not match:
            raise ValueError(
                f"'initial_time' must be in hh:mm format (e.g., '09:30' or '14:45'). "
                f"Received '{initial_time}' which is invalid."
            )

        hours, minutes = map(int, match.groups())
        if hours < 0 or hours > 23:
            raise ValueError(
                f"Hours in 'initial_time' must be between 00 and 23. "
                f"Received '{initial_time}' with invalid hour {hours}."
            )

        if minutes < 0 or minutes > 59:
            raise ValueError(
                f"Minutes in 'initial_time' must be between 00 and 59. "
                f"Received '{initial_time}' with invalid minute {minutes}."
            )

        # All checks passed
        return func(*args, **kwargs)

    return wrapper


def validate_simple_https_url(func):
    """
    Decorator to validate 'url' parameter (if exists) meets two criteria:
    1. Must start with 'https://'
    2. Must have non-empty content after 'https://'
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        if 'url' not in bound_args.arguments:
            return func(*args, **kwargs)

        url = bound_args.arguments['url']

        if not isinstance(url, str):
            raise TypeError(f"'url' must be a string, got {type(url).__name__} instead")

        if not url.startswith('https://'):
            raise ValueError(f"'url' must start with 'https://', got '{url}' instead")

        content_after_protocol = url[len('https://'):]
        if not content_after_protocol.strip():
            raise ValueError(f"'url' must have content after 'https://', got '{url}'")

        return func(*args, **kwargs)

    return wrapper
