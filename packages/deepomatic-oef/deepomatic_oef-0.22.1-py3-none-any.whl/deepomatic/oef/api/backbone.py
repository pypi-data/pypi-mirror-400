from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict, Callable

import tensorflow as tf

from deepomatic.oef.protos.models.image.backbones_pb2 import Backbone


# -----------------------------------------------------------------------------#

class BackboneInterface(ABC):

    def __init__(self, generic_config: Backbone, config: Any, feature_maps: Optional[List[str]] = None):
        """
        Initialize the backbone.

        Args:
            generic_config: An instance of deepomatic.oef.protos.models.image.backbones_pb2.Backbone.
            config: The specific config of the backbone. Its type depends on the backbone type, it might
                    for exemple be an instance of deepomatic.oef.protos.models.image.backbones_pb2.InceptionBackbone.
            feature_maps: The list of feature_maps to extract. If None is given, assume the only feature
                maps of interest is the last one.
        """
        self._generic_config = generic_config
        self._config = config
        self._feature_maps = feature_maps

        # Get the desired input shape
        image_resizer_config = self._generic_config.input.image_resizer

        image_resizer_type = image_resizer_config.WhichOneof('image_resizer_oneof')
        if image_resizer_type == 'keep_aspect_ratio_resizer':
            ir_config = image_resizer_config.keep_aspect_ratio_resizer
            convert_to_grayscale = ir_config.convert_to_grayscale
            if ir_config.pad_to_max_dimension:
                width = height = ir_config.max_dimension
            else:
                width = height = None
        elif image_resizer_type == 'fixed_shape_resizer':
            ir_config = image_resizer_config.fixed_shape_resizer
            convert_to_grayscale = ir_config.convert_to_grayscale
            width = ir_config.width
            height = ir_config.height
        else:
            raise Exception(f"Unexpected image resizer type: {image_resizer_type}")

        # Input shape in HWC format
        self._input_shape = [
            height,
            width,
            1 if convert_to_grayscale else 3
        ]

    @property
    def input_shape(self) -> List[Optional[int]]:
        return self._input_shape

    def get_feature_maps(self) -> List[str]:
        """
        The list of feature_maps to extract or None. If it is None, we assume the only feature
        maps of interest is the last one.
        """
        return self._feature_maps

    @abstractmethod
    def builder(self,
                feature_maps: Optional[List[str]] = None,
                starting_layer: Optional[str] = None,
                ending_layer: Optional[str] = None) -> Any:
        """
        Build the backbone graph given its inputs.

        Args:
            feature_maps: The list of feature_maps to extract. If None is given, assume the only feature
                maps of interest is the last one.
            starting_layer: If not None, the built backbone will start only strictly after this layer.
            ending_layer: If not None, the built backbone will stop once this layer has been met.

        Return:
            Output is trainer dependent.
        """

    @abstractmethod
    def get_aux_logits(self) -> List[Callable[[Dict[str, tf.Tensor]], tf.Tensor]]:
        """
        Return the list of auxiliary logits tensor functions.
        Each items of the list is function with the following signature:
        logits_tensor = aux_fn(endpoints) with `endpoints` as returned by the builder.
        """

    @abstractmethod
    def get_preprocessor(self) -> tf.keras.layers.Layer:
        """
        Return the default preprocessor to use for this backbone in classification mode.
        Other meta architectures might use another preprocessing.
        """
