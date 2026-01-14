"""
Protobuf to JSON conversion module.

This module provides functionality to decode protobuf binary data into
JSON-compatible Python dictionaries without requiring a schema definition.

Usage:
    from proto2json import decode_protobuf, decode_protobuf_to_json
    
    # Decode to dict
    result = decode_protobuf(protobuf_bytes)
    
    # Decode to JSON string
    json_str = decode_protobuf_to_json(protobuf_bytes)
"""

from .decoder import (
    decode_protobuf,
    decode_protobuf_to_json,
    # Wire type constants
    WIRE_TYPE_VARINT,
    WIRE_TYPE_FIXED64,
    WIRE_TYPE_LENGTH_DELIMITED,
    WIRE_TYPE_FIXED32,
)

__all__ = [
    'decode_protobuf',
    'decode_protobuf_to_json',
    'WIRE_TYPE_VARINT',
    'WIRE_TYPE_FIXED64',
    'WIRE_TYPE_LENGTH_DELIMITED',
    'WIRE_TYPE_FIXED32',
]


__version__ = '1.0.0'
