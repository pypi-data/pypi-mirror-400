"""
Protobuf to JSON decoder module.

This module provides functionality to decode protobuf binary data into
JSON-compatible Python dictionaries without requiring a schema definition.

Reference: protobuf_inspector/core.py and protobuf_inspector/types.py
"""

import io
import struct
from typing import Dict, List, Any, Optional, BinaryIO


# Wire type constants
WIRE_TYPE_VARINT = 0
WIRE_TYPE_FIXED64 = 1
WIRE_TYPE_LENGTH_DELIMITED = 2
WIRE_TYPE_START_GROUP = 3  # Deprecated
WIRE_TYPE_END_GROUP = 4  # Deprecated
WIRE_TYPE_FIXED32 = 5


def read_varint(file: BinaryIO) -> Optional[int]:
    """
    Read a varint from the file stream.

    Returns None on EOF.
    """
    result = 0
    pos = 0
    while True:
        b = file.read(1)
        if not len(b):
            if pos == 0:
                return None
            raise ValueError("Unexpected EOF while reading varint")
        b = b[0]
        result |= (b & 0x7F) << pos
        pos += 7
        if not (b & 0x80):
            return result


def read_identifier(file: BinaryIO) -> tuple:
    """
    Read a field identifier (field number + wire type) from the file stream.

    Returns (field_number, wire_type) or (None, None) on EOF.
    """
    id_value = read_varint(file)
    if id_value is None:
        return (None, None)
    return (id_value >> 3, id_value & 0x07)


def read_value(file: BinaryIO, wire_type: int) -> Any:
    """
    Read a value from the file stream based on the wire type.

    Returns the raw value according to wire type:
    - wire_type 0: int (varint)
    - wire_type 1: bytes (8 bytes)
    - wire_type 2: BytesIO (length-delimited)
    - wire_type 3: True (start group)
    - wire_type 4: False (end group)
    - wire_type 5: bytes (4 bytes)
    """
    if wire_type == WIRE_TYPE_VARINT:
        return read_varint(file)

    if wire_type == WIRE_TYPE_FIXED64:
        c = file.read(8)
        if len(c) != 8:
            raise ValueError("Unexpected EOF while reading fixed64")
        return c

    if wire_type == WIRE_TYPE_LENGTH_DELIMITED:
        length = read_varint(file)
        if length is None:
            raise ValueError("Unexpected EOF while reading length")
        c = file.read(length)
        if len(c) != length:
            raise ValueError("Unexpected EOF while reading length-delimited data")
        return io.BytesIO(c)

    if wire_type == WIRE_TYPE_START_GROUP:
        return True

    if wire_type == WIRE_TYPE_END_GROUP:
        return False

    if wire_type == WIRE_TYPE_FIXED32:
        c = file.read(4)
        if len(c) != 4:
            raise ValueError("Unexpected EOF while reading fixed32")
        return c

    raise ValueError(f"Unknown wire type {wire_type}")


def is_valid_utf8_string(data: bytes) -> bool:
    """
    Check if the data is a valid UTF-8 string that looks like text.
    """
    try:
        text = data.decode("utf-8")
        # Check if it looks like a reasonable string (not too many control chars)
        if not text:
            return False
        control_chars = sum(1 for c in text if ord(c) < 0x20 and c not in "\n\r\t")
        if len(text) > 0 and control_chars / len(text) > 0.1:
            return False
        return True
    except UnicodeDecodeError:
        return False


def _can_be_valid_message(data: bytes) -> bool:
    """
    Check if data could be a valid protobuf message structure.
    This is a structural check that validates the wire format without
    recursively decoding nested messages.

    Returns True if the data appears to be a valid message structure.
    """
    if not data or len(data) < 2:
        return False

    try:
        file = io.BytesIO(data)
        fields_found = 0

        while True:
            # Try to read identifier
            id_value = read_varint(file)
            if id_value is None:
                break

            field_number = id_value >> 3
            wire_type = id_value & 0x07

            # Validate field number (must be positive)
            # Proto field numbers range from 1 to 2^29-1 (536870911)
            if field_number <= 0 or field_number > 536870911:
                return False

            # Validate wire type (must be 0-5, excluding deprecated 3, 4)
            if wire_type not in (0, 1, 2, 5):
                # wire_type 3 and 4 are deprecated groups, skip them for validation
                if wire_type in (3, 4):
                    return False
                return False

            # Skip the value based on wire type
            if wire_type == WIRE_TYPE_VARINT:
                val = read_varint(file)
                if val is None:
                    return False
            elif wire_type == WIRE_TYPE_FIXED64:
                c = file.read(8)
                if len(c) != 8:
                    return False
            elif wire_type == WIRE_TYPE_LENGTH_DELIMITED:
                length = read_varint(file)
                if length is None:
                    return False
                # Reasonable length check
                if length > 100 * 1024 * 1024:  # 100MB max
                    return False
                c = file.read(length)
                if len(c) != length:
                    return False
            elif wire_type == WIRE_TYPE_FIXED32:
                c = file.read(4)
                if len(c) != 4:
                    return False

            fields_found += 1

        # Must have consumed all bytes and found at least one field
        remaining = file.read()
        return len(remaining) == 0 and fields_found > 0

    except Exception:
        return False


def _decode_varint_field(value: int) -> Dict[str, Any]:
    """
    Decode a varint value into a JSON-compatible dict.
    """
    result = {"wire_type": WIRE_TYPE_VARINT, "value": value}

    # Add signed interpretation if it would be negative
    if value >= (1 << 63):
        result["as_signed"] = value - (1 << 64)

    return result


def _decode_fixed64_field(data: bytes) -> Dict[str, Any]:
    """
    Decode a 64-bit fixed value into a JSON-compatible dict with multiple interpretations.
    """
    return {
        "wire_type": WIRE_TYPE_FIXED64,
        "as_fixed64": struct.unpack("<Q", data)[0],
        "as_sfixed64": struct.unpack("<q", data)[0],
        "as_double": struct.unpack("<d", data)[0],
    }


def _decode_fixed32_field(data: bytes) -> Dict[str, Any]:
    """
    Decode a 32-bit fixed value into a JSON-compatible dict with multiple interpretations.
    """
    return {
        "wire_type": WIRE_TYPE_FIXED32,
        "as_fixed32": struct.unpack("<I", data)[0],
        "as_sfixed32": struct.unpack("<i", data)[0],
        "as_float": struct.unpack("<f", data)[0],
    }


def _decode_length_delimited_field(file: BinaryIO) -> Dict[str, Any]:
    """
    Decode a length-delimited field.

    Strategy: try message first, then UTF-8 string, then bytes (hex).
    """
    data = file.read()

    if not data:
        return {"wire_type": WIRE_TYPE_LENGTH_DELIMITED, "type": "bytes", "value": ""}

    # Try to decode as message first (with strict validation)
    if _can_be_valid_message(data):
        try:
            message_result = _decode_message(io.BytesIO(data))
            if message_result:
                return {
                    "wire_type": WIRE_TYPE_LENGTH_DELIMITED,
                    "type": "message",
                    "value": message_result,
                }
        except Exception:
            pass

    # Try to decode as UTF-8 string
    if is_valid_utf8_string(data):
        return {
            "wire_type": WIRE_TYPE_LENGTH_DELIMITED,
            "type": "string",
            "value": data.decode("utf-8"),
        }

    # Fall back to bytes (hex)
    return {
        "wire_type": WIRE_TYPE_LENGTH_DELIMITED,
        "type": "bytes",
        "value": data.hex(),
    }


def _add_field_to_result(result: Dict, field_number: int, field_value: Dict) -> None:
    """
    Add a field to the result dict, handling repeated fields by converting to array.
    """
    key = str(field_number)

    if key not in result:
        result[key] = field_value
    else:
        # Convert to array if not already
        existing = result[key]
        if isinstance(existing, list):
            existing.append(field_value)
        else:
            result[key] = [existing, field_value]


def _decode_message(file: BinaryIO, end_group: Optional[List] = None) -> Dict[str, Any]:
    """
    Decode a protobuf message from the file stream.

    Args:
        file: Binary file stream to read from
        end_group: Optional list to store end group field number (for group handling)

    Returns:
        Dict with field numbers as keys and decoded values
    """
    result = {}

    while True:
        field_number, wire_type = read_identifier(file)

        if field_number is None:
            break

        value = read_value(file, wire_type)

        # Handle end group
        if wire_type == WIRE_TYPE_END_GROUP:
            if end_group is not None:
                end_group.append(field_number)
            break

        # Handle start group (deprecated but still possible)
        if wire_type == WIRE_TYPE_START_GROUP:
            end = []
            nested = _decode_message(file, end)
            field_value = {
                "wire_type": WIRE_TYPE_START_GROUP,
                "type": "group",
                "value": nested,
            }
            _add_field_to_result(result, field_number, field_value)
            continue

        # Decode based on wire type
        if wire_type == WIRE_TYPE_VARINT:
            field_value = _decode_varint_field(value)
        elif wire_type == WIRE_TYPE_FIXED64:
            field_value = _decode_fixed64_field(value)
        elif wire_type == WIRE_TYPE_LENGTH_DELIMITED:
            field_value = _decode_length_delimited_field(value)
        elif wire_type == WIRE_TYPE_FIXED32:
            field_value = _decode_fixed32_field(value)
        else:
            raise ValueError(f"Unknown wire type {wire_type}")

        _add_field_to_result(result, field_number, field_value)

    return result


def decode_protobuf(data: bytes) -> Dict[str, Any]:
    """
    Decode protobuf binary data into a JSON-compatible dictionary.

    Args:
        data: Protobuf serialized bytes

    Returns:
        Dict with field numbers as string keys and decoded values.

        For wire_type 0 (varint):
            {"wire_type": 0, "value": <int>}

        For wire_type 1 (fixed64):
            {"wire_type": 1, "as_fixed64": <uint64>, "as_sfixed64": <int64>, "as_double": <float>}

        For wire_type 2 (length_delimited):
            {"wire_type": 2, "type": "string"|"bytes"|"message", "value": <decoded_value>}

        For wire_type 5 (fixed32):
            {"wire_type": 5, "as_fixed32": <uint32>, "as_sfixed32": <int32>, "as_float": <float>}

        Repeated fields are automatically merged into arrays.

    Example:
        >>> data = b'\\x08\\x96\\x01'  # field 1, varint 150
        >>> decode_protobuf(data)
        {'1': {'wire_type': 0, 'value': 150}}
    """
    if not data:
        return {}

    return _decode_message(io.BytesIO(data))


def decode_protobuf_to_json(data: bytes, indent: Optional[int] = 2) -> str:
    """
    Decode protobuf binary data and return as JSON string.

    Args:
        data: Protobuf serialized bytes
        indent: JSON indentation level (None for compact output)

    Returns:
        JSON string representation of the decoded protobuf
    """
    import json

    result = decode_protobuf(data)
    return json.dumps(result, indent=indent, ensure_ascii=False)
