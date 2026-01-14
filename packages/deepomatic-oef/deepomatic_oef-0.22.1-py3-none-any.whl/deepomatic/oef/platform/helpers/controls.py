from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum
import functools
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.message import Message
from typing import Any, List, Callable

from deepomatic.oef.utils.common import convert_protobuf_to_json
from deepomatic.oef.configs.utils import dict_inject
from deepomatic.oef.utils.class_helpers import load_proto_class_from_protobuf_descriptor

from .common import CHECK_TYPE, CHECK_LIST, CHECK_DICT
from .tags import Tags, Backend


###############################################################################

class ControlType(Enum):
    """
    Form control types
    """
    TITLE = 'title'
    TEXT = 'text'
    SELECT = 'select'
    INPUT = 'input'
    TOGGLE = 'toggle'
    FORM = 'form'
    LIST = 'list'


###############################################################################

class DisplayCondition:
    """
    Used to decide whether or not a control should be displayed.
    A DisplayCondition works by looking at the value of one tag.
    If this value is in a pre-determined set, then the condition
    is true. By combining multiple conditions in a list, one can
    define complex conditions.
    """

    def __init__(self, tag, allowed_values):
        """
        Create a DisplayCondition.

        Args:
            tag (str): The name of the tag to watch.
            allowed_values (list of str): If the tag takes one of this value then the condition
                is satisfied.
        """
        self._tag = CHECK_TYPE(tag, str)
        self._allowed_values = CHECK_TYPE(allowed_values, list, allow_none=True)

    def json(self):
        """
        Convert the object into a Python dict which is JSON-serializable.
        """
        return {
            'tag': self._tag,
            'allowed_values': self._allowed_values
        }

    def is_visible(self, tags):
        """
        Return true if control is visible

        Args:
            tags (dict): dict of tags (str) to their values (str)

        Return True if tag belongs to allowed values.
        """
        return tags[self._tag] in self._allowed_values


###############################################################################

def protobuf_iterate(protobuf, keys, check_last_one=True):
    keys = keys.split('.')

    if keys[0] in ['@meta_arch', '@backbone']:
        meta_arch_type = protobuf.trainer.WhichOneof('model_type')
        assert meta_arch_type != 'custom_model', 'Model parameters shortcuts are not available for custom models'
        trainer = protobuf.trainer
        if keys[0] == '@backbone':
            protobuf = getattr(trainer, meta_arch_type)
            key = 'backbone'
        else:
            protobuf = trainer
            key = meta_arch_type

        if len(keys) == 1:
            return protobuf, key
        else:
            # We remove the first key as it has been processed
            keys.pop(0)
            protobuf = getattr(protobuf, key)

    last_i = len(keys) - 1
    for i, key in enumerate(keys):
        if i < last_i or check_last_one:
            assert hasattr(protobuf, key), "Expecting finding the attribute '{}' but could not find one in protobuf message '{}'".format(key, protobuf.DESCRIPTOR.name)
        if i == last_i:
            return protobuf, key
        else:
            protobuf = getattr(protobuf, key)


def get_default_value_for_field(field_descriptor):
    """
    Given a protobuf field type, return its default value
    Args:
        field_descriptor (google.protobuf.descriptor.FieldDescriptor)
    Return:
        A default value
    """
    if field_descriptor.label == FieldDescriptor.LABEL_REPEATED:
        return list()
    if field_descriptor.message_type is not None:
        return dict()
    else:
        # Scalars
        if field_descriptor.cpp_type in [field_descriptor.CPPTYPE_DOUBLE, field_descriptor.CPPTYPE_FLOAT, field_descriptor.CPPTYPE_INT32, field_descriptor.CPPTYPE_INT64, field_descriptor.CPPTYPE_UINT32, field_descriptor.CPPTYPE_UINT64]:
            return 0
        elif field_descriptor.cpp_type in [field_descriptor.CPPTYPE_BOOL]:
            return False
        elif field_descriptor.cpp_type in [field_descriptor.CPPTYPE_STRING]:
            return ''
        else:
            raise Exception(f"Cannot handle type message type {field_descriptor.cpp_type}")


def build_message_from_payload(message_class, data):
    """
    Fills a protobuf message with the JSON data payload. When the message
    contains oneof values, not all data field may be consumed. Indeed, the
    front-end accumulates values for each oneof field. For example, if the
    user changes the 'Optimizer' select from 'Momentum Optimize' to
    'RMS Prop Optimizer', we will accumulate some values for both oneof fields,
    like both:
        - "trainer.optimizer.momentum_optimizer.momentum_optimizer_value": 0.9
        - "trainer.optimizer.rms_prop_optimizer.momentum_optimizer_value": 0.9
    In such case, the data also contains the name of the field to consider, e.g:
        "trainer.optimizer.optimizer": "rms_prop_optimizer"
    The last part of the key ('optimizer' in the example) is the name of the
    oneof field.

    Args:
        message_class: The class of the protobuf to build
        data: a dict of value, potentially containing more values as decribed
            above.

    Return:
        The build protobuf message.
    """
    # We clear irrelevant fields
    for oneof_name, oneof in message_class.DESCRIPTOR.oneofs_by_name.items():
        if oneof_name in data:
            which_oneof = data.pop(oneof_name)
            # Add new (key,value) to data dict, key (which_oneof) being the value that we got from data.pop(oneof_name), and the value is the default value related to this which_oneof.
            # This field will be later with the necessary parameters
            data[which_oneof] = get_default_value_for_field(message_class.DESCRIPTOR.fields_by_name[which_oneof])
        # We clear all non activated fields from data:
        for field in oneof.fields:
            field = field.name
            if field == which_oneof:
                # We do not clear the activated field
                continue
            prefix_to_remove = field + '.'
            for key in list(data.keys()):
                if key.startswith(prefix_to_remove):
                    data.pop(key)

    # We collect subkeys
    subkeys = defaultdict(dict)
    for key in list(data.keys()):
        parts = key.split('.')
        if len(parts) > 1:
            value = data.pop(key)
            field = parts[0]
            subkey = '.'.join(parts[1:])
            subkeys[field][subkey] = value

    # We build the sub messages
    for key, fields in subkeys.items():
        field_descriptor = message_class.DESCRIPTOR.fields_by_name[key]
        submessage_class = load_proto_class_from_protobuf_descriptor(field_descriptor.message_type)
        data[key] = build_message_from_payload(submessage_class, fields)

    return message_class(**data)


def simple_value_parser(value, key):
    """
    Create a nested dictionnary removing prefix of keys starting with @

    Args:
        value (string): value in the fields of the payload that we get from frontend
        key (string): key in the format of foo.coucou

    Returns:
        dictionnary : dictionnary injected nicely

    Example:
        key = "@backbone.input.image_resizer.image_resizer_oneof"
        value = "fixed_shape_resizer"

        return {'input': {'image_resizer': {'image_resizer_oneof': 'fixed_shape_resizer'}}}
    """
    if key.startswith('@'):
        # we use the magic behavior of the experiment builder to locate the right parameter recursively
        key = ".".join(key.split(".")[1:])
    return dict_inject(dict(), {key: value})


def flat_dictionnary_parser(value, key):
    """transform a key and value from payload to a dictionnary that can be used as kwargs for experiment builder

    Args:
        value (str): the content of the payload field
        key (str): key of the payload (see example)

    Returns:
        nicely formatted sub_payload
        example
            key : 'trainer.optimizer.optimizer'
            value : 'nadam_optimizer'

            result : {
                'trainer': {
                    'optimizer': {'nadam_optimizer': {}}
                }
            }

    """
    if key.startswith('@'):
        # we use the magic behavior of the experiment builder to locate the right parameter recursively
        key = ".".join(key.split(".")[1:])
    transformed_key = ".".join(key.split(".")[:-1] + [value])
    return dict_inject(dict(), {transformed_key: {}})


###############################################################################

class GetDefaultValueInterface(ABC):

    @abstractmethod
    def __call__(self, model_key, experiment, backend: Backend):
        """
        Return a default value for the specified model.

        Args:
            model_key: The model key as in model_list.py
            experiment: a Experiment protobuf
            backend: An instance of Backend

        Return:
            The default value.
        """


class GetProtobufValue(GetDefaultValueInterface):
    """
    A helper that represent a callable used to fetch the default value in the ModelArguments instance.
    """

    def __init__(self, value_key):
        """
        Args:
            value_key: A dot-separated path to the value of interest as stored in model.default_args.
                       For exemple: 'trainer.initial_learning_rate'
        """
        self._value_key = value_key

    def __call__(self, model_key, experiment, backend):
        """See GetDefaultValueInterface"""
        protobuf, last_key = protobuf_iterate(experiment, self._value_key)
        value = getattr(protobuf, last_key)
        field = protobuf.DESCRIPTOR.fields_by_name[last_key]
        if field.type == FieldDescriptor.TYPE_FLOAT:
            # Float protobuf fields will generate rounding error when converted back to double.
            # For example storing 0.9 in a float protobuf and reading it in Python would return
            # the 64 bits value 0.8999999761581421.
            # The hack below allow to display the value back with the proper number of decimals
            # to get a proper rounding and parse it in 64 bits to get back the initial value.
            value = float("{:f}".format(value))
        elif field.message_type is not None:
            if field.label == FieldDescriptor.LABEL_REPEATED:
                value = [self.protobuf_to_json_payload(v) for v in value]
            else:
                value = self.protobuf_to_json_payload(value)
        return value

    def protobuf_to_json_payload(self, protobuf):
        payload = convert_protobuf_to_json(protobuf)
        for oneof in protobuf.DESCRIPTOR.oneofs_by_name:
            assert oneof not in payload
            payload[oneof] = protobuf.WhichOneof(oneof)
        return payload


class GetProtobufOneof(GetDefaultValueInterface):
    """
    A helper that represent a callable used to fetch the default oneof field in the ModelArguments instance.
    """

    def __init__(self, oneof_key):
        """
        Args:
            oneof_key: A dot-separated path to the value of interest as stored in model.default_args.
                       For exemple: 'trainer.initial_learning_rate'
        """
        self._oneof_key = oneof_key

    def __call__(self, model_key, experiment, backend):
        """See GetDefaultValueInterface"""
        protobuf, last_key = protobuf_iterate(experiment, self._oneof_key, check_last_one=False)
        return protobuf.WhichOneof(last_key)


class ConstantDefaultValue:
    """
    A helper that return a constant value when called
    """

    def __init__(self, default_value):
        """
        Args:
            default_value: The value to return
        """
        self._default_value = default_value

    def __call__(self, model_key, experiment, backend):
        """See GetDefaultValueInterface"""
        return self._default_value


###############################################################################

class Control:

    def __init__(self,
                 property_name: str,
                 parser_function: Callable[[Message, Any], None],
                 message: str,
                 control_type: ControlType,
                 default_value: Any,
                 check_control_default_fn: Callable[[], Any],
                 display_ifs: List[DisplayCondition] = None):
        """
        Create a Control.

        Args:
            property_name (str): name attribute of the control in the front-end. The value of interest will be stored
                           in the JSON payload posted to the training API under this key.
            parser_function (callable): a function to parse the form post request: will be called with two arguments: (xp_protobuf, value).
                                           This function is expected to modify the protobuf inplace.
            message (str): a message to display in the front-end. Corresponds to the label of the control.
            control_type (ControlType): an instance of ControlType
            default_value (mixed): the default value for this control. It is either:
                - a callable accepting two arguments `model_key` (a string) and `model` (a ModelArguments instance).
                  This callable must return the default value for the given model.
                - a string: `GetProtobufValue` will be used to fetch this value in the model. If the string is empty,
                            `GetProtobufValue` will be called with the `property_name`.
                - constant: `check_control_default_fn` will be used to check the constant type
            check_control_default_fn: A function without argument that will check the constant in default_value and return the real constant to use.
            display_ifs (list): A list of DisplayCondition

        Return:
            The Control object.
        """
        # Sanity checks
        self._message = CHECK_TYPE(message, str, allow_none=True)
        self._property_name = CHECK_TYPE(property_name, str, allow_none=True)
        if parser_function is not None:
            assert callable(parser_function)
        self._parser_function = parser_function
        self._control_type = CHECK_TYPE(control_type, ControlType)
        self._display_ifs = CHECK_LIST(display_ifs, DisplayCondition)
        self._tags = None
        self._value_to_tag_map = None
        self._control_parameters = {}

        if default_value == GetProtobufValue:
            self._default_value_fn = GetProtobufValue(self._property_name)
        elif default_value == GetProtobufOneof:
            self._default_value_fn = GetProtobufOneof(self._property_name)
        elif default_value is None or callable(default_value):
            self._default_value_fn = default_value
        else:
            default_value = check_control_default_fn()
            self._control_parameters['default_value'] = default_value
            self._default_value_fn = ConstantDefaultValue(default_value)

    def json(self):
        """
        Convert the control into a Python dict which is JSON-serializable.
        """
        as_json = {
            'message': self._message,
            'type': self._control_type.value,
            'property': self._property_name,
            'display_if': [d.json() for d in self._display_ifs],
            'tags': self._tags,
            'control_parameters': self._control_parameters,
            'value_to_tag_map': self._value_to_tag_map,
        }
        return as_json

    def default_value(self, model_key, model, backend):
        """
        Return the control default value for this model.

        Args:
            model_key: The model key as in model_list.py
            model: a ModelArguments instance
            backend: An instance of Backend
        """
        if self._default_value_fn is None:
            return None
        return self._default_value_fn(model_key, model, backend)

    @property
    def property_name(self):
        """Return the property name"""
        return self._property_name

    @property
    def parser_function(self):
        return self._parser_function

    @property
    def value_to_tag_map(self):
        """
        Return the value_to_tag_map for this control. This is a dict
        representing a mapping from the possible values to the tag values.

        For example, the control declares a tag named 'backend', the returned value will be:

        {
            "image_classification.pretraining_natural_rgb.sigmoid.efficientnet_b0": {
                "backend": "tensorflow"
            },
            ... // as many keys as SelectOption in the control
            "image_detection.pretraining_natural_rgb.yolo_v3.darknet_53": {
                "backend": "darkenet"
            }
            // an additional tag named `model` will be declared by default, its
            // value will be the value of the `model` property.
        }
        """
        return self._value_to_tag_map

    def add_display_ifs(self, display_ifs):
        """
        Args:
            display_ifs (list): A list of DisplayCondition
        """
        self._display_ifs += display_ifs

    def is_visible(self, tags):
        """
        Return true if control is visible

        Args:
            tags (dict): dict of tags (str) to their values (str)

        Return:
            visible: True if control is visible
        """
        visible = True
        for condition in self._display_ifs:
            visible = visible and condition.is_visible(tags)
        return visible


###############################################################################

class Title(Control):
    """
    Use this class to display a title in bold.
    """

    def __init__(self, message, display_ifs=None):
        """
        Args:
            message (string): The title of the section
            display_ifs (list): see Control

        Return:
            The Control object.
        """
        super().__init__(None, None, message, ControlType.TITLE, None, None, display_ifs=display_ifs)


###############################################################################

class Text(Control):
    """
    Use this class to display a text.
    """

    def __init__(self, message, display_ifs=None):
        """
        Args:
            message (string): The title of the section
            display_ifs (list): see Control

        Return:
            The Control object.
        """
        super().__init__(None, None, message, ControlType.TEXT, None, None, display_ifs=display_ifs)


###############################################################################

class SelectControl(Control):
    """A helper class to define a SELECT."""

    def __init__(self, property_name, message, values, tags=None, display_ifs=None, default_value=GetProtobufOneof, property_is_a_oneof=True):
        """
        Creates a SELECT. See Control for a description of other arguments.

        Args:
            property_name: see Control
            message: see Control
            values (list): a list of SelectOption.
            tags (dict): a dict mapping values to instances of type Tags
            display_ifs (list): see Control
            default_value: see Control
            property_is_a_oneof (bool): True if the control is a oneof
        """
        def check_control_default_fn():
            # if the default value is a constant, it must be an index of one of the options
            CHECK_TYPE(default_value, int, exclude_types=bool)
            assert default_value < len(values)
            return values[default_value].value

        # Check that property_name points to a protobuf value
        if isinstance(self, ModelControl):
            parser_function = None
        else:
            if property_is_a_oneof:
                parser_function = functools.partial(flat_dictionnary_parser, key=property_name)
            else:
                parser_function = functools.partial(simple_value_parser, key=property_name)

        super().__init__(
            property_name,
            parser_function,
            message,
            ControlType.SELECT,
            default_value,
            check_control_default_fn,
            display_ifs
        )

        # Convert values into JSON
        self._control_parameters = {
            'values': [v.json() for v in values],
        }

        # Set tags
        self._tags = [self._property_name]
        self._value_to_tag_map = {}
        self._accumulate_values_and_tags_(values, tags)

    def _accumulate_values_and_tags_(self, values, tags):
        """
        Used by the ModelControl to accumulate all the possible values
        across possible view type. There is no possibility of interference
        between views because the model keys differe.

        Args: see __init__
        """
        # Sanity check
        CHECK_LIST(values, SelectOption)
        if tags is not None:
            CHECK_DICT(tags, Tags)
            assert tags.keys() == set([v.value for v in values])
            additional_tags = None
            for t in tags.values():
                if additional_tags is None:
                    additional_tags = t.tags.keys()
                else:
                    assert additional_tags == t.tags.keys()
            self._tags += list(additional_tags)
            self._value_to_tag_map.update({key: t.tags for key, t in tags.items()})
        else:
            self._value_to_tag_map.update({v.value: {} for v in values})


class ModelControl(SelectControl):
    """A special control class for model selection."""

    def __init__(self, property_name, message):
        super().__init__(
            property_name,
            message,
            [],  # no values, they will be set thanks to accumulate_values_and_tags
            # No default value for this one: the form sets its value at intialization
            default_value=None)
        self._control_parameters_per_view = {}

    def set_values_and_tags(self, view_type, values, tags):
        self._accumulate_values_and_tags_(values, tags)
        self._control_parameters_per_view[view_type] = values

    def select_view_type(self, view_type):
        # Convert values into JSON
        values = self._control_parameters_per_view[view_type]
        self._control_parameters = {
            'values': [v.json() for v in values],
        }


###############################################################################

class InputControl(Control):
    """A helper class to define an INPUT."""

    def __init__(self, property_name, message, min_value=None, max_value=None, increment_value=None, percent=False, display_ifs=None, default_value=GetProtobufValue):
        """
        A helper class to define a INPUT. See Control for a description of other arguments.

        Args:
            property_name: see Control
            message: see Control
            default_value: see Control
            min_value (number): the minimum value of the input.
            max_value (number): the maximum value of the input.
            increment_value (number): the increment value when click on the up and down arrows of the control.
            percent (bool): If true, the number will be displayed as percentage in the UI
            display_ifs (list): see Control
        """
        text = min_value is None and max_value is None and increment_value is None and not percent

        if text:
            def check_control_default_fn():
                CHECK_TYPE(default_value, (str,), exclude_types=bool)
                return default_value
        else:
            def check_control_default_fn():
                CHECK_TYPE(default_value, (int, float), exclude_types=bool)
                return default_value

        super().__init__(
            property_name,
            functools.partial(simple_value_parser, key=property_name),
            message,
            ControlType.INPUT,
            default_value,
            check_control_default_fn,
            display_ifs
        )

        if min_value is not None:
            self._control_parameters['min_value'] = min_value
        if max_value is not None:
            self._control_parameters['max_value'] = max_value
        if increment_value is not None:
            self._control_parameters['increment_value'] = increment_value
        self._control_parameters['text'] = text
        self._control_parameters['percent'] = percent


###############################################################################

class ListControl(Control):
    """A helper class to define an INPUT."""

    def __init__(self, property_name, message, form, display_ifs=None, default_value=GetProtobufValue):
        """
        A helper class to define a INPUT. See Control for a description of other arguments.

        Args:
            property_name: see Control
            message: see Control
            display_ifs (list): see Control
            default_value: see Control
        """
        def check_control_default_fn():
            CHECK_LIST(default_value, dict)
            return default_value

        super().__init__(
            property_name,
            functools.partial(simple_value_parser, key=property_name),
            message,
            ControlType.LIST,
            default_value,
            check_control_default_fn,
            display_ifs
        )

        self._form = form
        self._control_parameters['form'] = self._form.json()


###############################################################################

class ToggleControl(Control):
    """A helper class to define an TOGGLE."""

    def __init__(self, property_name, message, tags=None, display_ifs=None, default_value=GetProtobufValue, parser_function=None):
        """
        A helper class to define a TOGGLE. See Control for a description of other arguments.

        Args:
            property_name: see Control
            message: see Control
            default_value: see Control
            tags (tuple): if not None, must be a tuple of length 2 containing two dicts.
                The first (second) dict are the additional tags to set when the toggle is off (on), respectively.
                Each dict must have the same keys as additional_tags.
            display_ifs (list): see Control
            default_value: see Control
            parser_function: see Control
        """
        def check_control_default_fn():
            CHECK_TYPE(default_value, bool)
            return default_value

        if parser_function is None:
            parser_function = functools.partial(simple_value_parser, key=property_name)

        super().__init__(
            property_name,
            parser_function,
            message,
            ControlType.TOGGLE,
            default_value,
            check_control_default_fn,
            display_ifs
        )

        # A toogle declares itself
        self._tags = [self._property_name]
        tags_off = {}
        tags_on = {}
        if tags is not None:
            # Sanity checks
            assert tags is not None
            CHECK_LIST(tags, Tags)
            assert len(tags) == 2
            tags_off, tags_on = tags
            tags_off = tags_off.tags
            tags_on = tags_on.tags
            assert tags_off.keys() == tags_on.keys()

            # Add additional tags to the list of tags
            self._tags += tags_on.keys()
        self._value_to_tag_map = {
            "false": tags_off,
            "true": tags_on
        }


###############################################################################

class SelectOption:
    """A helper class for controls of type SELECT to store the possible values"""

    def __init__(self, value, display_string, display_ifs=None):
        """
        Create a SelectOption instance.

        Args:
            value (str): the computer-friendly value for this option
            display_string (str): the human-friendly string to display
            display_ifs (list): A list of DisplayCondition

        Return:
            A SelectOption instance.
        """
        self._value = CHECK_TYPE(value, str)
        self._display_string = CHECK_TYPE(display_string, str)
        self._display_ifs = CHECK_LIST(display_ifs, DisplayCondition)

    def json(self):
        """
        Convert the object into a Python dict which is JSON-serializable.
        """
        return {
            'value': self._value,
            'display_string': self._display_string,
            'display_if': [d.json() for d in self._display_ifs]
        }

    @property
    def value(self):
        return self._value
