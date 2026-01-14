import sys
import logging
from google.protobuf import json_format
from google.protobuf.message import Message


logger = logging.getLogger(__name__)

# ###############################################################################

if sys.version_info >= (3, 0):
    def is_string(x):
        return isinstance(x, str)
else:
    def is_string(x):
        return isinstance(x, basestring)  # noqa: F821


# ###############################################################################

class ValidationError(Exception):
    """
    Raise this exception when the confirguration required in the experiment protobuf
    is not valid.
    """


# ###############################################################################


def parse_protobuf_from_json_or_binary(protobuf_class, data):
    try:
        return json_format.Parse(data, protobuf_class())
    except (json_format.ParseError, UnicodeDecodeError) as e:
        logger.info("Failed to load the protobuf from JSON (Got: {}). Trying to load it as a binary.".format(str(e)))
        msg = protobuf_class()
        msg.ParseFromString(data)
        return msg


def convert_protobuf_to_json(message):
    return json_format.MessageToDict(message, including_default_value_fields=True, preserving_proto_field_name=True)


def convert_to_dict(value):
    """Convert a protobuf message into a dict"""
    if isinstance(value, Message):
        return convert_protobuf_to_json(value)
    elif isinstance(value, dict):
        return value  # nothing to do
