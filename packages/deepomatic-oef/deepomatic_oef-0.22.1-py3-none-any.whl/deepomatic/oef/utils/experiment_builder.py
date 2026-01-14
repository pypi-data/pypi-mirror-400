import copy
import logging
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.message import Message
import google.protobuf.json_format as json_format

from deepomatic.oef.configs import model_list
from deepomatic.oef.configs.utils import dict_inject
from deepomatic.oef.utils.common import parse_protobuf_from_json_or_binary, convert_to_dict
from deepomatic.oef.utils.class_helpers import load_proto_class_from_protobuf_descriptor
from deepomatic.oef.protos.experiment_pb2 import Experiment
from deepomatic.oef.protos.hyperparameter_pb2 import field_option, oneof_option, HyperParameter

logger = logging.getLogger(__name__)


class InvalidNet(Exception):
    pass


class ExperimentBuilder(object):
    """
    This class can build a Experiment protobuf given the pre-determined parameters. You can also pass
    additionnal parameters to override the default arguments. In that purpose, all fields of Model and its
    sub-messages are assumed to have a different name (this assumpition is checked by model_generator).
    """

    _model_list = None

    def __init__(self, model_type_key):
        if self._model_list is None:
            self.load_model_list()
        if model_type_key not in self._model_list:
            # Try model_type_key reordering to provide backward compatibility with oef<0.5.0
            model_type_key_parts = model_type_key.split('.')
            model_type_key_new_format = '.'.join([model_type_key_parts[0], model_type_key_parts[-1]] + model_type_key_parts[1:-1])
            if model_type_key_new_format in self._model_list:
                logger.warning("This model key format is deprecated: '{}'. Use '{}' instead.".format(model_type_key, model_type_key_new_format))
                model_type_key = model_type_key_new_format
            else:
                raise InvalidNet("Unknown model key '{}'. Also tried '{}' for backward compatibility.".format(model_type_key, model_type_key_new_format))
        self._model_args = self._model_list[model_type_key]
        self._hyperparameters = {}

    @classmethod
    def load_model_list(cls):
        # Avoid to load it at the root of the module to avoid nested import loops
        cls._model_list = {}
        for key, args in model_list.model_list.items():
            assert key not in cls._model_list, "Duplicate model key, this should not happen"
            cls._model_list[key] = args

    def add_hyperparameter(self, hyperparameter, distribution=None):
        """
        Add a hyperparameter to the experiment.

        Args:
            hyperparameter (string): path to hyperparameter in the protobuf hierarchy seperated by a '.' (e.g., 'trainer.batch_size')
            distribution (dict, Message, JSON, binary): Hyperparameter distribution
        """
        def convert_to_protobuf(value):
            """
            Convert a dict / JSON / binary to protobuf Message
            """
            if isinstance(value, dict):
                value = json_format.ParseDict(value, HyperParameter())
            elif isinstance(value, Message):
                pass
            else:
                value = parse_protobuf_from_json_or_binary(HyperParameter, value)
            return value

        if hyperparameter in ['trainer.num_train_steps', 'trainer.num_train_epochs']:
            raise Exception(f'`{hyperparameter}` is not available for hyperparameter optimization')

        if distribution is None:
            distribution = self._get_default_distribution_(Experiment, hyperparameter)
        else:
            self._recursive_search_(Experiment, hyperparameter)

        self._hyperparameters[hyperparameter] = convert_to_protobuf(distribution)

    @staticmethod
    def _get_default_distribution_(protobuf_class, hyperparameter):
        """
        Recursively find and fill default distribution for hyperparameter

        Args:
            protobuf_class (protobuf): parent protobuf class from which to start recursively the finding procedure
            hyperparameter (string): path to hyperparameter in the protobuf hierarchy seperated by a '.' (e.g., 'trainer.batch_size')
        """

        # Get field and protobuf class for the given hyperparameter
        protobuf_class, field_name = ExperimentBuilder._recursive_search_(protobuf_class, hyperparameter)

        # If the field_name is None, it is an OneOf
        if field_name is None:
            oneofs = protobuf_class.DESCRIPTOR.oneofs
            assert len(oneofs) == 1, f'Number of OneOfs should be 1, found {len(oneofs)}. This should not happen.'
            oneof = oneofs[0]
            if not oneof.has_options:
                raise Exception('No distribution given for hyperparemeter {}'.format(oneof.name))
            return oneof.GetOptions().Extensions[oneof_option]
        else:
            field = protobuf_class.DESCRIPTOR.fields_by_name[field_name]
            if field.message_type is None or field.label == FieldDescriptor.LABEL_REPEATED:
                if not field.has_options:
                    raise Exception('No distribution given for hyperparemeter {}'.format(field_name))
                return field.GetOptions().Extensions[field_option]

    @staticmethod
    def _recursive_search_(protobuf_class, path_name):
        """
        Check if path_name is correct by checking recursively fields of the input protobuf_class

        Args:
            protobuf_class (protobuf): parent protobuf class from which to start recursively the finding procedure
            hyperparameter (string): path to hyperparameter in the protobuf hierarchy seperated by a '.' (e.g., 'trainer.batch_size')

        Returns:
            protobuf, field_name tuple. field_name is None for OneOf
        """
        fields = path_name.split('.')

        field_name = fields[0]

        # Check if the field exists
        if field_name not in protobuf_class.DESCRIPTOR.fields_by_name:
            raise ValueError(f"'{field_name}' field not found in protobuf message '{protobuf_class.DESCRIPTOR.name}'")

        # If it is a nested message or Oneof field
        field_message_type = protobuf_class.DESCRIPTOR.fields_by_name[field_name].message_type
        if field_message_type is not None:
            field_message_class = load_proto_class_from_protobuf_descriptor(field_message_type)
            # It's a nested message, go deeper
            if 1 < len(fields):
                return ExperimentBuilder._recursive_search_(field_message_class, '.'.join(fields[1:]))
            # It's a Oneof
            return field_message_class, None
        # It's a scalar or repeated field
        else:
            return protobuf_class, field_name

    def build(self, **kwargs):

        args_from_switch_activations = self._recursive_switch_activation_(
            protobuf_class=Experiment,
            default_args=self._model_args.default_args,
            kwargs=copy.deepcopy(kwargs),
            switch_args=self.accumulate_switch_args(self._model_args.switch_args)
        )
        all_args = set([*self._model_args.default_args] + [*kwargs])
        used_args = set()

        xp = self._recursive_build_(Experiment, self._model_args.default_args, args_from_switch_activations, copy.deepcopy(kwargs), used_args, self._hyperparameters)
        unused_args = all_args - used_args
        if len(unused_args) > 0:
            raise Exception('Unused keyword argument: {}'.format(', '.join(unused_args)))
        unused_hyperparameters = [k for k, v in self._hyperparameters.items() if v is None]
        if len(unused_hyperparameters) > 0:
            raise Exception('hyperparameter not found: {}'.format(', '.join(unused_hyperparameters)))
        for k, v in self._hyperparameters.items():
            xp.hyperparameters[k].CopyFrom(v)
        return xp

    @staticmethod
    def accumulate_switch_args(switch_args):
        """Accumulate switch args.

        Args:
            switch_args (list[dict]): has the form
                [{
                    "field": "trainer.optimizer.optimizer",
                    "triggering_value": "nadam_optimizer",
                    "target_value": {
                        "trainer": {
                            "initial_learning_rate": 2e-5,
                            "learning_rate_policy": {"one_cycle_learning_rate": {}},
                        }
                    },
                },
                {
                    "field": "trainer.optimizer.optimizer",
                    "triggering_value": "momentum_optimizer",
                    "target_value": {
                        "trainer": {
                            "initial_learning_rate": 2e-3,
                            "learning_rate_policy": {"constant_learning_rate": {}},
                        }
                    },
                }]

        Returns:
            The accumulated switch args under the form:
            {
                "trainer": {
                    "optimizer": {
                        "optimizer": {
                            "nadam_optimizer": {
                                "initial_learning_rate": 2e-5,
                                "learning_rate_policy": {"one_cycle_learning_rate": {}},
                            },
                            "momentum_optimizer": {
                                "initial_learning_rate": 2e-3,
                                "learning_rate_policy": {"constant_learning_rate": {}},
                            }
                        }
                    }
                }
            }
        """
        accumulated_switch_args = {}
        for switch in switch_args:
            accumulated_switch_args = dict_inject(accumulated_switch_args, {
                switch['field']: {
                    switch['triggering_value']: switch['target_value']
                }
            })
        return accumulated_switch_args

    @staticmethod
    def _recursive_switch_activation_(protobuf_class, default_args, switch_args, kwargs):
        """The goal of this method is to return the parameters that are a result of activated switch arguments
        Args:
            protobuf_class : Protobuf class of an object on which we want to check of there are any activated values
            default_args (dict): default arguments that are used for the specific object that is defined by the protobuf_class
            kwargs (dict): arguments that are injected by the called of this method, in general requested through the api by the user
            switch_args (dict): Switch args should have been accumulated by `accumulate_switch_args` and have the form:
                {
                    "trainer": {
                        "optimizer": {
                            "optimizer": {
                                "nadam_optimizer": {
                                    "initial_learning_rate": 2e-5,
                                    "learning_rate_policy": {"one_cycle_learning_rate": {}},
                                },
                                "momentum_optimizer": {
                                    "initial_learning_rate": 2e-3,
                                    "learning_rate_policy": {"constant_learning_rate": {}},
                                }
                            }
                        }
                    }
                }
        """
        kwargs = convert_to_dict(kwargs)
        selected_args = {}

        # The oneof has fields which are also present in the protobuf fields.
        # We can hence identify the oneof fields which should be skipped, by removing the selected oneof field.
        # We identify the selected oneof field by its presence in the kwargs or default_args parameters, where kwargs has the higher priority
        skipped_fields = []
        for oneof in protobuf_class.DESCRIPTOR.oneofs:
            fields = [field.name for field in oneof.fields]
            # Identify selected one of fields
            intersection_of_oneof_fields_and_user_args = set(fields) & set(kwargs.keys())
            if len(intersection_of_oneof_fields_and_user_args) > 0:
                selected = intersection_of_oneof_fields_and_user_args
            else:
                intersection_of_oneof_fields_and_default_args = set(fields) & set(default_args.keys())
                selected = intersection_of_oneof_fields_and_default_args
            # We cannot have more than 1 selected oneof field.
            assert len(selected) <= 1, "Two or more values are given for the one-of '{}' (error when processing '{}'): {}".format(oneof.name, protobuf_class.DESCRIPTOR.name, selected)
            # The skipped fields are all the fields of the one-of but the one which is selected
            skipped_fields += list(set(fields) - selected)
            selected = list(selected)
            if oneof.name in switch_args and selected[0] in switch_args[oneof.name]:
                selected_args = dict_inject(selected_args, switch_args[oneof.name][selected[0]])

        for field in protobuf_class.DESCRIPTOR.fields:
            # Skip fields which are unselected oneof fields
            if field.name in skipped_fields:
                continue

            if (field.message_type is not None) and (field.label != FieldDescriptor.LABEL_REPEATED):

                # gather the kwargs (arguments from the user) to be used in the recursion
                sub_kwargs = {}
                if field.name in kwargs:
                    sub_kwargs = convert_to_dict(kwargs.pop(field.name))
                # we add kwargs aggain to the sub_kwargs because we want to keep all user key arguments and resolve them in the recursion
                sub_kwargs.update(kwargs)

                # gather the default arguments that will be used in the recursion
                sub_default_args = {}
                if field.name in default_args:
                    sub_default_args = default_args[field.name]

                # gather switch arguments that will be used in the recursion
                sub_switch_args = {}
                if field.name in switch_args:
                    sub_switch_args = switch_args[field.name]
                # If the field is required, we build it
                # --> then we build the message
                # This fields is a protobuf message, we build it recursively
                field_message_class = load_proto_class_from_protobuf_descriptor(field.message_type)
                sub_selected_args = ExperimentBuilder._recursive_switch_activation_(field_message_class, sub_default_args, sub_switch_args, sub_kwargs)
                selected_args = dict_inject(selected_args, sub_selected_args)
        return selected_args

    @staticmethod
    def _recursive_build_(protobuf_class, default_args, selected_switch_args, kwargs, used_args, hyperparameters):
        """builds recusively an object using the protobuf_class, default arguments, selected_arguments that are the ouptut of _recusive_switch_activation
        kwargs, that are the user arguments

        Args:
            protobuf_class : Protobuf class of an object on which we want to check of there are any activated values
            default_args (dict): default arguments that are used for the specific object that is defined by the protobuf_class
            kwargs (dict): arguments that are injected by the called of this method, in general requested through the api by the user
            switch_args (list[dict]): A list of dictionaries used to switch default values of
                            some experiment parameters based on fields to watch and specific triggering values
                            , each dictionnary with 3 keys:
                                    example
                            {
                                "field": "optimizer",
                                "triggering_value": "nadam_optimizer",
                                "target_value": {
                                    "trainer": {
                                        "initial_learning_rate": 2e-5,
                                        "learning_rate_policy": {"one_cycle_learning_rate": {}},
                                    }
                                },
                            },
                            field: field optimizer to be watched
                            triggering value: if triggering value is found in field optimizer, the value
                            of target value is to be later injected in the experiment
            used_args (list): an accumulator used in the recursion to make sure that all arguments have been used
            hyperparameters (dict): parameter for a specific case where the research of parameter is used
        """

        def check_valid_hp_value(field):
            """
            Check if given kwarg is in the hyperparameter distribution
            """
            # check that the field value is in the defined hyperparameter distribution range
            if field.name in hp_to_field_name:
                value = kwargs[field.name]
                # Check if it is a OneOf and take the only value
                if field.message_type is not None:
                    entries = kwargs[field.name].keys()
                    assert len(entries) == 1, f'{entries} should be of lenght one for field {field.name}'
                    value = list(entries)[0]
                hp = hyperparameters[hp_to_field_name[field.name]]
                distribution_type = hp.WhichOneof('distribution')
                if distribution_type == 'categorical':
                    values = [getattr(v, v.WhichOneof('value')) for v in hp.categorical.values]
                    assert value in values, f'{value} not in the given hyperparameter categorical distribution ({values})'
                else:
                    distribution = getattr(hp, distribution_type)
                    min = 1
                    max = -1
                    if distribution_type in ['uniform', 'log_uniform']:
                        min = distribution.min
                        max = distribution.max
                    elif distribution_type == 'normal':
                        min = distribution.mu - 5 * distribution.sigma
                        max = distribution.mu + 5 * distribution.sigma
                    assert min <= kwargs[field.name] <= max, f'{kwargs[field.name]} not in the given hyperparameter {distribution_type} distribution ({min}, {max})'

        real_args = {}
        default_args = convert_to_dict(default_args)
        # Check if there are not part of the protobuf descriptor, if it is the case then there is an exception that is raised
        unused_default_args = default_args.keys() - set([f.name for f in protobuf_class.DESCRIPTOR.fields])
        if len(unused_default_args) > 0:
            raise Exception('Unexpected default keyword argument: {}'.format(', '.join(unused_default_args)))

        hp_to_field_name = {k.split('.')[-1]: k for k in hyperparameters.keys()}

        # The oneof has fields which are also present in the protobuf fields.
        # We can hence identify the oneof fields which should be skipped, by removing the selected oneof field.
        # We identify the selected oneof field by its presence in the kwargs or default_args parameters, where kwargs has the higher priority
        skipped_fields = []
        for oneof in protobuf_class.DESCRIPTOR.oneofs:
            fields = [field.name for field in oneof.fields]
            # Identify selected one of fields
            intersection_of_oneof_fields_and_user_args = set(fields) & set(kwargs.keys())
            intersection_of_oneof_fields_and_selected_switch_args = set(fields) & set(selected_switch_args.keys())
            intersection_of_oneof_fields_and_default_args = set(fields) & set(default_args.keys())
            if len(intersection_of_oneof_fields_and_user_args) > 0:
                selected = intersection_of_oneof_fields_and_user_args
            elif len(intersection_of_oneof_fields_and_selected_switch_args) > 0:
                selected = intersection_of_oneof_fields_and_selected_switch_args
            else:
                selected = intersection_of_oneof_fields_and_default_args
            # We cannot have more than 1 selected oneof field.
            assert len(selected) <= 1, "Two or more values are given for the one-of '{}' (error when processing '{}'): {}".format(oneof.name, protobuf_class.DESCRIPTOR.name, selected)
            # The skipped fields are all the fields of the one-of but the one which is selected
            skipped_fields += set(fields) - selected

        for field in protobuf_class.DESCRIPTOR.fields:
            # Skip fields which are unselected oneof fields
            if field.name in skipped_fields:
                continue

            # If the field is a scalar or a list ...
            if field.message_type is None or field.label == FieldDescriptor.LABEL_REPEATED:

                # ... there is only one possible value and kwargs has higher priority
                if field.name in kwargs:
                    check_valid_hp_value(field)
                    real_args[field.name] = kwargs.pop(field.name)
                elif field.name in selected_switch_args:
                    real_args[field.name] = selected_switch_args[field.name]
                elif field.name in default_args:
                    real_args[field.name] = default_args[field.name]

            else:
                # If the field is required, we build it
                # --> then we build the message
                used = False

                # gather the kwargs (arguments from the user) to be used in the recursion
                sub_kwargs = {}
                if field.name in kwargs:
                    check_valid_hp_value(field)
                    sub_kwargs = convert_to_dict(kwargs.pop(field.name))
                    used = True
                # we add kwargs again to the sub_kwargs because we want to keep all user key arguments and resolve them in the recursion
                sub_kwargs.update(kwargs)

                # gather the default arguments that will be used in the recursion
                sub_default_args = {}
                if field.name in default_args:
                    sub_default_args = default_args[field.name]
                    used = True

                # gather switch arguments that will be used in the recursion
                sub_selected_switch_args = {}
                if field.name in selected_switch_args:
                    sub_selected_switch_args = selected_switch_args[field.name]
                    used = True

                # This fields is a protobuf message, we build it recursively
                field_message_class = load_proto_class_from_protobuf_descriptor(field.message_type)

                exp_builder = ExperimentBuilder._recursive_build_(field_message_class, sub_default_args, sub_selected_switch_args, copy.deepcopy(sub_kwargs), used_args, hyperparameters)
                if used or field.label == FieldDescriptor.LABEL_REQUIRED:
                    real_args[field.name] = exp_builder

        used_args.update([*real_args])
        return protobuf_class(**real_args)
