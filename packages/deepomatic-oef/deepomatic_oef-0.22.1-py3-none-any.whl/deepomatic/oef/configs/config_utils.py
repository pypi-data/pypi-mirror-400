import copy
from enum import Enum

from .utils import dict_inject


###############################################################################

def make_alias(name):
    """Encode a human readable name into a model key"""
    return name.replace('%', '').replace(' ', '_').replace('-', '_').lower()


###############################################################################

def update_switch_args(switch_args, new_switch_args):
    updated_switch_args = copy.deepcopy(switch_args)
    for args in new_switch_args:
        for existing_switch in updated_switch_args:
            if existing_switch['field'] == args['field'] and existing_switch['triggering_value'] == args['triggering_value']:
                existing_switch['target_value'] = dict_inject(existing_switch['target_value'], args['target_value'])
                break
        else:
            updated_switch_args.append(copy.deepcopy(args))
    return updated_switch_args


class ModelVariant:

    def __init__(self, display_name, alias, args, switch_args, pretrained_parameters):
        """
        Configuration class for a backbone.

        Args:
            display_name (string): The name to display for humans.
            alias (string): A key used to refer to this model when generating model_list.py.
            args (dict): A dict passed the protobuf for initialization.
            switch_args (list[dict]): A list of dictionaries used to switch default values of
                            some experiment parameters based on fields to watch and specific triggering values.
                            Each dictionnary should look like this:
                            {
                                "field": "trainer.optimizer.optimizer",
                                "triggering_value": "nadam_optimizer",
                                "target_value": {
                                    "trainer": {
                                        "initial_learning_rate": 2e-5,
                                        "learning_rate_policy": {"one_cycle_learning_rate": {}},
                                    }
                                },
                            },
                            field: field optimizer to be watched
                            triggering value: if trigering value is found in field optimizer, the value
                            of target value is to be later injected in the experiment

            pretrained_parameters (dict): A dict DataType -> "path/to/pretrained.tar.gz" or None
        """
        self._display_name = display_name
        self._args = args
        self._switch_args = switch_args
        self._pretrained_parameters = pretrained_parameters if pretrained_parameters is not None else {}
        self._alias = make_alias(display_name) if alias is None else alias

    @property
    def display_name(self):
        return self._display_name

    @property
    def alias(self):
        return self._alias

    @property
    def args(self):
        return self._args

    @property
    def switch_args(self):
        return self._switch_args

    @property
    def pretrained_parameters(self):
        return self._pretrained_parameters

    def update(self, args=None, switch_args=[], pretrained_parameters=None):
        """
        Similar to the behavior of dict.update for args and pretrained_parameters.
        Returns an updated copy of the object instead of modifying it inplace.

        Args:
            args (dict): If not None: the new `args` will be injected into backbone.args using dict_inject.
            switch_args (list[dict]): new switch args to be appended to the existing switch_args
            pretrained_parameters (dict): If not None, the default backbone.pretrained_parameters will be
                                          updated with that dict.

        Return:
            An updated copy of self.
        """
        if args is None:
            args = copy.deepcopy(self._args)
        else:
            args = dict_inject(self._args, args)

        updated_switch_args = update_switch_args(self._switch_args, switch_args)

        pretrained = copy.deepcopy(self._pretrained_parameters)
        if pretrained_parameters is not None:
            pretrained.update(pretrained_parameters)

        return ModelVariant(display_name=self._display_name, alias=self._alias, args=args, switch_args=updated_switch_args, pretrained_parameters=pretrained)


###############################################################################

class DataType(Enum):
    NATURAL_RGB = 'natural_rgb'


class BackboneConfig(ModelVariant):

    def __init__(self, display_name, args, switch_args=[], pretrained_parameters=None, alias=None):
        """
        Configuration class for a backbone.

        Args:
            display_name: see ModelVariant for the detail
            args: see ModelVariant for the detail
            switch_args: see ModelVariant for the detail
            pretrained_parameters: see ModelVariant for the detail
            alias: see ModelVariant for the detail
        """
        if alias is None:
            alias = make_alias(display_name)

        # Args passed when building a backbone are relative to @model.backbone
        args = {'@model.backbone': args}

        super().__init__(display_name=display_name, alias=alias, args=args, switch_args=switch_args, pretrained_parameters=pretrained_parameters)


###############################################################################

class ModelConfig:

    def __init__(self, display_name, args, switch_args=[], meta_arch=None, alias=None):
        """
        Configuration class for a backbone.

        Args:
            display_name (string): The name to display for humans
            args (dict): A dict passed to Backbone protobuf for its initialization
            switch_args (list[dict]): used to switch some default args based on some triggering values
                                      of specific fields
            backbones (list): A list of BackboneConfig
            meta_arch (string): Protobuf meta_arch to use when using '@meta_arch' in args.
            alias (string): A key used to refer to this backbone when generating model_list.py. If None,
                            an alias is inferred from the display_name.
        """
        self._display_name = display_name
        self._args = args
        self._switch_args = switch_args
        self._meta_arch = meta_arch

        if alias is None:
            alias = make_alias(display_name)
        self._alias = alias

        self._variants = []
        self._variants_keys = set()

    @property
    def display_name(self):
        return self._display_name

    @property
    def variants(self):
        return self._variants

    @property
    def meta_arch(self):
        return self._meta_arch

    def add_backbone(self, backbone, model_display_name=None, model_aliases=None, args=None, switch_args=[], pretrained_parameters=None, skip_existing_aliases=False):
        """
        Add a backbone to this model.

        Args:
            backbone (Backbones enum key): A backbone enum.
            model_display_name (str): If not None, it will override the default display name made of the
                                      concatenation of model and backbone display names.
            model_aliases (list): If not None, it will override the default alias made of the
                                      concatenation of model and backbone aliases.
            args: See BackboneConfig.update.
            switch_args(list[dict]): See BackboneConfig.update.
            pretrained_parameters: See BackboneConfig.update.
            skip_existing_aliases (bool): If True, if will ignore already inserted models, otherwise it will
                                          raise an error in case of duplicate.
        """
        backbone = backbone.value
        variant = backbone.update(args=args, switch_args=switch_args, pretrained_parameters=pretrained_parameters)

        if model_display_name is None:
            model_display_name = '{} - {}'.format(self._display_name, backbone.display_name)
        if model_aliases is None:
            model_aliases = ['{}.{}'.format(self._alias, backbone.alias)]

        for alias in model_aliases:
            if alias in self._variants_keys:
                if skip_existing_aliases:
                    continue
                else:
                    raise Exception("Duplicate alias: {}".format(alias))
            self._variants_keys.add(alias)
            self._variants.append(ModelVariant(
                display_name=model_display_name,
                alias=alias,
                args=dict_inject(self._args, variant.args),
                switch_args=update_switch_args(self._switch_args, switch_args),
                pretrained_parameters=variant.pretrained_parameters
            ))
