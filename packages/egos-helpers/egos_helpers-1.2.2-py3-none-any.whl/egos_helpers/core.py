#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Helper functions """

import logging
import os
import re
import unicodedata
import secrets
import string
from typing import Any, Dict, Union
from .constants import NAME

log = logging.getLogger(NAME)

def gather_environ(keys: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Return a dict of environment variables correlating to the keys dict.
    The environment variables have to be set in **ALL_UPPER_CASE**.

    Supported settings for each key:
    * `type`: one of `string`, `int`, `list`, `boolean`, `enum` or `filter`
    * `default`: if omitted, it will be set to `None`
    * `hidden`: no `log.info` will be generated if unset or a default value
                is used
    * `deprecated`: boolean flag to issue a `log.warning` if set
    * `replaced_by`: string referencing the name of another key, that should
                     take the value of this key if `deprecated` is `True`
    * `redact`: boolean flag to have the value of this key replaced with a
                redacted string in the `log.info` message

    Every environment variable found will be echoed on `log.info()` (except those
    with `redact: True`).

    `boolean` keys will use :py:func:`strtobool` to convert a string to boolean.

    The env separator for the type `list` is `<space>` and the key/value separator
    for the type `filter` (which is stored as a dictionary) is the first `=` sign.
    So a `filter` with the value `a=b=c=d` will be stored as `{'a': 'b=c=d'}`.

    The keys must be in the following format:

        keys = {
            'key_one': {
                'default': ['one', 2],
                'type': "list",
            },
            'key_two':{
                'hidden': True,
                'default': False,
                'type': "boolean",
            },
            'key_three': {
                'default': {},
                'type': "filter",
            },
            'key_four': {
                'default': None,
                'redact': True,
                'type': 'string',
            },
            'key_five': {
                'default': 12,
                'type': 'int',
            },
            'key_six': {
                'default': 'INFO',
                'type': 'enum',
                'values': [
                    'DEBUG',
                    'INFO',
                    'WARNING',
                    'ERROR'
                ],
            },
            'key_seven': {
                'default': '12',
                'deprecated': True,
                'replaced_by': 'key_five',
                'type': 'int',
            }
        }

    Based on the found environment variables, this will return a `Dict[str, Any]`.

        return {
            'key_one': 'one',
            'key_two': False,
            'key_three': {
                'foo': 'bar'
            },
            'key_four': 'super_secret_string',
            'key_five': 33,
            'key_six': 'WARNING'
        }

    :param keys: The environ keys to use
    :type keys: Dict[str,Dict[str,Any]]
    :returns: A dict of the found environ values
    :rtype: Dict[str,Any]
    """

    if not isinstance(keys, dict):
        raise TypeError("Keys must be a dictionary")

    environs = {}

    # Check the environment variables
    for key, key_attributes in keys.items():
        if not isinstance(key_attributes, dict):
            log.warning("Invalid configuration for key '%d'. Skipping.", key)
            continue

        # Get environment variable value (supports file-based secrets)
        try:
            env_value = _get_environ_value(key)
        except (ValueError, RuntimeError) as e:
            log.warning("Error retrieving %d: %d", key.upper(), e)
            continue

        # Process the value if found
        if env_value is not None:
            try:
                processed_value = _process_environ_val(key_attributes, env_value)
                environs[key] = processed_value

                # Log the value (respecting hidden and redact flags)
                if not key_attributes.get('hidden', False):
                    log.info(
                        redact(
                            message=f'{key.upper()} is set to `{processed_value}`.',
                            param=processed_value,
                            replace=key_attributes.get('redact', False)
                        )
                    )
            except ValueError as e:
                log.warning('Error processing %d: %d. Default value will be used.', key.upper(), e)
                continue
    environs = _handle_deprecations(environs=environs, keys=keys)
    environs = _fill_missing_environs(environs=environs, keys=keys)
    return environs

def _process_environ_val(key_attributes: dict, key_value: str) -> Any:
    """
    Process and convert environment variable value based on its configured type.

    Takes a raw environment variable value (typically a string) and converts it
    to the appropriate Python type based on the type specification in key_attributes.

    Supported types:
    - 'string': Returns value as-is (default)
    - 'list': Splits value on spaces into a list
    - 'filter': Splits on first '=' to create a single-key dictionary
    - 'int': Converts to integer
    - 'boolean': Converts to boolean using strtobool logic
    - 'enum': Validates against allowed values list

    Args:
        key_attributes: Configuration dictionary containing at least:
            - type: The target type for conversion ('string', 'list', 'filter',
                   'int', 'boolean', 'enum')
            - values: Required for 'enum' type - list of allowed values
        key_value: A string with the raw environment variable value to process.

    Returns:
        The processed value in the appropriate Python type:
        - str: for 'string' type
        - list: for 'list' type (space-separated values)
        - dict: for 'filter' type (single key-value pair)
        - int: for 'int' type
        - bool: for 'boolean' type
        - str: for 'enum' type (validated against allowed values)

    Raises:
        ValueError: If the value cannot be converted to the specified type or
                   if an 'enum' value is not in the allowed values list.
        KeyError: If 'enum' type is specified but 'values' key is missing.

    Examples:
        >>> # String type (default)
        >>> _process_environ_val({'type': 'string'}, 'hello')
        'hello'

        >>> # List type
        >>> _process_environ_val({'type': 'list'}, 'a b c')
        ['a', 'b', 'c']

        >>> # Filter type
        >>> _process_environ_val({'type': 'filter'}, 'env=production')
        {'env': 'production'}

        >>> # Integer type
        >>> _process_environ_val({'type': 'int'}, '42')
        42

        >>> # Boolean type
        >>> _process_environ_val({'type': 'boolean'}, 'true')
        True

        >>> # Enum type
        >>> _process_environ_val({'type': 'enum', 'values': ['dev', 'prod']}, 'dev')
        'dev'
    """

    key_type = key_attributes.get('type', 'string')

    if key_type == 'list':
        return key_value.split(' ')

    if key_type == 'filter':
        filters = key_value.split('=', 1)
        try:
            return {filters[0]: filters[1]}
        except IndexError as e:
            raise ValueError(f"Invalid filter format `{key_value}`. Format must be `key=value`.") from e

    if key_type == 'int':
        try:
            return int(key_value)
        except ValueError as e:
            raise ValueError(f"Invalid integer format `{key_value}`.") from e

    if key_type == 'boolean':
        try:
            return bool(strtobool(key_value))
        except ValueError as e:
            raise ValueError(f"Invalid boolean format `{key_value}`.") from e

    if key_type == 'enum':
        if not key_value in key_attributes['values']:
            raise ValueError(f"Value `{key_value}` is not allowed.")
        return key_value

    # Return for all non-checked values
    return key_value

def _get_environ_value(key: str) -> str|None:
    """
    Retrieves environment variable value with support for file-based secrets.

    This function implements a common pattern for handling secrets in containerized
    environments where sensitive values can be provided either directly as environment
    variables or as file paths containing the actual values.

    Priority order:
    1. Checks for {KEY}_FILE environment variable first
    2. If found, reads the file contents and returns the stripped value
    3. If not found, falls back to the direct {KEY} environment variable
    4. Returns None if neither is found

    Args:
        key: The base name of the environment variable to check.
             Will be converted to uppercase for lookup. Must be a non-empty,
             non-whitespace string.

    Returns:
        The environment variable value, file contents (stripped), or None if not found.

    Raises:
        ValueError: If key is not a string, is empty, or contains only whitespace.
        RuntimeError: If both {KEY} and {KEY}_FILE are defined simultaneously,
                     or if the file specified by {KEY}_FILE cannot be read.

    Example:
        >>> # With direct env var: MYAPP_TOKEN=secret123
        >>> _get_environ_value("myapp_token")
        'secret123'

        >>> # With file-based env var: MYAPP_TOKEN_FILE=/run/secrets/token
        >>> _get_environ_value("myapp_token")
        'contents_of_token_file'
    """

    if not key or not isinstance(key, str):
        raise ValueError("Key must be a non-empty string")

    if not key.strip():
        raise ValueError("Key cannot be whitespace only")

    key_upper = key.upper()
    file_key = f"{key_upper}_FILE"

    if file_key in os.environ and key_upper in os.environ:
        raise RuntimeError(f'Both "{key_upper}" and "{file_key}" are defined. Choose one.')

    if file_key in os.environ:
        file_path = os.environ[file_key]
        try:
            with open(file_path, "r", encoding='utf-8') as env_file:
                return env_file.read().strip()
        except (FileNotFoundError, PermissionError, OSError) as e:
            raise RuntimeError(f'Failed to read file "{file_path}" for {file_key}: {e}') from e

    return os.environ.get(key_upper)

def _fill_missing_environs(
    environs: Dict[str, Any],
    keys: Dict
) -> Dict[str, Any]:
    """
    Fills out the missing environment variables with the values stored in the keys

    :param environs: The already gathered environment variables
    :type environs: Dict[str,Any]
    :param keys: The environ keys to use
    :type keys: Dict[str, Dict[str,Any]]
    :returns:
        A dict of found environ values. For the unset environment variables,
        it returns the default set in the `keys`
    :rtype: Dict[str,Any]
    """
    for key, key_attributes in keys.items():
        if not key in environs and not key_attributes.get('deprecated', False) :
            display = key_attributes.get('default')

            if key_attributes['type'] == 'list':
                display = ' '.join(display)

            if key_attributes['type'] == 'filter':
                display = '='.join(display)

            if not key_attributes.get('hidden', False):
                log.info(
                    redact(
                        message=f'{key.upper()} is set to `{display}`.',
                        param=display,
                        replace=key_attributes.get('redact', False)
                    )
                )
            environs[key] = key_attributes.get('default')
    return environs

def _handle_deprecations(
    environs: Dict[str, Any],
    keys: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Handles deprecated environment variables

    :param environs: The already gathered environment variables
    :type environs: Dict[str,Any]
    :param keys: The environ keys to use
    :type keys: Dict[str, Dict[str,Any]]
    :returns: A dict environ values, after deprecation processing
    :rtype: Dict[str,Any]
    """
    for key, key_attributes in keys.items():
        if key in environs and key_attributes.get('deprecated', False) :
            message = f"{key.upper()} is deprecated and will be removed in a next version."
            if key_attributes.get('replaced_by'):
                message += f" Use {key_attributes['replaced_by'].upper()} instead."
                log.warning(message)
                if key_attributes['replaced_by'] in environs:
                    log.warning("%d and %d are both set. Dropping %d.",
                        key.upper(),
                        key_attributes['replaced_by'].upper(),
                        key.upper()
                    )
                    del environs[key]
                else:
                    environs[key_attributes['replaced_by']] = environs[key]
                    del environs[key]
            else:
                log.warning(message)

    return environs

def short_msg(msg: str, chars: int = 150) -> str:
    """
    Truncates the message to `chars` characters and adds two dots at the end.

    :param msg: The string to truncate
    :type msg: str
    :param chars: The max number of characters before adding `..` (default: 150)
    :type chars: int, optional
    :return: The truncated `msg`. It will return back the `msg` if the length is < `chars`
    :rtype: str
    """
    return (str(msg)[:chars] + '..') if len(str(msg)) > chars else str(msg)

def strtobool(value: str) -> bool:
    """
    Converts a string to a boolean

    :param value: The string to check if it represents true or false
    :type value: str
    :raises ValueError: When the string cannot be matched to a boolean
    :return: The corresponding boolean value
    :rtype: bool
    """
    str_to_bool_map = {
        'y': True,
        'yes': True,
        't': True,
        'true': True,
        'on': True,
        '1': True,
        'n': False,
        'no': False,
        'f': False,
        'false': False,
        'off': False,
        '0': False
    }

    try:
        return str_to_bool_map[str(value).lower()]
    except KeyError as exc:
        raise ValueError(f'"{value}" is not a valid bool value') from exc

def redact(
    message: str,
    param: Union[str, Any],
    replace: bool = False,
    replace_value: str = 'xxxREDACTEDxxx'
) -> str:
    """
    Replaces in `message` the `param` string with `replace_value`

    :param message: The string to parse
    :param param: The substring to be replaced
    :param replace: Whether the `param` should be replaced
    :param replace_value: The value to replace `param` with
    :return: The modified string
    """
    if replace:
        param_str = str(param)
        return message.replace(param_str, replace_value)
    return message

def key_to_title(key: str) -> str:
    """
    Converts a string key in form 'a_is_b' to a title in form 'A Is B'

    :param key: The source string `a_is_b`
    :return: The converted string `A Is B`
    """
    return ' '.join(word.capitalize() for word in key.split('_'))

def _random_slug(length: int) -> str:
    """Generate a random URL-safe slug of the given length."""
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def slugify(value: str, max_length: int = 20) -> str:
    """Convert a string to a URL-safe slug with a maximum length.

    - Normalizes Unicode (NFKD) and strips accents.
    - Lowercases.
    - Replaces non-alphanumeric characters with hyphens.
    - Collapses multiple hyphens and trims leading/trailing hyphens.
    - Truncates to `max_length` characters, default 20.
    - If the result is empty, returns a random slug of the same max_length.
    """
    # Normalize and remove accents
    normalized = unicodedata.normalize("NFKD", value)
    ascii_str = normalized.encode("ascii", "ignore").decode("ascii")

    # Lowercase and replace non-alphanumeric with hyphen
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_str.lower())

    # Strip extra hyphens
    slug = slug.strip("-")

    # Enforce max length
    slug = slug[:max_length].rstrip("-")

    # Fallback: random slug if everything was stripped
    return slug or _random_slug(max_length)
