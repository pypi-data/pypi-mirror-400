from copy import deepcopy
from deepomatic.oef.configs.utils import dict_inject
from deepomatic.oef.configs.config_utils import ModelConfig

from ..utils import fixed_shape_resizer
from ..backbones import Backbones as bb

backbones = [
    (bb.VGG_11, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.5}}, []),
    (bb.VGG_16, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.005}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.5}}, []),
    (bb.VGG_19, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.0025}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.5}}, []),
    (bb.INCEPTION_V1, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.8}}, []),
    (bb.INCEPTION_V2, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.0025}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.8}}, []),
    (bb.INCEPTION_V3, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.005}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(299, 299)}, 'dropout_keep_prob': 0.8}}, []),
    (bb.INCEPTION_V4, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.005}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(299, 299)}, 'dropout_keep_prob': 0.8}}, []),
    (bb.INCEPTION_RESNET_V2, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.005}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(299, 299)}, 'dropout_keep_prob': 0.8}}, []),
    (bb.RESNET_50_V1, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}, []),  # TODO: try with dropout, ?
    (bb.RESNET_101_V1, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}, []),
    (bb.RESNET_152_V1, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}, []),
    # (bb.RESNET_200_V1, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}, []),
    (bb.RESNET_50_V2, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.025}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}, []),
    (bb.RESNET_101_V2, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}, []),
    (bb.RESNET_152_V2, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.0025}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}, []),
    # (bb.RESNET_200_V2, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}, []),
    (bb.MOBILENET_V1, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.999}}, []),
    (bb.MOBILENET_V1_075, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.999}}, []),
    (bb.MOBILENET_V1_050, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.999}}, []),
    (bb.MOBILENET_V1_025, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.999}}, []),
    (bb.MOBILENET_V2, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}, []),  # TODO: try with dropout, [] ?
    (bb.MOBILENET_V2_140, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 1.}}, []),
    (bb.NASNET_MOBILE, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.5}}, []),
    (bb.NASNET_LARGE, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(331, 331)}, 'dropout_keep_prob': 0.5}}, []),
    (bb.PNASNET_MOBILE, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(224, 224)}, 'dropout_keep_prob': 0.5}}, []),
    (bb.PNASNET_LARGE, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.01}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(331, 331)}, 'dropout_keep_prob': 0.5}}, []),
    (bb.EFFICIENTNET_B0, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.032}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 224, 'width': 224, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.8}}, []),
    (bb.EFFICIENTNET_B1, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.032}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 240, 'width': 240, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.8}}, []),
    (bb.EFFICIENTNET_B2, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.032}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 260, 'width': 260, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.7}}, []),
    (bb.EFFICIENTNET_B3, {'trainer': {'batch_size': 32, 'initial_learning_rate': 0.032}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 300, 'width': 300, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.7}}, []),
    (bb.EFFICIENTNET_B4, {'trainer': {'batch_size': 16, 'initial_learning_rate': 0.016}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 380, 'width': 380, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.6}}, []),
    (bb.EFFICIENTNET_B5, {'trainer': {'batch_size': 8, 'initial_learning_rate': 0.008}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 456, 'width': 456, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.6}}, []),
    (bb.EFFICIENTNET_B6, {'trainer': {'batch_size': 4, 'initial_learning_rate': 0.004}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 528, 'width': 528, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.5}}, []),
    (bb.EFFICIENTNET_B7, {'trainer': {'batch_size': 2, 'initial_learning_rate': 0.002}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 600, 'width': 600, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.5}}, []),
    (bb.EFFICIENTNET_B8, {'trainer': {'batch_size': 1, 'initial_learning_rate': 0.001}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 672, 'width': 672, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.5}}, []),
    (bb.EFFICIENTNET_L2, {'trainer': {'batch_size': 1, 'initial_learning_rate': 0.001}, '@model': {'backbone': {'input.image_resizer': {'fixed_shape_resizer': {'height': 800, 'width': 800, 'resize_method': 'BICUBIC'}}}, 'dropout_keep_prob': 0.5}}, []),
    (bb.DARKNET_53, {'trainer': {'batch_size': 16, 'initial_learning_rate': 0.001}, '@model': {'backbone': {'input.image_resizer': fixed_shape_resizer(256, 256)}, 'dropout_keep_prob': 0.5}}, []),
]


NADAM_OPTIMIZER_LR = {
    bb.INCEPTION_V1.name: 4e-05,
    bb.INCEPTION_V2.name: 1e-05,
    bb.INCEPTION_V3.name: 3e-05,
    bb.INCEPTION_V4.name: 4e-05,
    bb.INCEPTION_RESNET_V2.name: 4e-05,
    bb.RESNET_50_V1.name: 9e-06,
    bb.RESNET_101_V1.name: 5e-06,
    bb.RESNET_152_V1.name: 3e-06,
    bb.RESNET_50_V2.name: 2e-05,
    bb.RESNET_101_V2.name: 2e-05,
    bb.RESNET_152_V2.name: 6e-06,
    bb.EFFICIENTNET_B0.name: 2e-05,
    bb.EFFICIENTNET_B1.name: 2e-05,
    bb.EFFICIENTNET_B2.name: 2e-05,
    bb.EFFICIENTNET_B3.name: 2e-05,
    bb.EFFICIENTNET_B4.name: 2e-05,
    bb.EFFICIENTNET_B5.name: 2e-05,
    bb.EFFICIENTNET_B6.name: 2e-05,
    bb.MOBILENET_V1.name: 1e-05,
    bb.MOBILENET_V1_075.name: 1e-05,
    bb.MOBILENET_V1_050.name: 1e-05,
    bb.MOBILENET_V1_025.name: 1e-05,
    bb.MOBILENET_V2.name: 1.5e-05,
    bb.MOBILENET_V2_140.name: 1.5e-05,
    bb.NASNET_MOBILE.name: 1e-5,
    bb.NASNET_LARGE.name: 1e-5,
    bb.PNASNET_MOBILE.name: 1e-5,
    bb.PNASNET_LARGE.name: 1e-5,
    bb.EFFICIENTNET_B7.name: 2e-5,  # learning rate value not fully benchmarked
    bb.EFFICIENTNET_B8.name: 2e-5,  # learning rate value not fully benchmarked
    bb.EFFICIENTNET_L2.name: 2e-5,  # learning rate value not fully benchmarked
    bb.VGG_11.name: 1e-5,  # learning rate value not fully benchmarked
    bb.VGG_16.name: 1e-5,  # learning rate value not fully benchmarked
    bb.VGG_19.name: 1e-5,  # learning rate value not fully benchmarked
    bb.DARKNET_53.name: 5e-4,  # learning rate value not fully benchmarked
}

ADAM_OPTIMIZER_LR = NADAM_OPTIMIZER_LR
RADAM_OPTIMIZER_LR = NADAM_OPTIMIZER_LR
YOGI_OPTIMIZER_LR = NADAM_OPTIMIZER_LR

MOMENTUM_OPTIMIZER_LR = {
    bb.INCEPTION_V1.name: 0.01,
    bb.INCEPTION_V2.name: 0.0025,
    bb.INCEPTION_V3.name: 0.005,
    bb.INCEPTION_V4.name: 0.005,
    bb.INCEPTION_RESNET_V2.name: 0.005,
    bb.RESNET_50_V1.name: 0.01,
    bb.RESNET_101_V1.name: 0.01,
    bb.RESNET_152_V1.name: 0.01,
    bb.RESNET_50_V2.name: 0.025,
    bb.RESNET_101_V2.name: 0.01,
    bb.RESNET_152_V2.name: 0.0025,
    bb.EFFICIENTNET_B0.name: 0.032,
    bb.EFFICIENTNET_B1.name: 0.032,
    bb.EFFICIENTNET_B2.name: 0.032,
    bb.EFFICIENTNET_B3.name: 0.032,
    bb.EFFICIENTNET_B4.name: 0.016,
    bb.EFFICIENTNET_B5.name: 0.008,
    bb.EFFICIENTNET_B6.name: 0.004,
    bb.MOBILENET_V1.name: 0.01,
    bb.MOBILENET_V1_075.name: 0.01,
    bb.MOBILENET_V1_050.name: 0.01,
    bb.MOBILENET_V1_025.name: 0.01,
    bb.MOBILENET_V2.name: 0.01,
    bb.MOBILENET_V2_140.name: 0.01,
    bb.NASNET_MOBILE.name: 0.01,
    bb.NASNET_LARGE.name: 0.01,
    bb.PNASNET_MOBILE.name: 0.01,
    bb.PNASNET_LARGE.name: 0.01,
    bb.EFFICIENTNET_B7.name: 0.002,
    bb.EFFICIENTNET_B8.name: 0.001,
    bb.EFFICIENTNET_L2.name: 0.001,
    bb.VGG_11.name: 0.01,
    bb.VGG_16.name: 0.005,
    bb.VGG_19.name: 0.0025,
    bb.DARKNET_53.name: 0.001
}

RMS_PROP_OPTIMIZER_LR = MOMENTUM_OPTIMIZER_LR

NADAM_OPTIMIZER_LR_POLICY = {'one_cycle_learning_rate': {}}

ADAM_OPTIMIZER_LR_POLICY = NADAM_OPTIMIZER_LR_POLICY
RADAM_OPTIMIZER_LR_POLICY = NADAM_OPTIMIZER_LR_POLICY
YOGI_OPTIMIZER_LR_POLICY = NADAM_OPTIMIZER_LR_POLICY

MOMENTUM_OPTIMIZER_LR_POLICY = {
    'manual_step_learning_rate': {
        'schedule': [
            {'learning_rate_factor': 0.1, 'step_pct': 0.33},
            {'learning_rate_factor': 0.01, 'step_pct': 0.66},
        ]
    }
}

RMS_PROP_OPTIMIZER_LR_POLICY = MOMENTUM_OPTIMIZER_LR_POLICY

CLASSIF_BACKBONES_DEFEAULT_NADAM = [
    bb.INCEPTION_V1,
    bb.INCEPTION_V2,
    bb.INCEPTION_V3,
    bb.INCEPTION_V4,
    bb.INCEPTION_RESNET_V2,
    bb.RESNET_50_V1,
    bb.RESNET_101_V1,
    bb.RESNET_152_V1,
    bb.RESNET_50_V2,
    bb.RESNET_101_V2,
    bb.RESNET_152_V2,
    bb.EFFICIENTNET_B0,
    bb.EFFICIENTNET_B1,
    bb.EFFICIENTNET_B2,
    bb.EFFICIENTNET_B3,
    bb.EFFICIENTNET_B4,
    bb.EFFICIENTNET_B5,
    bb.EFFICIENTNET_B6,
    bb.MOBILENET_V1,
    bb.MOBILENET_V1_075,
    bb.MOBILENET_V1_050,
    bb.MOBILENET_V1_025,
    bb.MOBILENET_V2,
    bb.MOBILENET_V2_140,
    bb.DARKNET_53
]

CLASSIF_BACKBONES_DEFAULT_MOMENTUM = [
    bb.VGG_11,
    bb.VGG_16,
    bb.VGG_19,
    bb.NASNET_MOBILE,
    bb.NASNET_LARGE,
    bb.PNASNET_MOBILE,
    bb.PNASNET_LARGE,
    bb.EFFICIENTNET_B7,
    bb.EFFICIENTNET_B8,
    bb.EFFICIENTNET_L2,
]


PROBLEMATIC_BACKBONES_CLASSIF = set(CLASSIF_BACKBONES_DEFAULT_MOMENTUM).intersection(set(CLASSIF_BACKBONES_DEFEAULT_NADAM))
assert len(PROBLEMATIC_BACKBONES_CLASSIF) == 0, f'backbones in {[b.name for b in PROBLEMATIC_BACKBONES_CLASSIF]} have 2 values of default optimizer for classification'
TAGGING_BACKBONES_DEFEAULT_NADAM = []

TAGGING_BACKBONES_DEFAULT_MOMENTUM = [
    bb.VGG_11,
    bb.VGG_16,
    bb.VGG_19,
    bb.INCEPTION_V1,
    bb.INCEPTION_V2,
    bb.INCEPTION_V3,
    bb.INCEPTION_V4,
    bb.INCEPTION_RESNET_V2,
    bb.RESNET_50_V1,
    bb.RESNET_101_V1,
    bb.RESNET_152_V1,
    bb.RESNET_50_V2,
    bb.RESNET_101_V2,
    bb.RESNET_152_V2,
    bb.MOBILENET_V1,
    bb.MOBILENET_V1_075,
    bb.MOBILENET_V1_050,
    bb.MOBILENET_V1_025,
    bb.MOBILENET_V2,
    bb.MOBILENET_V2_140,
    bb.NASNET_MOBILE,
    bb.NASNET_LARGE,
    bb.PNASNET_MOBILE,
    bb.PNASNET_LARGE,
    bb.EFFICIENTNET_B0,
    bb.EFFICIENTNET_B1,
    bb.EFFICIENTNET_B2,
    bb.EFFICIENTNET_B3,
    bb.EFFICIENTNET_B4,
    bb.EFFICIENTNET_B5,
    bb.EFFICIENTNET_B6,
    bb.EFFICIENTNET_B7,
    bb.EFFICIENTNET_B8,
    bb.EFFICIENTNET_L2,
    bb.DARKNET_53
]

PROBLEMATIC_BACKBONES_TAGGING = set(TAGGING_BACKBONES_DEFAULT_MOMENTUM).intersection(set(TAGGING_BACKBONES_DEFEAULT_NADAM))
assert len(PROBLEMATIC_BACKBONES_TAGGING) == 0, f'backbones in {[b.name for b in PROBLEMATIC_BACKBONES_TAGGING]} have 2 values of default optimizer for tagging'


# list of different optimizers and their lr per backbone
BACKBONE_LR_OPTIMIZER_LIST = [
    MOMENTUM_OPTIMIZER_LR,
    RMS_PROP_OPTIMIZER_LR,
    NADAM_OPTIMIZER_LR,
    ADAM_OPTIMIZER_LR,
    RADAM_OPTIMIZER_LR,
    YOGI_OPTIMIZER_LR
]

BACKBONE_LR_OPTIMIZER_POLICY_LIST = [
    MOMENTUM_OPTIMIZER_LR_POLICY,
    RMS_PROP_OPTIMIZER_LR_POLICY,
    NADAM_OPTIMIZER_LR_POLICY,
    ADAM_OPTIMIZER_LR_POLICY,
    RADAM_OPTIMIZER_LR_POLICY,
    YOGI_OPTIMIZER_LR_POLICY
]

OPTIMIZERS_LIST = [
    "momentum_optimizer",
    "rms_prop_optimizer",
    "nadam_optimizer",
    "adam_optimizer",
    "rectified_adam_optimizer",
    "yogi_optimizer",
]

for backbone_config in backbones:
    for lr_per_backbone in BACKBONE_LR_OPTIMIZER_LIST:
        assert backbone_config[0].name in lr_per_backbone
    for optimizer, lr_per_backbone, policy in zip(OPTIMIZERS_LIST, BACKBONE_LR_OPTIMIZER_LIST, BACKBONE_LR_OPTIMIZER_POLICY_LIST):
        backbone_config[2].append({
            'field': 'trainer.optimizer.optimizer',
            'triggering_value': optimizer,
            'target_value': {
                'trainer': {
                    'initial_learning_rate': lr_per_backbone[backbone_config[0].name],
                    'learning_rate_policy': policy,
                }
            }
        })

backbones_classification = [(backbone, deepcopy(default_args), deepcopy(switch_args)) for backbone, default_args, switch_args in backbones]
backbones_tagging = [(backbone, deepcopy(default_args), deepcopy(switch_args)) for backbone, default_args, switch_args in backbones]

common_args = {
}

softmax_classifier = ModelConfig(
    display_name="Softmax",
    args=dict_inject(
        common_args, {"@model.loss": {"weighted_softmax": {"logit_scale": 1.0}}}
    ),
    switch_args=[],)

sigmoid_classifier = ModelConfig(
    display_name="Sigmoid",
    args=dict_inject(
        common_args,
        {"@model.loss": {"weighted_sigmoid": {}}},
    ),
)

iteration_list = [(backbones_classification, CLASSIF_BACKBONES_DEFEAULT_NADAM, CLASSIF_BACKBONES_DEFAULT_MOMENTUM, softmax_classifier),
                  (backbones_tagging, TAGGING_BACKBONES_DEFEAULT_NADAM, TAGGING_BACKBONES_DEFAULT_MOMENTUM, sigmoid_classifier)]


for task_backbones, task_backbones_default_nadam, task_backbones_default_momentum, task_classifier in iteration_list:
    for backbone, default_args, switch_args in task_backbones:
        # assert that a backbone is at least present in one of the lists of default values
        assert backbone in task_backbones_default_nadam + task_backbones_default_momentum

        for DEFAULT, LR, POLICY, OPTIMIZER in [
            (task_backbones_default_nadam, NADAM_OPTIMIZER_LR, NADAM_OPTIMIZER_LR_POLICY, 'nadam_optimizer'),
            (task_backbones_default_momentum, MOMENTUM_OPTIMIZER_LR, MOMENTUM_OPTIMIZER_LR_POLICY, 'momentum_optimizer'),
        ]:
            if backbone in DEFAULT:
                default_args['trainer']['initial_learning_rate'] = LR[backbone.name]
                default_args['trainer']['learning_rate_policy'] = POLICY
                default_args['trainer']['optimizer'] = {OPTIMIZER: {}}

        task_classifier.add_backbone(backbone, args=default_args, switch_args=switch_args)

configs = [softmax_classifier, sigmoid_classifier]
